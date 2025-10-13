"""
API endpoints для интеграции с HH.ru
Синхронизация вакансий и откликов
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.api.auth import get_current_user
from app.schemas.base import APIResponse
from app.schemas.hh import (
    HHVacancyBasic, HHVacancyFull, HHApplication,
    SyncJobCreate, SyncJobStatus, HHTokenValidation
)
from app.services.hh_client import HHClient
from app.services.auth_service import AuthService
from app.utils.exceptions import HHIntegrationError, ValidationError
from app.utils.response import success, created, bad_request, unauthorized, not_found, internal_error

router = APIRouter()


@router.get("/test-connection", response_model=APIResponse)
async def test_hh_connection(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Тестирование соединения с HH.ru API
    Проверка валидности токена и доступности API
    """
    if not current_user.has_hh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "NO_HH_TOKEN",
                "message": "HH.ru токен не настроен. Добавьте токен в настройках."
            }
        )

    try:
        auth_service = AuthService(db)
        hh_client = await auth_service.get_hh_client(current_user.id)
        validation_result = await hh_client.test_connection()
        return success(data=validation_result.model_dump())
    except HHIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "HH_INTEGRATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при подключении к HH.ru"
            }
        )


@router.get("/vacancies", response_model=APIResponse)
async def get_vacancies(
    limit: int = 50,
    offset: int = 0,
    active_only: bool = True,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка вакансий пользователя
    Данные из локальной БД с возможностью фильтрации
    """
    from app.models.vacancy import Vacancy

    # Базовый запрос - только вакансии текущего пользователя
    query = db.query(Vacancy).filter(Vacancy.user_id == current_user.id)

    # Фильтрация по активности
    if active_only:
        query = query.filter(Vacancy.is_active == True)

    # Подсчет общего количества
    total = query.count()

    # Применение пагинации и сортировка по дате создания (новые сначала)
    vacancies = query.order_by(Vacancy.created_at.desc()).offset(offset).limit(limit).all()

    # Сериализация
    vacancies_data = [vacancy.to_dict() for vacancy in vacancies]

    return success(data={
        "vacancies": vacancies_data,
        "total": total,
        "limit": limit,
        "offset": offset
    })


@router.get("/vacancies/{vacancy_id}", response_model=APIResponse)
async def get_vacancy_details(
    vacancy_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение детальной информации о вакансии
    Включает статистику и последние отклики
    """
    from app.models.vacancy import Vacancy

    # Поиск вакансии по ID и проверка принадлежности пользователю
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.user_id == current_user.id
    ).first()

    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "VACANCY_NOT_FOUND",
                "message": f"Вакансия {vacancy_id} не найдена"
            }
        )

    return success(data=vacancy.to_dict())


@router.get("/vacancies/{vacancy_id}/applications", response_model=APIResponse)
async def get_vacancy_applications(
    vacancy_id: str,
    limit: int = 50,
    offset: int = 0,
    analyzed_only: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение откликов на конкретную вакансию
    С возможностью фильтрации по статусу анализа
    """
    from app.models.vacancy import Vacancy
    from app.models.application import Application

    # Проверка существования вакансии и принадлежности пользователю
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.user_id == current_user.id
    ).first()

    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "VACANCY_NOT_FOUND",
                "message": f"Вакансия {vacancy_id} не найдена"
            }
        )

    # Базовый запрос откликов для этой вакансии
    query = db.query(Application).filter(Application.vacancy_id == vacancy_id)

    # Фильтрация по статусу анализа
    if analyzed_only:
        query = query.filter(Application.analyzed_at.isnot(None))

    # Подсчет общего количества
    total = query.count()

    # Применение пагинации и сортировка по дате создания (новые сначала)
    applications = query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()

    # Сериализация
    applications_data = [app.to_dict() for app in applications]

    return success(data={
        "applications": applications_data,
        "vacancy_id": vacancy_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "analyzed_only": analyzed_only
    })


@router.post("/sync", response_model=APIResponse)
async def start_sync(
    sync_request: SyncJobCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Запуск синхронизации с HH.ru
    Создает фоновую задачу для получения данных
    """
    if not current_user.has_hh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "NO_HH_TOKEN",
                "message": "HH.ru токен не настроен"
            }
        )

    try:
        from app.models.application import SyncJob
        from app.workers.sync_jobs import run_vacancy_sync_background
        import uuid

        # Создаем задачу синхронизации в БД
        sync_job = SyncJob(
            id=uuid.uuid4(),
            user_id=current_user.id,
            status="pending",
            vacancies_synced=0,
            applications_synced=0,
            errors=[]
        )
        db.add(sync_job)
        db.commit()
        db.refresh(sync_job)

        # Запускаем фоновую задачу (используем синхронную обёртку)
        background_tasks.add_task(
            run_vacancy_sync_background,
            current_user.id,
            sync_job.id,
            sync_request.sync_vacancies,
            sync_request.sync_applications
        )

        return success(data=sync_job.to_dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SYNC_START_ERROR",
                "message": "Ошибка при запуске синхронизации"
            }
        )


@router.get("/sync/{job_id}", response_model=APIResponse)
async def get_sync_status(
    job_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статуса задачи синхронизации
    Для отслеживания прогресса синхронизации
    """
    from app.models.application import SyncJob

    # Получаем задачу из БД
    sync_job = db.query(SyncJob).filter(
        SyncJob.id == job_id,
        SyncJob.user_id == current_user.id
    ).first()

    if not sync_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SYNC_JOB_NOT_FOUND",
                "message": f"Задача синхронизации {job_id} не найдена"
            }
        )

    return success(data=sync_job.to_dict())


@router.get("/sync/history", response_model=APIResponse)
async def get_sync_history(
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    История задач синхронизации
    Последние задачи с результатами
    """
    # TODO: Реализовать получение истории синхронизации
    history_data = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "status": "completed",
            "vacancies_synced": 10,
            "applications_synced": 150,
            "errors": [],
            "started_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T00:05:00",
            "created_at": "2024-01-01T00:00:00"
        }
    ]

    return success(data={
        "sync_jobs": history_data,
        "total": len(history_data),
        "limit": limit
    })


@router.delete("/sync/{job_id}", response_model=APIResponse)
async def cancel_sync(
    job_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отмена выполняющейся задачи синхронизации
    Останавливает фоновую задачу
    """
    # TODO: Реализовать отмену задачи
    return success(data={
        "status": "TODO",
        "message": f"Отмена задачи {job_id} будет реализована",
        "job_id": job_id,
        "cancelled": True
    })


@router.get("/stats", response_model=APIResponse)
async def get_integration_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Статистика интеграции с HH.ru
    Общие метрики по синхронизации и данным
    """
    # TODO: Реализовать статистику интеграции
    stats_data = {
        "total_vacancies": 15,
        "active_vacancies": 12,
        "total_applications": 450,
        "new_applications_today": 12,
        "last_sync_at": "2024-01-01T10:00:00",
        "sync_frequency": "every_30_minutes",
        "api_calls_today": 156,
        "api_rate_limit_remaining": 4844
    }

    return success(data=stats_data)


@router.post("/oauth/exchange", response_model=APIResponse)
async def exchange_oauth_code(
    code: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обмен OAuth code на access_token
    Автоматизирует процесс получения токена от HH.ru
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== OAuth exchange request received ===")
    logger.info(f"Code: {code[:20]}...")
    logger.info(f"User: {current_user.id}")

    try:
        import httpx
        from app.config import settings
        from app.services.auth_service import AuthService

        # Обмен code на access_token через HH.ru API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.hh.ru/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.HH_CLIENT_ID,
                    "client_secret": settings.HH_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.HH_REDIRECT_URI
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error_description", "Не удалось получить токен")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "OAUTH_EXCHANGE_FAILED",
                        "message": f"Ошибка при обмене кода: {error_message}"
                    }
                )

            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "NO_ACCESS_TOKEN",
                        "message": "Не получен access_token от HH.ru"
                    }
                )

        # Сохраняем токен для пользователя
        auth_service = AuthService(db)
        await auth_service.update_hh_token(current_user.id, access_token)

        # Проверяем валидность токена
        hh_client = await auth_service.get_hh_client(current_user.id)
        validation_result = await hh_client.test_connection()

        return success(data={
            "token_saved": True,
            "token_valid": validation_result.get("is_valid", False),
            "employer_info": {
                "employer_name": validation_result.get("employer_name"),
                "employer_id": validation_result.get("employer_id")
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"OAuth exchange error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "OAUTH_EXCHANGE_ERROR",
                "message": "Ошибка при обмене OAuth кода на токен"
            }
        )