"""
API endpoints для работы с откликами
Статистика, фильтрация и получение откликов
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.schemas.base import APIResponse
from app.schemas.auth import UserProfile
from app.services.auth_service import AuthService
from app.models.application import Application, AnalysisResult
from app.models.vacancy import Vacancy
from app.utils.exceptions import AuthenticationError
from app.utils.response import success, not_found

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Получение текущего пользователя"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "INVALID_CREDENTIALS", "message": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "AUTHENTICATION_ERROR", "message": str(e)},
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/stats", response_model=APIResponse)
async def get_applications_stats(
    vacancy_id: Optional[str] = Query(None, description="ID вакансии для фильтрации"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики по откликам

    Возвращает:
    - Всего откликов
    - Непроанализированных откликов (без AnalysisResult)
    - Проанализированных откликов (с AnalysisResult)
    - Разбивка по collection_id (response, consider, interview, discard)
    """
    try:
        # Базовый запрос - только отклики пользователя
        base_query = db.query(Application).join(Vacancy).filter(
            Vacancy.user_id == current_user.id
        )

        # Фильтр по вакансии (если указана)
        if vacancy_id:
            base_query = base_query.filter(Application.vacancy_id == vacancy_id)

        # Общее количество откликов
        total_applications = base_query.count()

        # Количество проанализированных (есть запись в AnalysisResult)
        analyzed_count = base_query.join(
            AnalysisResult,
            Application.id == AnalysisResult.application_id,
            isouter=False
        ).count()

        # Количество непроанализированных (нет записи в AnalysisResult)
        # ИСКЛЮЧАЕМ discard - они не должны анализироваться
        from sqlalchemy import or_, and_, not_
        unanalyzed_count = base_query.outerjoin(
            AnalysisResult,
            Application.id == AnalysisResult.application_id
        ).filter(
            AnalysisResult.id == None,
            # Только response и consider, БЕЗ discard
            and_(
                or_(
                    Application.collection_id.like('%response%'),
                    Application.collection_id.like('%consider%')
                ),
                not_(Application.collection_id.like('%discard%'))
            )
        ).count()

        # Разбивка по collection_id
        collections_stats = db.query(
            Application.collection_id,
            func.count(Application.id).label('count'),
            func.count(AnalysisResult.id).label('analyzed')
        ).join(Vacancy).outerjoin(
            AnalysisResult,
            Application.id == AnalysisResult.application_id
        ).filter(
            Vacancy.user_id == current_user.id
        )

        if vacancy_id:
            collections_stats = collections_stats.filter(Application.vacancy_id == vacancy_id)

        collections_stats = collections_stats.group_by(Application.collection_id).all()

        # Форматируем результат
        collections_breakdown = {}
        for coll_id, count, analyzed in collections_stats:
            collection_name = coll_id or "unknown"
            collections_breakdown[collection_name] = {
                "total": count,
                "analyzed": analyzed,
                "unanalyzed": count - analyzed
            }

        stats_data = {
            "total_applications": total_applications,
            "analyzed_applications": analyzed_count,
            "unanalyzed_applications": unanalyzed_count,
            "by_collection": collections_breakdown,
            "vacancy_id": vacancy_id
        }

        return success(data=stats_data)

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "STATS_ERROR", "message": f"Ошибка получения статистики: {str(e)}"}
        )


@router.get("/unanalyzed", response_model=APIResponse)
async def get_unanalyzed_applications(
    vacancy_id: Optional[str] = Query(None, description="ID вакансии для фильтрации"),
    collection_id: Optional[str] = Query("response", description="Фильтр по статусу (response, consider, interview, discard)"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум откликов"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка непроанализированных откликов

    По умолчанию возвращает только отклики со статусом 'response' (неразобранные)
    """
    try:
        # Запрос непроанализированных откликов
        query = db.query(Application).join(Vacancy).outerjoin(
            AnalysisResult,
            Application.id == AnalysisResult.application_id
        ).filter(
            Vacancy.user_id == current_user.id,
            AnalysisResult.id == None  # Нет анализа
        )

        # Фильтр по вакансии
        if vacancy_id:
            query = query.filter(Application.vacancy_id == vacancy_id)

        # Фильтр по collection_id (по умолчанию только 'response')
        if collection_id:
            query = query.filter(Application.collection_id.like(f"%{collection_id}%"))
        else:
            # Если фильтр не указан - берём response и consider, исключаем discard
            from sqlalchemy import or_, and_, not_
            query = query.filter(
                and_(
                    or_(
                        Application.collection_id.like('%response%'),
                        Application.collection_id.like('%consider%')
                    ),
                    not_(Application.collection_id.like('%discard%'))
                )
            )

        # Ограничение количества
        applications = query.limit(limit).all()

        # Сериализация
        applications_data = [app.to_dict() for app in applications]

        result = {
            "applications": applications_data,
            "count": len(applications_data),
            "filters": {
                "vacancy_id": vacancy_id,
                "collection_id": collection_id,
                "limit": limit
            }
        }

        return success(data=result)

    except Exception as e:
        logger.error(f"Ошибка получения непроанализированных откликов: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "FETCH_ERROR", "message": f"Ошибка получения откликов: {str(e)}"}
        )
