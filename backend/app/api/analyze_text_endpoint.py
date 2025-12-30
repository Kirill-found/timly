"""
Дополнительные endpoints для анализа по тексту вакансии
Добавить в конец uploaded_candidates.py
"""


@router.post("/{candidate_id}/analyze-text")
async def analyze_with_vacancy_text(
    candidate_id: UUID,
    vacancy_title: str = Form(...),
    vacancy_description: str = Form(...),
    key_skills: Optional[str] = Form(None),
    experience: Optional[str] = Form(None),
    salary_from: Optional[int] = Form(None),
    salary_to: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Анализ кандидата по тексту вакансии (без HH.ru)

    Позволяет анализировать резюме без привязки к HH.ru аккаунту.
    Просто вставьте текст вакансии и получите AI анализ.
    """
    candidate = db.query(UploadedCandidate).filter(
        UploadedCandidate.id == candidate_id,
        UploadedCandidate.user_id == current_user.id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")

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
            "salary_expectation": candidate.salary_expectation,
            "original_text": candidate.original_text
        }

        # Парсим ключевые навыки из строки
        skills_list = []
        if key_skills:
            skills_list = [s.strip() for s in key_skills.split(",") if s.strip()]

        # Формируем данные вакансии из текста
        vacancy_data = {
            "title": vacancy_title,
            "description": vacancy_description,
            "key_skills": skills_list,
            "experience": experience,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "currency": "RUB"
        }

        analysis = await parser.analyze_candidate(candidate_data, vacancy_data)

        # Сохраняем результат (без vacancy_id так как вакансия не в БД)
        candidate.is_analyzed = True
        candidate.ai_score = analysis.get("score")
        candidate.ai_recommendation = analysis.get("recommendation")
        candidate.ai_summary = analysis.get("reasoning")
        candidate.ai_strengths = analysis.get("strengths", [])
        candidate.ai_weaknesses = analysis.get("weaknesses", [])
        candidate.ai_red_flags = analysis.get("red_flags", [])
        candidate.ai_analysis_data = {
            **analysis,
            "vacancy_text": {
                "title": vacancy_title,
                "description": vacancy_description[:500] + "..." if len(vacancy_description) > 500 else vacancy_description
            }
        }
        from datetime import datetime
        candidate.analyzed_at = datetime.utcnow()

        db.commit()
        db.refresh(candidate)

        logger.info(f"Анализ кандидата {candidate.full_name} по тексту вакансии (user={current_user.id})")

        return {
            "status": "success",
            "candidate": candidate.to_dict(),
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Ошибка анализа кандидата по тексту: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {e}")


@router.post("/upload-and-analyze-text")
async def upload_and_analyze_with_text(
    file: UploadFile = File(...),
    vacancy_title: str = Form(...),
    vacancy_description: str = Form(...),
    key_skills: Optional[str] = Form(None),
    experience: Optional[str] = Form(None),
    salary_from: Optional[int] = Form(None),
    salary_to: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка резюме и анализ по тексту вакансии (без HH.ru) - всё в одном запросе

    Идеально для пользователей без аккаунта HH.ru:
    1. Загружает PDF/Excel резюме
    2. Анализирует по введённому тексту вакансии
    3. Возвращает AI оценку кандидата
    """
    # Проверка типа файла
    filename_lower = file.filename.lower()
    is_pdf = filename_lower.endswith('.pdf')
    is_excel = filename_lower.endswith(('.xlsx', '.xls'))

    if not is_pdf and not is_excel:
        raise HTTPException(status_code=400, detail="Файл должен быть в формате PDF или Excel")

    # Проверка размера (макс 10 MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10 MB)")

    try:
        parser = ResumeParser()
        import io

        # Парсим файл
        if is_pdf:
            parsed_data = await parser.parse_pdf(io.BytesIO(content), file.filename)
            source = UploadSource.PDF
        else:
            candidates_list = await parser.parse_excel(io.BytesIO(content), file.filename)
            if not candidates_list:
                raise HTTPException(status_code=400, detail="Excel файл пустой")
            parsed_data = candidates_list[0]  # Берём первого кандидата
            source = UploadSource.EXCEL

        # Создаем кандидата в БД
        candidate = UploadedCandidate(
            user_id=current_user.id,
            vacancy_id=None,  # Нет вакансии из БД
            source=source,
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
            salary_expectation=parsed_data.get("salary_expectation") or parsed_data.get("salary"),
            experience_years=parsed_data.get("experience_years") or parsed_data.get("experience"),
            experience_text=parsed_data.get("experience_text"),
            skills=parsed_data.get("skills", []),
            education=parsed_data.get("education"),
            parsed_data=parsed_data
        )

        db.add(candidate)
        db.flush()

        # Парсим ключевые навыки
        skills_list = []
        if key_skills:
            skills_list = [s.strip() for s in key_skills.split(",") if s.strip()]

        # Формируем данные вакансии
        vacancy_data = {
            "title": vacancy_title,
            "description": vacancy_description,
            "key_skills": skills_list,
            "experience": experience,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "currency": "RUB"
        }

        # AI анализ
        analysis = await parser.analyze_candidate(parsed_data, vacancy_data)

        candidate.is_analyzed = True
        candidate.ai_score = analysis.get("score")
        candidate.ai_recommendation = analysis.get("recommendation")
        candidate.ai_summary = analysis.get("reasoning")
        candidate.ai_strengths = analysis.get("strengths", [])
        candidate.ai_weaknesses = analysis.get("weaknesses", [])
        candidate.ai_red_flags = analysis.get("red_flags", [])
        candidate.ai_analysis_data = {
            **analysis,
            "vacancy_text": {
                "title": vacancy_title,
                "description": vacancy_description[:500] + "..." if len(vacancy_description) > 500 else vacancy_description
            }
        }
        from datetime import datetime
        candidate.analyzed_at = datetime.utcnow()

        db.commit()
        db.refresh(candidate)

        logger.info(f"Загружен и проанализирован кандидат {candidate.full_name} по тексту (user={current_user.id})")

        return {
            "status": "success",
            "candidate": candidate.to_dict(),
            "analysis": analysis,
            "message": "Резюме загружено и проанализировано"
        }

    except FileParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка загрузки и анализа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {e}")
