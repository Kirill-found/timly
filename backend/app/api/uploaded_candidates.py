"""
API для загрузки и анализа резюме
Загрузка PDF/Excel файлов с резюме кандидатов
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.vacancy import Vacancy
from app.models.uploaded_candidate import UploadedCandidate, UploadSource
from app.services.resume_parser import ResumeParser
from app.utils.auth import get_current_user
from app.utils.exceptions import FileParseError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploaded-candidates", tags=["Uploaded Candidates"])


@router.post("/upload/pdf")
async def upload_pdf_resume(
    file: UploadFile = File(...),
    vacancy_id: Optional[UUID] = Form(None),
    auto_analyze: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка PDF резюме

    - Парсит PDF файл
    - Извлекает данные с помощью AI
    - Опционально анализирует под вакансию
    """
    # Проверка типа файла
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате PDF")

    # Проверка размера (макс 10 MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10 MB)")

    try:
        # Парсим PDF
        parser = ResumeParser()
        import io
        parsed_data = await parser.parse_pdf(io.BytesIO(content), file.filename)

        # Получаем вакансию если указана
        vacancy = None
        if vacancy_id:
            vacancy = db.query(Vacancy).filter(
                Vacancy.id == vacancy_id,
                Vacancy.user_id == current_user.id
            ).first()

        # Создаем кандидата в БД
        candidate = UploadedCandidate(
            user_id=current_user.id,
            vacancy_id=vacancy_id,
            source=UploadSource.PDF,
            original_filename=file.filename,
            original_text=parsed_data.get("original_text"),
            first_name=parsed_data.get("first_name"),
            last_name=parsed_data.get("last_name"),
            middle_name=parsed_data.get("middle_name"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            title=parsed_data.get("title"),
            age=parsed_data.get("age"),
            gender=parsed_data.get("gender"),
            city=parsed_data.get("city"),
            salary_expectation=parsed_data.get("salary_expectation"),
            experience_years=parsed_data.get("experience_years"),
            experience_text=parsed_data.get("experience_text"),
            skills=parsed_data.get("skills", []),
            education=parsed_data.get("education"),
            parsed_data=parsed_data
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # AI анализ если есть вакансия и включен auto_analyze
        if auto_analyze and vacancy:
            vacancy_data = {
                "title": vacancy.title,
                "key_skills": vacancy.key_skills or [],
                "experience": vacancy.experience,
                "salary_from": vacancy.salary_from,
                "salary_to": vacancy.salary_to,
                "currency": vacancy.currency or "RUB",
                "description": vacancy.description
            }

            analysis = await parser.analyze_candidate(parsed_data, vacancy_data)

            candidate.is_analyzed = True
            candidate.ai_score = analysis.get("score")
            candidate.ai_recommendation = analysis.get("recommendation")
            candidate.ai_summary = analysis.get("reasoning")
            candidate.ai_strengths = analysis.get("strengths", [])
            candidate.ai_weaknesses = analysis.get("weaknesses", [])
            candidate.ai_red_flags = analysis.get("red_flags", [])
            candidate.ai_analysis_data = analysis
            from datetime import datetime
            candidate.analyzed_at = datetime.utcnow()

            db.commit()
            db.refresh(candidate)

        logger.info(f"Загружен PDF кандидат: {candidate.full_name} (user={current_user.id})")

        return {
            "status": "success",
            "candidate": candidate.to_dict(),
            "message": f"Резюме успешно загружено и {'проанализировано' if candidate.is_analyzed else 'сохранено'}"
        }

    except FileParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка загрузки PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {e}")


@router.post("/upload/excel")
async def upload_excel_candidates(
    file: UploadFile = File(...),
    vacancy_id: Optional[UUID] = Form(None),
    auto_analyze: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка Excel файла с кандидатами

    - Парсит Excel (автоопределение колонок)
    - Создает кандидатов в БД
    - Опционально анализирует каждого под вакансию
    """
    # Проверка типа файла
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате Excel (.xlsx или .xls)")

    # Проверка размера (макс 10 MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10 MB)")

    try:
        # Парсим Excel
        parser = ResumeParser()
        import io
        candidates_data = await parser.parse_excel(io.BytesIO(content), file.filename)

        if not candidates_data:
            raise HTTPException(status_code=400, detail="Excel файл пустой или не содержит данных")

        # Получаем вакансию если указана
        vacancy = None
        vacancy_data = None
        if vacancy_id:
            vacancy = db.query(Vacancy).filter(
                Vacancy.id == vacancy_id,
                Vacancy.user_id == current_user.id
            ).first()
            if vacancy:
                vacancy_data = {
                    "title": vacancy.title,
                    "key_skills": vacancy.key_skills or [],
                    "experience": vacancy.experience,
                    "salary_from": vacancy.salary_from,
                    "salary_to": vacancy.salary_to,
                    "currency": vacancy.currency or "RUB",
                    "description": vacancy.description
                }

        created_candidates = []
        for candidate_data in candidates_data:
            # Создаем кандидата
            candidate = UploadedCandidate(
                user_id=current_user.id,
                vacancy_id=vacancy_id,
                source=UploadSource.EXCEL,
                original_filename=file.filename,
                first_name=candidate_data.get("first_name"),
                last_name=candidate_data.get("last_name"),
                email=candidate_data.get("email"),
                phone=candidate_data.get("phone"),
                title=candidate_data.get("title"),
                city=candidate_data.get("city"),
                salary_expectation=candidate_data.get("salary"),
                experience_years=candidate_data.get("experience"),
                skills=candidate_data.get("skills", []),
                parsed_data=candidate_data
            )

            db.add(candidate)
            db.flush()  # Получаем ID без коммита

            # AI анализ если есть вакансия
            if auto_analyze and vacancy_data:
                try:
                    analysis = await parser.analyze_candidate(candidate_data, vacancy_data)

                    candidate.is_analyzed = True
                    candidate.ai_score = analysis.get("score")
                    candidate.ai_recommendation = analysis.get("recommendation")
                    candidate.ai_summary = analysis.get("reasoning")
                    candidate.ai_strengths = analysis.get("strengths", [])
                    candidate.ai_weaknesses = analysis.get("weaknesses", [])
                    candidate.ai_red_flags = analysis.get("red_flags", [])
                    candidate.ai_analysis_data = analysis
                    from datetime import datetime
                    candidate.analyzed_at = datetime.utcnow()
                except Exception as e:
                    logger.warning(f"Ошибка анализа кандидата {candidate.full_name}: {e}")

            created_candidates.append(candidate)

        db.commit()

        logger.info(f"Загружено {len(created_candidates)} кандидатов из Excel (user={current_user.id})")

        return {
            "status": "success",
            "candidates_count": len(created_candidates),
            "analyzed_count": sum(1 for c in created_candidates if c.is_analyzed),
            "candidates": [c.to_dict() for c in created_candidates],
            "message": f"Загружено {len(created_candidates)} кандидатов"
        }

    except FileParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка загрузки Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {e}")


@router.get("/")
async def get_uploaded_candidates(
    vacancy_id: Optional[UUID] = Query(None),
    is_analyzed: Optional[bool] = Query(None),
    recommendation: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    sort_by: str = Query("ai_score", regex="^(ai_score|created_at|full_name)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка загруженных кандидатов

    Фильтры:
    - vacancy_id: по вакансии
    - is_analyzed: только проанализированные
    - recommendation: hire/interview/maybe/reject
    - min_score: минимальный AI score
    """
    query = db.query(UploadedCandidate).filter(
        UploadedCandidate.user_id == current_user.id
    )

    # Фильтры
    if vacancy_id:
        query = query.filter(UploadedCandidate.vacancy_id == vacancy_id)
    if is_analyzed is not None:
        query = query.filter(UploadedCandidate.is_analyzed == is_analyzed)
    if recommendation:
        query = query.filter(UploadedCandidate.ai_recommendation == recommendation)
    if min_score is not None:
        query = query.filter(UploadedCandidate.ai_score >= min_score)

    # Общее количество
    total = query.count()

    # Сортировка
    sort_column = getattr(UploadedCandidate, sort_by, UploadedCandidate.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Пагинация
    candidates = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "candidates": [c.to_dict() for c in candidates]
    }


@router.get("/{candidate_id}")
async def get_uploaded_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение кандидата по ID"""
    candidate = db.query(UploadedCandidate).filter(
        UploadedCandidate.id == candidate_id,
        UploadedCandidate.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    return candidate.to_dict_full()


@router.post("/{candidate_id}/analyze")
async def analyze_uploaded_candidate(
    candidate_id: UUID,
    vacancy_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Анализ кандидата под вакансию

    Запускает AI анализ для уже загруженного кандидата
    """
    candidate = db.query(UploadedCandidate).filter(
        UploadedCandidate.id == candidate_id,
        UploadedCandidate.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.user_id == current_user.id
    ).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")

    try:
        parser = ResumeParser()

        # Формируем данные кандидата
        candidate_data = {
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "title": candidate.title,
            "city": candidate.city,
            "experience_years": candidate.experience_years,
            "experience_text": candidate.experience_text,
            "skills": candidate.skills,
            "salary_expectation": candidate.salary_expectation
        }

        vacancy_data = {
            "title": vacancy.title,
            "key_skills": vacancy.key_skills or [],
            "experience": vacancy.experience,
            "salary_from": vacancy.salary_from,
            "salary_to": vacancy.salary_to,
            "currency": vacancy.currency or "RUB",
            "description": vacancy.description
        }

        analysis = await parser.analyze_candidate(candidate_data, vacancy_data)

        # Сохраняем результат
        candidate.vacancy_id = vacancy_id
        candidate.is_analyzed = True
        candidate.ai_score = analysis.get("score")
        candidate.ai_recommendation = analysis.get("recommendation")
        candidate.ai_summary = analysis.get("reasoning")
        candidate.ai_strengths = analysis.get("strengths", [])
        candidate.ai_weaknesses = analysis.get("weaknesses", [])
        candidate.ai_red_flags = analysis.get("red_flags", [])
        candidate.ai_analysis_data = analysis
        from datetime import datetime
        candidate.analyzed_at = datetime.utcnow()

        db.commit()
        db.refresh(candidate)

        return {
            "status": "success",
            "candidate": candidate.to_dict(),
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Ошибка анализа кандидата: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {e}")


@router.delete("/{candidate_id}")
async def delete_uploaded_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление кандидата"""
    candidate = db.query(UploadedCandidate).filter(
        UploadedCandidate.id == candidate_id,
        UploadedCandidate.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    db.delete(candidate)
    db.commit()

    return {"status": "success", "message": "Кандидат удален"}


@router.patch("/{candidate_id}")
async def update_uploaded_candidate(
    candidate_id: UUID,
    is_favorite: Optional[bool] = None,
    is_contacted: Optional[bool] = None,
    contact_status: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление статуса кандидата"""
    candidate = db.query(UploadedCandidate).filter(
        UploadedCandidate.id == candidate_id,
        UploadedCandidate.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

    if is_favorite is not None:
        candidate.is_favorite = is_favorite
    if is_contacted is not None:
        candidate.is_contacted = is_contacted
    if contact_status is not None:
        candidate.contact_status = contact_status
    if notes is not None:
        candidate.notes = notes

    db.commit()
    db.refresh(candidate)

    return candidate.to_dict()
