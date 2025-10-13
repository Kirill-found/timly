"""
API endpoints для работы с вакансиями и анализом откликов
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.core.security import decrypt_hh_token
from app.models import User, Vacancy, Application
from app.schemas.vacancy import (
    VacancyResponse,
    VacancySyncRequest,
    ApplicationResponse,
    AnalysisRequest,
    AnalysisResult
)
from app.services.hh_client import HHClient
from app.services.ai_analyzer import AIAnalyzer
from app.api.auth import get_current_user

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


@router.post("/sync")
async def sync_vacancies(
    sync_request: VacancySyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Синхронизация вакансий с HH.ru
    
    Получает список активных вакансий работодателя и сохраняет их в БД
    """
    # Проверяем наличие токена
    if not current_user.encrypted_hh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен HH.ru не настроен"
        )
    
    # Расшифровываем токен
    try:
        hh_token = decrypt_hh_token(current_user.encrypted_hh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка расшифровки токена"
        )
    
    # Получаем вакансии с HH.ru
    hh_client = HHClient(hh_token)
    hh_vacancies = await hh_client.get_employer_vacancies()
    
    if not hh_vacancies:
        return {
            "message": "Активные вакансии не найдены",
            "synced_count": 0
        }
    
    synced_count = 0
    
    # Сохраняем вакансии в БД
    for hh_vacancy in hh_vacancies:
        # Проверяем, существует ли вакансия
        result = await db.execute(
            select(Vacancy).where(
                Vacancy.user_id == current_user.id,
                Vacancy.hh_vacancy_id == str(hh_vacancy["id"])
            )
        )
        existing_vacancy = result.scalar_one_or_none()
        
        if existing_vacancy:
            # Обновляем существующую вакансию
            existing_vacancy.title = hh_vacancy["name"]
            existing_vacancy.company_name = hh_vacancy.get("employer", {}).get("name")
            existing_vacancy.raw_data = hh_vacancy
            existing_vacancy.last_synced_at = datetime.utcnow()
        else:
            # Создаём новую вакансию
            new_vacancy = Vacancy(
                user_id=current_user.id,
                hh_vacancy_id=str(hh_vacancy["id"]),
                title=hh_vacancy["name"],
                company_name=hh_vacancy.get("employer", {}).get("name"),
                raw_data=hh_vacancy,
                last_synced_at=datetime.utcnow()
            )
            db.add(new_vacancy)
            synced_count += 1
    
    await db.commit()
    
    # Запускаем фоновую задачу для синхронизации откликов
    background_tasks.add_task(sync_applications_task, current_user.id, hh_token)
    
    return {
        "message": f"Синхронизировано вакансий: {synced_count}",
        "synced_count": synced_count,
        "total_vacancies": len(hh_vacancies)
    }


@router.get("/", response_model=List[VacancyResponse])
async def get_vacancies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка вакансий пользователя
    """
    # Получаем вакансии с количеством откликов
    result = await db.execute(
        select(
            Vacancy,
            func.count(Application.id).label("applications_count")
        )
        .outerjoin(Application)
        .where(Vacancy.user_id == current_user.id)
        .group_by(Vacancy.id)
        .order_by(Vacancy.created_at.desc())
    )
    
    vacancies = []
    for vacancy, apps_count in result:
        vacancy_dict = VacancyResponse.model_validate(vacancy).model_dump()
        vacancy_dict["applications_count"] = apps_count
        vacancies.append(VacancyResponse(**vacancy_dict))
    
    return vacancies


@router.get("/{vacancy_id}/applications", response_model=List[ApplicationResponse])
async def get_vacancy_applications(
    vacancy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение откликов на вакансию
    """
    # Проверяем доступ к вакансии
    result = await db.execute(
        select(Vacancy).where(
            Vacancy.id == vacancy_id,
            Vacancy.user_id == current_user.id
        )
    )
    vacancy = result.scalar_one_or_none()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вакансия не найдена"
        )
    
    # Получаем отклики
    result = await db.execute(
        select(Application)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.score.desc().nullsfirst(), Application.created_at.desc())
    )
    applications = result.scalars().all()
    
    return [ApplicationResponse.model_validate(app) for app in applications]


@router.post("/{vacancy_id}/analyze")
async def analyze_vacancy_applications(
    vacancy_id: str,
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Запуск анализа откликов на вакансию с помощью AI
    """
    # Проверяем доступ к вакансии
    result = await db.execute(
        select(Vacancy).where(
            Vacancy.id == vacancy_id,
            Vacancy.user_id == current_user.id
        )
    )
    vacancy = result.scalar_one_or_none()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вакансия не найдена"
        )
    
    # Проверяем токен HH.ru
    if not current_user.encrypted_hh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен HH.ru не настроен"
        )
    
    # Запускаем анализ в фоне
    background_tasks.add_task(
        analyze_applications_task,
        vacancy_id,
        decrypt_hh_token(current_user.encrypted_hh_token),
        analysis_request.analyze_all
    )
    
    return {
        "message": "Анализ запущен в фоновом режиме",
        "vacancy_id": vacancy_id
    }


async def sync_applications_task(user_id: str, hh_token: str):
    """
    Фоновая задача для синхронизации откликов
    
    Args:
        user_id: ID пользователя
        hh_token: Расшифрованный токен HH.ru
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Получаем вакансии пользователя
        result = await db.execute(
            select(Vacancy).where(Vacancy.user_id == user_id)
        )
        vacancies = result.scalars().all()
        
        hh_client = HHClient(hh_token)
        
        for vacancy in vacancies:
            # Получаем отклики с HH.ru
            hh_applications = await hh_client.get_vacancy_applications(vacancy.hh_vacancy_id)
            
            for hh_app in hh_applications:
                # Проверяем, существует ли отклик
                result = await db.execute(
                    select(Application).where(
                        Application.vacancy_id == vacancy.id,
                        Application.hh_application_id == str(hh_app["id"])
                    )
                )
                existing_app = result.scalar_one_or_none()
                
                if not existing_app:
                    # Создаём новый отклик
                    resume = hh_app.get("resume", {})
                    new_app = Application(
                        vacancy_id=vacancy.id,
                        hh_application_id=str(hh_app["id"]),
                        hh_resume_id=str(resume.get("id")) if resume else None,
                        candidate_name=f"{resume.get('first_name', '')} {resume.get('last_name', '')}".strip(),
                        candidate_email=resume.get("contact", [{}])[0].get("value") if resume.get("contact") else None,
                        status="pending"
                    )
                    
                    # Создаём хеш резюме для дедупликации
                    if resume:
                        resume_text = str(resume)
                        new_app.resume_hash = hashlib.md5(resume_text.encode()).hexdigest()
                    
                    db.add(new_app)
            
            await db.commit()


async def analyze_applications_task(vacancy_id: str, hh_token: str, analyze_all: bool = False):
    """
    Фоновая задача для анализа откликов с помощью AI
    
    Args:
        vacancy_id: ID вакансии
        hh_token: Расшифрованный токен HH.ru
        analyze_all: Анализировать все отклики, включая обработанные
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Получаем вакансию
        result = await db.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = result.scalar_one_or_none()
        
        if not vacancy:
            return
        
        # Получаем отклики для анализа
        query = select(Application).where(Application.vacancy_id == vacancy_id)
        if not analyze_all:
            query = query.where(Application.status == "pending")
        
        result = await db.execute(query)
        applications = result.scalars().all()
        
        hh_client = HHClient(hh_token)
        ai_analyzer = AIAnalyzer()
        
        for application in applications:
            try:
                # Обновляем статус
                application.status = "analyzing"
                await db.commit()
                
                # Получаем резюме с HH.ru
                if application.hh_resume_id:
                    resume_data = await hh_client.get_resume(application.hh_resume_id)
                    
                    if resume_data:
                        # Получаем сопроводительное письмо
                        messages = await hh_client.get_application_messages(application.hh_application_id)
                        cover_letter = messages[0].get("text") if messages else None
                        
                        # Анализируем с помощью AI
                        analysis_result = await ai_analyzer.analyze_resume(
                            resume_data,
                            vacancy.raw_data,
                            cover_letter
                        )
                        
                        # Сохраняем результаты
                        application.analysis_result = analysis_result
                        application.score = analysis_result.get("score", 0)
                        application.ai_summary = analysis_result.get("summary", "")
                        application.status = "completed"
                        application.processed_at = datetime.utcnow()
                    else:
                        application.status = "error"
                        application.error_message = "Не удалось получить резюме"
                else:
                    application.status = "error"
                    application.error_message = "Отсутствует ID резюме"
                    
            except Exception as e:
                application.status = "error"
                application.error_message = str(e)
            
            await db.commit()