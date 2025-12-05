"""
API endpoints для поиска по базе резюме
Создание поисков, запуск, получение кандидатов, AI анализ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.resume_search import ResumeSearch, SearchCandidate, SearchStatus
from app.models.vacancy import Vacancy
from app.schemas.resume_search import (
    ResumeSearchCreate, ResumeSearchUpdate, ResumeSearchResponse,
    ResumeSearchListResponse, CandidateResponse, CandidateListResponse,
    CandidateDetailResponse, RunSearchRequest, AnalyzeCandidatesRequest,
    UpdateCandidateRequest, SearchDictionaries, SearchStats
)
from app.schemas.base import APIResponse
from app.utils.response import success, created, bad_request, not_found
from app.services.resume_search_service import ResumeSearchService

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== CRUD поисковых проектов ====================

@router.get("/searches", response_model=APIResponse)
async def list_searches(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    vacancy_id: Optional[str] = Query(None, description="Фильтр по вакансии"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка поисковых проектов пользователя
    """
    query = db.query(ResumeSearch).filter(ResumeSearch.user_id == current_user.id)

    if status_filter:
        query = query.filter(ResumeSearch.status == status_filter)
    if vacancy_id:
        query = query.filter(ResumeSearch.vacancy_id == vacancy_id)

    total = query.count()
    searches = query.order_by(ResumeSearch.updated_at.desc()).offset(offset).limit(limit).all()

    return success(data={
        "searches": [s.to_dict() for s in searches],
        "total": total
    })


@router.post("/searches", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_search(
    data: ResumeSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового поискового проекта
    """
    # Проверяем вакансию если указана
    if data.vacancy_id:
        vacancy = db.query(Vacancy).filter(
            Vacancy.id == data.vacancy_id,
            Vacancy.user_id == current_user.id
        ).first()
        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "VACANCY_NOT_FOUND", "message": "Вакансия не найдена"}
            )

    search = ResumeSearch(
        user_id=current_user.id,
        vacancy_id=data.vacancy_id,
        name=data.name,
        description=data.description,
        search_query=data.search_query,
        filters=data.filters.model_dump() if data.filters else {},
        status=SearchStatus.DRAFT
    )

    db.add(search)
    db.commit()
    db.refresh(search)

    logger.info(f"Создан поисковый проект: {search.name} (user={current_user.email})")
    return created(data=search.to_dict())


@router.get("/searches/{search_id}", response_model=APIResponse)
async def get_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение поискового проекта по ID
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    return success(data=search.to_dict())


@router.put("/searches/{search_id}", response_model=APIResponse)
async def update_search(
    search_id: str,
    data: ResumeSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление поискового проекта
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    # Обновляем только переданные поля
    if data.name is not None:
        search.name = data.name
    if data.description is not None:
        search.description = data.description
    if data.search_query is not None:
        search.search_query = data.search_query
    if data.vacancy_id is not None:
        search.vacancy_id = data.vacancy_id
    if data.filters is not None:
        search.filters = data.filters.model_dump()

    db.commit()
    db.refresh(search)

    return success(data=search.to_dict())


@router.delete("/searches/{search_id}", response_model=APIResponse)
async def delete_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление поискового проекта
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    db.delete(search)
    db.commit()

    logger.info(f"Удален поисковый проект: {search.name} (user={current_user.email})")
    return success(data={"message": "Поисковый проект удален"})


# ==================== Запуск поиска ====================

@router.post("/searches/{search_id}/run", response_model=APIResponse)
async def run_search(
    search_id: str,
    data: RunSearchRequest = RunSearchRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Запуск поиска по базе резюме HH.ru
    Загружает резюме и сохраняет в БД
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    if search.status == SearchStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "SEARCH_ALREADY_RUNNING", "message": "Поиск уже выполняется"}
        )

    try:
        service = ResumeSearchService(db, current_user)
        result = await service.run_search(search, max_results=data.max_results)
        return success(data=result)
    except Exception as e:
        logger.error(f"Ошибка запуска поиска: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "SEARCH_ERROR", "message": str(e)}
        )


# ==================== Кандидаты ====================

@router.get("/searches/{search_id}/candidates", response_model=APIResponse)
async def list_candidates(
    search_id: str,
    analyzed_only: bool = Query(False, description="Только проанализированные"),
    recommendation: Optional[str] = Query(None, description="Фильтр по рекомендации: hire, consider, reject"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Минимальный AI score"),
    favorites_only: bool = Query(False, description="Только избранные"),
    order_by: str = Query("score", description="Сортировка: score, name, created"),
    page: int = Query(0, ge=0),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка кандидатов из поиска
    """
    # Проверяем доступ к поиску
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    # Строим запрос
    query = db.query(SearchCandidate).filter(SearchCandidate.search_id == search_id)

    if analyzed_only:
        query = query.filter(SearchCandidate.is_analyzed == True)
    if recommendation:
        query = query.filter(SearchCandidate.ai_recommendation == recommendation)
    if min_score is not None:
        query = query.filter(SearchCandidate.ai_score >= min_score)
    if favorites_only:
        query = query.filter(SearchCandidate.is_favorite == True)

    # Сортировка
    if order_by == "score":
        query = query.order_by(SearchCandidate.ai_score.desc().nullslast())
    elif order_by == "name":
        query = query.order_by(SearchCandidate.last_name, SearchCandidate.first_name)
    else:
        query = query.order_by(SearchCandidate.created_at.desc())

    total = query.count()
    candidates = query.offset(page * per_page).limit(per_page).all()

    return success(data={
        "candidates": [c.to_dict() for c in candidates],
        "total": total,
        "page": page,
        "per_page": per_page
    })


@router.get("/searches/{search_id}/candidates/{candidate_id}", response_model=APIResponse)
async def get_candidate(
    search_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение полных данных кандидата
    """
    candidate = db.query(SearchCandidate).join(ResumeSearch).filter(
        SearchCandidate.id == candidate_id,
        SearchCandidate.search_id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CANDIDATE_NOT_FOUND", "message": "Кандидат не найден"}
        )

    return success(data=candidate.to_dict_full())


@router.put("/searches/{search_id}/candidates/{candidate_id}", response_model=APIResponse)
async def update_candidate(
    search_id: str,
    candidate_id: str,
    data: UpdateCandidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление данных кандидата (избранное, заметки и т.д.)
    """
    candidate = db.query(SearchCandidate).join(ResumeSearch).filter(
        SearchCandidate.id == candidate_id,
        SearchCandidate.search_id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CANDIDATE_NOT_FOUND", "message": "Кандидат не найден"}
        )

    if data.is_favorite is not None:
        candidate.is_favorite = data.is_favorite
    if data.is_contacted is not None:
        candidate.is_contacted = data.is_contacted
    if data.notes is not None:
        candidate.notes = data.notes

    db.commit()
    db.refresh(candidate)

    return success(data=candidate.to_dict())


# ==================== AI Анализ ====================

@router.post("/searches/{search_id}/analyze", response_model=APIResponse)
async def analyze_candidates(
    search_id: str,
    data: AnalyzeCandidatesRequest = AnalyzeCandidatesRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Запуск AI анализа кандидатов
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    if search.status == SearchStatus.ANALYZING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ANALYSIS_IN_PROGRESS", "message": "Анализ уже выполняется"}
        )

    try:
        service = ResumeSearchService(db, current_user)
        result = await service.analyze_candidates(
            search,
            candidate_ids=data.candidate_ids,
            force_reanalysis=data.force_reanalysis
        )
        return success(data=result)
    except Exception as e:
        logger.error(f"Ошибка анализа кандидатов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ANALYSIS_ERROR", "message": str(e)}
        )


# ==================== Статистика ====================

@router.get("/searches/{search_id}/stats", response_model=APIResponse)
async def get_search_stats(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Статистика по поисковому проекту
    """
    search = db.query(ResumeSearch).filter(
        ResumeSearch.id == search_id,
        ResumeSearch.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SEARCH_NOT_FOUND", "message": "Поисковый проект не найден"}
        )

    # Считаем статистику
    total = db.query(SearchCandidate).filter(SearchCandidate.search_id == search_id).count()
    analyzed = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.is_analyzed == True
    ).count()

    hire_count = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.ai_recommendation == "hire"
    ).count()

    consider_count = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.ai_recommendation == "consider"
    ).count()

    reject_count = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.ai_recommendation == "reject"
    ).count()

    favorites = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.is_favorite == True
    ).count()

    contacted = db.query(SearchCandidate).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.is_contacted == True
    ).count()

    # Средний score
    from sqlalchemy import func
    avg_score = db.query(func.avg(SearchCandidate.ai_score)).filter(
        SearchCandidate.search_id == search_id,
        SearchCandidate.ai_score.isnot(None)
    ).scalar()

    return success(data={
        "total_candidates": total,
        "analyzed_count": analyzed,
        "hire_count": hire_count,
        "consider_count": consider_count,
        "reject_count": reject_count,
        "favorites_count": favorites,
        "contacted_count": contacted,
        "avg_score": round(avg_score, 1) if avg_score else None
    })


# ==================== Справочники ====================

@router.get("/dictionaries", response_model=APIResponse)
async def get_search_dictionaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение справочников для фильтров поиска
    """
    try:
        service = ResumeSearchService(db, current_user)
        dictionaries = await service.get_dictionaries()
        return success(data=dictionaries)
    except Exception as e:
        logger.error(f"Ошибка получения справочников: {e}")
        # Возвращаем базовые справочники
        return success(data={
            "experience": [
                {"id": "noExperience", "name": "Нет опыта"},
                {"id": "between1And3", "name": "От 1 до 3 лет"},
                {"id": "between3And6", "name": "От 3 до 6 лет"},
                {"id": "moreThan6", "name": "Более 6 лет"}
            ],
            "education_level": [
                {"id": "secondary", "name": "Среднее"},
                {"id": "special_secondary", "name": "Среднее специальное"},
                {"id": "higher", "name": "Высшее"},
                {"id": "bachelor", "name": "Бакалавр"},
                {"id": "master", "name": "Магистр"}
            ],
            "gender": [
                {"id": "male", "name": "Мужской"},
                {"id": "female", "name": "Женский"}
            ],
            "order_by": [
                {"id": "relevance", "name": "По релевантности"},
                {"id": "publication_time", "name": "По дате обновления"},
                {"id": "salary_desc", "name": "По убыванию зарплаты"},
                {"id": "salary_asc", "name": "По возрастанию зарплаты"}
            ],
            "areas": [
                {"id": "1", "name": "Москва"},
                {"id": "2", "name": "Санкт-Петербург"},
                {"id": "3", "name": "Екатеринбург"},
                {"id": "4", "name": "Новосибирск"}
            ]
        })
