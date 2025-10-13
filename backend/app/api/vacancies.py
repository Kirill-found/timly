"""
API endpoints для работы с вакансиями
Получение списка вакансий и откликов с mock данными
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.schemas.base import APIResponse
from app.schemas.hh import HHVacancyFull, HHApplication
from app.schemas.auth import UserProfile
from app.services.auth_service import AuthService
from app.services.hh_client import HHClient
from app.services.encryption import TokenEncryption
from app.utils.exceptions import AuthenticationError, HHIntegrationError
from app.utils.response import success, created, bad_request, unauthorized, not_found, internal_error

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# Dependency для получения текущего пользователя (копируем из auth.py)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    Получение текущего аутентифицированного пользователя
    Используется во всех защищенных endpoints
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": "Invalid authentication credentials"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTHENTICATION_ERROR",
                "message": str(e)
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency для получения HH.ru клиента с токеном пользователя
async def get_hh_client(
    user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> HHClient:
    """
    Создание HH.ru клиента с расшифрованным токеном пользователя
    """
    try:
        # Проверяем что у пользователя есть HH токен
        if not user.encrypted_hh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "NO_HH_TOKEN",
                    "message": "У пользователя не настроена интеграция с HH.ru"
                }
            )

        # Расшифровываем токен
        encryption = TokenEncryption()
        hh_token = encryption.decrypt(user.encrypted_hh_token)

        # Создаем HH клиент
        hh_client = HHClient(token=hh_token)

        return hh_client

    except Exception as e:
        logger.error(f"Ошибка создания HH клиента для пользователя {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "HH_CLIENT_ERROR",
                "message": f"Не удалось подключиться к HH.ru: {str(e)}"
            }
        )


@router.get("/", response_model=APIResponse)
async def get_vacancies(
    page: int = Query(0, ge=0, description="Номер страницы (начиная с 0)"),
    per_page: int = Query(20, ge=1, le=100, description="Количество вакансий на странице"),
    hh_client: HHClient = Depends(get_hh_client)
):
    """
    Получение списка вакансий пользователя

    Args:
        page: Номер страницы для пагинации
        per_page: Количество вакансий на странице

    Returns:
        APIResponse: Список вакансий с пагинацией в стандартном формате API
    """
    try:
        logger.info(f"Получение вакансий: страница {page}, по {per_page} на странице")

        # Получаем вакансии через HH клиент (mock или реальный API)
        vacancies_data = await hh_client.get_vacancies(page=page, per_page=per_page)

        # Преобразуем каждую вакансию в нужный формат
        vacancy_items = []
        for vacancy in vacancies_data.get("items", []):
            vacancy_item = {
                "id": vacancy.get("id"),
                "hh_vacancy_id": vacancy.get("id"),
                "title": vacancy.get("name", ""),
                "description": vacancy.get("description", "")[:500] + "..." if len(vacancy.get("description", "")) > 500 else vacancy.get("description", ""),

                # Навыки
                "key_skills": [skill.get("name", "") for skill in vacancy.get("key_skills", [])],

                # Зарплата
                "salary_from": vacancy.get("salary", {}).get("from") if vacancy.get("salary") else None,
                "salary_to": vacancy.get("salary", {}).get("to") if vacancy.get("salary") else None,
                "currency": vacancy.get("salary", {}).get("currency", "RUR") if vacancy.get("salary") else "RUR",

                # Параметры
                "experience": vacancy.get("experience", {}).get("id") if vacancy.get("experience") else None,
                "employment": vacancy.get("employment", {}).get("id") if vacancy.get("employment") else None,
                "schedule": vacancy.get("schedule", {}).get("id") if vacancy.get("schedule") else None,
                "area": vacancy.get("area", {}).get("name") if vacancy.get("area") else None,

                # Статистика
                "applications_count": vacancy.get("counters", {}).get("responses", 0),
                "new_applications_count": vacancy.get("counters", {}).get("unread_responses", 0),
                "is_active": not vacancy.get("archived", False),

                # Даты
                "published_at": vacancy.get("published_at"),
                "created_at": vacancy.get("created_at"),

                # Дополнительные поля
                "url": vacancy.get("alternate_url"),
                "employer": {
                    "name": vacancy.get("employer", {}).get("name", ""),
                    "url": vacancy.get("employer", {}).get("alternate_url", "")
                }
            }
            vacancy_items.append(vacancy_item)

        response_data = {
            "items": vacancy_items,
            "pagination": {
                "page": vacancies_data.get("page", page),
                "pages": vacancies_data.get("pages", 0),
                "per_page": vacancies_data.get("per_page", per_page),
                "total": vacancies_data.get("found", 0)
            },
            "meta": {
                "source": "mock" if hh_client.is_mock_mode else "hh_api"
            }
        }

        logger.info(f"Успешно получено {len(vacancy_items)} вакансий")
        return success(data=response_data)

    except HHIntegrationError as e:
        logger.error(f"Ошибка интеграции с HH.ru: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "HH_INTEGRATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении вакансий: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        )
    finally:
        # Закрываем HH клиент
        await hh_client.close()


@router.get("/{vacancy_id}/applications", response_model=APIResponse)
async def get_vacancy_applications(
    vacancy_id: str,
    page: int = Query(0, ge=0, description="Номер страницы (начиная с 0)"),
    per_page: int = Query(20, ge=1, le=100, description="Количество откликов на странице"),
    hh_client: HHClient = Depends(get_hh_client)
):
    """
    Получение откликов на вакансию

    Args:
        vacancy_id: ID вакансии в HH.ru
        page: Номер страницы для пагинации
        per_page: Количество откликов на странице

    Returns:
        APIResponse: Список откликов с пагинацией в стандартном формате API
    """
    try:
        logger.info(f"Получение откликов для вакансии {vacancy_id}: страница {page}, по {per_page} на странице")

        # Получаем отклики через HH клиент
        applications_data = await hh_client.get_applications(
            vacancy_id=vacancy_id,
            page=page,
            per_page=per_page
        )

        # Преобразуем каждый отклик в нужный формат
        application_items = []
        for application in applications_data.get("items", []):
            resume = application.get("resume", {})

            # Извлекаем контактные данные
            contacts = resume.get("contact", [])
            email = None
            phone = None

            for contact in contacts:
                contact_type = contact.get("type", {}).get("id", "")
                if contact_type == "email":
                    email = contact.get("value", "")
                elif contact_type == "cell":
                    phone_data = contact.get("value", {})
                    if isinstance(phone_data, dict):
                        phone = phone_data.get("formatted", "")
                    else:
                        phone = str(phone_data)

            application_item = {
                "id": application.get("id"),
                "vacancy_id": vacancy_id,
                "hh_application_id": application.get("id"),
                "hh_resume_id": resume.get("id"),

                # Данные кандидата
                "candidate_name": f"{resume.get('first_name', '')} {resume.get('last_name', '')}".strip(),
                "candidate_email": email,
                "candidate_phone": phone,
                "resume_url": resume.get("alternate_url"),

                # Информация о резюме
                "resume_title": resume.get("title", ""),
                "candidate_age": resume.get("age"),
                "candidate_area": resume.get("area", {}).get("name") if resume.get("area") else None,
                "experience_months": resume.get("total_experience", {}).get("months") if resume.get("total_experience") else None,

                # Зарплатные ожидания
                "expected_salary": {
                    "amount": resume.get("salary", {}).get("amount") if resume.get("salary") else None,
                    "currency": resume.get("salary", {}).get("currency", "RUR") if resume.get("salary") else "RUR"
                },

                # Навыки
                "skills": resume.get("skill_set", []),

                # Статус
                "is_duplicate": False,  # TODO: реализовать дедупликацию
                "analyzed_at": None,    # TODO: связать с анализом

                # Даты
                "created_at": application.get("created_at"),
                "updated_at": application.get("updated_at"),

                # Дополнительные поля
                "state": application.get("state", {}).get("name", ""),
                "has_updates": application.get("has_updates", False),
                "viewed_by_opponent": application.get("viewed_by_opponent", True)
            }
            application_items.append(application_item)

        response_data = {
            "vacancy_id": vacancy_id,
            "items": application_items,
            "pagination": {
                "page": applications_data.get("page", page),
                "pages": applications_data.get("pages", 0),
                "per_page": applications_data.get("per_page", per_page),
                "total": applications_data.get("found", 0)
            },
            "meta": {
                "source": "mock" if hh_client.is_mock_mode else "hh_api"
            }
        }

        logger.info(f"Успешно получено {len(application_items)} откликов для вакансии {vacancy_id}")
        return success(data=response_data)

    except HHIntegrationError as e:
        logger.error(f"Ошибка интеграции с HH.ru: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "HH_INTEGRATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении откликов для вакансии {vacancy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        )
    finally:
        # Закрываем HH клиент
        await hh_client.close()


@router.get("/{vacancy_id}", response_model=APIResponse)
async def get_vacancy_details(
    vacancy_id: str,
    hh_client: HHClient = Depends(get_hh_client)
):
    """
    Получение детальной информации о вакансии

    Args:
        vacancy_id: ID вакансии в HH.ru

    Returns:
        APIResponse: Детальная информация о вакансии
    """
    try:
        logger.info(f"Получение деталей вакансии {vacancy_id}")

        # Получаем детали вакансии через HH клиент
        vacancy_data = await hh_client.get_vacancy_details(vacancy_id)

        vacancy_details = {
            "id": vacancy_data.get("id"),
            "hh_vacancy_id": vacancy_data.get("id"),
            "title": vacancy_data.get("name", ""),
            "description": vacancy_data.get("description", ""),

            # Навыки
            "key_skills": [skill.get("name", "") for skill in vacancy_data.get("key_skills", [])],

            # Зарплата
            "salary": {
                "from": vacancy_data.get("salary", {}).get("from") if vacancy_data.get("salary") else None,
                "to": vacancy_data.get("salary", {}).get("to") if vacancy_data.get("salary") else None,
                "currency": vacancy_data.get("salary", {}).get("currency", "RUR") if vacancy_data.get("salary") else "RUR",
                "gross": vacancy_data.get("salary", {}).get("gross", False) if vacancy_data.get("salary") else False
            },

            # Параметры
            "experience": {
                "id": vacancy_data.get("experience", {}).get("id") if vacancy_data.get("experience") else None,
                "name": vacancy_data.get("experience", {}).get("name") if vacancy_data.get("experience") else None
            },
            "employment": {
                "id": vacancy_data.get("employment", {}).get("id") if vacancy_data.get("employment") else None,
                "name": vacancy_data.get("employment", {}).get("name") if vacancy_data.get("employment") else None
            },
            "schedule": {
                "id": vacancy_data.get("schedule", {}).get("id") if vacancy_data.get("schedule") else None,
                "name": vacancy_data.get("schedule", {}).get("name") if vacancy_data.get("schedule") else None
            },

            # Локация
            "area": {
                "id": vacancy_data.get("area", {}).get("id") if vacancy_data.get("area") else None,
                "name": vacancy_data.get("area", {}).get("name") if vacancy_data.get("area") else None
            },
            "address": vacancy_data.get("address"),

            # Статистика
            "counters": vacancy_data.get("counters", {}),
            "is_active": not vacancy_data.get("archived", False),

            # Даты
            "published_at": vacancy_data.get("published_at"),
            "created_at": vacancy_data.get("created_at"),

            # Работодатель
            "employer": vacancy_data.get("employer", {}),

            # Дополнительные поля
            "url": vacancy_data.get("url"),
            "alternate_url": vacancy_data.get("alternate_url"),
            "apply_alternate_url": vacancy_data.get("apply_alternate_url"),
            "professional_roles": vacancy_data.get("professional_roles", []),
            "specializations": vacancy_data.get("specializations", []),

            # Мета информация
            "meta": {
                "source": "mock" if hh_client.is_mock_mode else "hh_api"
            }
        }

        logger.info(f"Успешно получена детальная информация о вакансии {vacancy_id}")
        return success(data=vacancy_details)

    except HHIntegrationError as e:
        logger.error(f"Ошибка интеграции с HH.ru: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "HH_INTEGRATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении деталей вакансии {vacancy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        )
    finally:
        # Закрываем HH клиент
        await hh_client.close()