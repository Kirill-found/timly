"""
Фоновые задачи синхронизации с HH.ru
Async функции для получения вакансий и откликов через FastAPI BackgroundTasks
"""
import asyncio
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.application import SyncJob, Application
from app.models.vacancy import Vacancy
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


def run_vacancy_sync_background(
    user_id: UUID,
    sync_job_id: UUID,
    sync_vacancies: bool = True,
    sync_applications: bool = True
):
    """
    Синхронная обёртка для BackgroundTasks
    FastAPI BackgroundTasks не поддерживает async функции напрямую
    """
    logger.info(f"[BACKGROUND] Starting background sync for job {sync_job_id}")
    try:
        # Создаём новый event loop для фоновой задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_vacancy_sync(user_id, sync_job_id, sync_vacancies, sync_applications))
            logger.info(f"[BACKGROUND] Sync job {sync_job_id} completed successfully")
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"[BACKGROUND] Sync job {sync_job_id} failed: {e}", exc_info=True)
        # Отмечаем задачу как failed в БД
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            sync_job = db.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
            if sync_job:
                sync_job.status = "failed"
                sync_job.errors = [str(e)]
                sync_job.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()


async def run_vacancy_sync(
    user_id: UUID,
    sync_job_id: UUID,
    sync_vacancies: bool = True,
    sync_applications: bool = True
):
    """Основная функция синхронизации вакансий и откликов с HH.ru"""
    from app.database import SessionLocal

    # Создаём новую сессию БД для фоновой задачи
    db = SessionLocal()
    hh_client = None

    try:
        sync_job = db.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
        if sync_job:
            sync_job.status = "running"
            sync_job.started_at = datetime.utcnow()
            db.commit()

        logger.info(f"[SYNC] Starting sync job {sync_job_id} for user {user_id}")

        logger.info(f"[SYNC] Creating AuthService...")
        auth_service = AuthService(db)

        logger.info(f"[SYNC] Getting HH client...")
        hh_client = await auth_service.get_hh_client(user_id)
        logger.info(f"[SYNC] HH client obtained successfully")

        vacancies_synced = 0
        applications_synced = 0
        errors = []

        if sync_vacancies:
            try:
                logger.info(f"[SYNC] Starting vacancies sync...")
                vacancy_ids = await _sync_vacancies(db, user_id, hh_client)
                vacancies_synced = len(vacancy_ids)
                logger.info(f"[SYNC] Synced {vacancies_synced} vacancies")

                if sync_applications:
                    for vacancy_id in vacancy_ids:
                        try:
                            apps_count = await _sync_vacancy_applications(db, user_id, vacancy_id, hh_client)
                            applications_synced += apps_count
                        except Exception as e:
                            errors.append(f"Error syncing applications for vacancy {vacancy_id}: {str(e)}")

                logger.info(f"Synced {applications_synced} applications")
            except Exception as e:
                errors.append(f"Error syncing vacancies: {str(e)}")
                raise

        if sync_job:
            sync_job.status = "completed"
            sync_job.vacancies_synced = vacancies_synced
            sync_job.applications_synced = applications_synced
            sync_job.errors = errors
            sync_job.completed_at = datetime.utcnow()
            db.commit()

    except Exception as e:
        logger.error(f"Sync job {sync_job_id} failed: {str(e)}")
        sync_job = db.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
        if sync_job:
            sync_job.status = "failed"
            sync_job.errors = [str(e)]
            sync_job.completed_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        if hh_client:
            await hh_client.close()
        db.close()


async def _sync_vacancies(db: Session, user_id: UUID, hh_client) -> List[str]:
    """Синхронизация вакансий работодателя"""
    vacancy_ids = []
    page = 0
    per_page = 100

    while True:
        vacancies_data = await hh_client.get_my_vacancies(page=page, per_page=per_page)
        if not vacancies_data or not vacancies_data.get('items'):
            break

        for vacancy_data in vacancies_data['items']:
            try:
                vacancy_id = await _upsert_vacancy(db, user_id, vacancy_data)
                vacancy_ids.append(vacancy_id)
            except Exception as e:
                logger.error(f"Error upserting vacancy: {str(e)}")

        if page >= vacancies_data.get('pages', 1) - 1:
            break
        page += 1

    return vacancy_ids


async def _upsert_vacancy(db: Session, user_id: UUID, vacancy_data: Dict) -> str:
    """Создание или обновление вакансии"""
    hh_vacancy_id = str(vacancy_data.get('id'))
    existing = db.query(Vacancy).filter(
        Vacancy.user_id == user_id,
        Vacancy.hh_vacancy_id == hh_vacancy_id
    ).first()

    # Парсинг данных из HH.ru API
    salary = vacancy_data.get('salary') or {}
    experience = vacancy_data.get('experience') or {}
    employment = vacancy_data.get('employment') or {}
    schedule = vacancy_data.get('schedule') or {}
    area = vacancy_data.get('area') or {}
    key_skills = vacancy_data.get('key_skills', [])

    # Парсинг даты published_at из ISO 8601 формата
    published_at = None
    if vacancy_data.get('published_at'):
        try:
            date_str = vacancy_data['published_at']
            # Убираем timezone suffix для совместимости с fromisoformat
            if '+' in date_str:
                date_str = date_str.rsplit('+', 1)[0]
            elif date_str.endswith('Z'):
                date_str = date_str[:-1]
            published_at = datetime.fromisoformat(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse published_at: {vacancy_data.get('published_at')}, error: {e}")
            published_at = None

    data = {
        "user_id": user_id,
        "hh_vacancy_id": hh_vacancy_id,
        "title": vacancy_data.get('name', ''),
        "description": vacancy_data.get('description', ''),
        "key_skills": [skill.get('name') for skill in key_skills] if isinstance(key_skills, list) else [],
        "salary_from": salary.get('from'),
        "salary_to": salary.get('to'),
        "currency": salary.get('currency', 'RUB'),
        "experience": experience.get('id', ''),
        "employment": employment.get('id', ''),
        "schedule": schedule.get('id', ''),
        "area": area.get('name', ''),
        "is_active": not vacancy_data.get('archived', False),
        "published_at": published_at,
        "last_synced_at": datetime.utcnow()
    }

    if existing:
        for key, value in data.items():
            if key != "user_id":
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return str(existing.id)
    else:
        new_vacancy = Vacancy(**data)
        db.add(new_vacancy)
        db.commit()
        db.refresh(new_vacancy)
        return str(new_vacancy.id)


async def _sync_vacancy_applications(db: Session, user_id: UUID, vacancy_id: str, hh_client) -> int:
    """Синхронизация откликов для вакансии"""
    count = 0
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        return 0

    page = 0
    per_page = 100

    while True:
        logger.info(f"Загрузка откликов для вакансии {vacancy.hh_vacancy_id} (страница {page})")
        apps_data = await hh_client.get_vacancy_applications(vacancy.hh_vacancy_id, page=page, per_page=per_page)
        logger.info(f"Получено откликов: {len(apps_data.get('items', []))}")
        if not apps_data or not apps_data.get('items'):
            break

        for app_data in apps_data['items']:
            try:
                await _upsert_application(db, vacancy_id, app_data)
                count += 1
            except Exception as e:
                logger.error(f"Error upserting application: {str(e)}")
                # Откатываем транзакцию если была ошибка
                db.rollback()

        if page >= apps_data.get('pages', 1) - 1:
            break
        page += 1

    # Обновляем счетчики откликов в вакансии
    vacancy.applications_count = count
    vacancy.new_applications_count = db.query(Application).filter(
        Application.vacancy_id == vacancy_id,
        Application.analyzed_at.is_(None)
    ).count()
    db.commit()

    return count


async def _upsert_application(db: Session, vacancy_id: str, application_data: Dict) -> str:
    """Создание или обновление отклика"""
    hh_application_id = str(application_data.get('id'))

    # Ищем дубликаты по hh_application_id глобально (не только в рамках вакансии)
    # Потому что один и тот же отклик может быть связан с разными вакансиями
    existing = db.query(Application).filter(
        Application.hh_application_id == hh_application_id
    ).first()

    resume = application_data.get('resume', {})
    first_name = resume.get('first_name', '')
    last_name = resume.get('last_name', '')
    candidate_name = f"{first_name} {last_name}".strip() or "Имя не указано"

    # Парсинг контактов из резюме (извлекаем formatted строку из dict)
    contacts = resume.get('contact', [])
    candidate_email = None
    candidate_phone = None
    if contacts and isinstance(contacts, list):
        for contact in contacts:
            if isinstance(contact, dict):
                contact_type = contact.get('type', {})
                value = contact.get('value')

                if isinstance(contact_type, dict) and contact_type.get('id') == 'email':
                    # Email может быть строкой или вложенным dict с полем 'value'
                    if isinstance(value, dict):
                        candidate_email = value.get('value') or value.get('formatted')
                    else:
                        candidate_email = value

                elif isinstance(contact_type, dict) and contact_type.get('id') == 'cell':
                    # Телефон может быть строкой или dict с полем 'formatted'
                    if isinstance(value, dict):
                        candidate_phone = value.get('formatted') or value.get('number')
                    else:
                        candidate_phone = value

    # Сериализуем resume_data через JSON чтобы убрать не-сериализуемые объекты
    try:
        resume_data_clean = json.loads(json.dumps(resume, default=str))
    except Exception as e:
        logger.warning(f"Failed to serialize resume_data, using empty dict: {e}")
        resume_data_clean = {}

    # Извлекаем collection_id и state из данных HH.ru
    # collection_id берем из параметра _collection_id, если он был передан
    # state извлекаем из поля state.id
    state_data = application_data.get('state', {})
    state_id = state_data.get('id') if isinstance(state_data, dict) else None

    data = {
        "vacancy_id": vacancy_id,
        "hh_application_id": hh_application_id,
        "hh_resume_id": str(resume.get('id', '')),
        "hh_negotiation_id": str(application_data.get('negotiation_id', '')),
        "candidate_name": str(candidate_name) if candidate_name else None,
        "candidate_email": str(candidate_email) if candidate_email else None,
        "candidate_phone": str(candidate_phone) if candidate_phone else None,
        "resume_url": str(resume.get('alternate_url', '')) if resume.get('alternate_url') else None,
        "resume_data": resume_data_clean,
        "collection_id": application_data.get('_collection_id'),  # Добавим в hh_client
        "state": state_id
    }

    if existing:
        # Обновляем все поля, включая vacancy_id (отклик мог переместиться на другую вакансию)
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return str(existing.id)
    else:
        new_app = Application(**data)
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return str(new_app.id)
