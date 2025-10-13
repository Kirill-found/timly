"""
Фоновые задачи AI анализа резюме
RQ воркеры для анализа кандидатов
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from rq import get_current_job

from app.database import SessionLocal
from app.services.ai_analyzer import AIAnalyzer
from app.models.application import Application, AnalysisResult
from app.models.vacancy import Vacancy
from app.utils.exceptions import BackgroundJobError, AIAnalysisError

logger = logging.getLogger(__name__)


def run_ai_analysis_batch(
    application_ids: List[str],
    user_id: str,
    force_reanalysis: bool = False
) -> Dict[str, Any]:
    """
    Запуск AI анализа для пакета откликов (для BackgroundTasks)

    Args:
        application_ids: Список ID заявок для анализа
        user_id: ID пользователя
        force_reanalysis: Принудительный повторный анализ

    Returns:
        Dict: Результат выполнения анализа
    """
    # DEBUG: выводим в консоль для отладки
    print(f"[DEBUG] run_ai_analysis_batch STARTED: {len(application_ids)} applications")
    print(f"[DEBUG] user_id={user_id}, force_reanalysis={force_reanalysis}")

    # Создаём новую сессию БД для фоновой задачи
    db = SessionLocal()

    try:
        logger.info(f"Запуск пакетного анализа: {len(application_ids)} заявок для пользователя {user_id}")
        print(f"[DEBUG] Logger info logged")

        ai_analyzer = AIAnalyzer()
        print(f"[DEBUG] AIAnalyzer created")

        results = {
            "processed_applications": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "errors": []
        }

        # Создаём event loop для async операций
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print(f"[DEBUG] Event loop created")

        try:
            for i, application_id in enumerate(application_ids):
                print(f"[DEBUG] Processing application {i+1}/{len(application_ids)}: {application_id}")
                try:
                    # Анализ одной заявки
                    analysis_result = loop.run_until_complete(
                        analyze_single_application_async(
                            application_id,
                            ai_analyzer,
                            db,
                            force_reanalysis
                        )
                    )

                    print(f"[DEBUG] Analysis result: {analysis_result}")

                    if analysis_result:
                        results["successful_analyses"] += 1
                        print(f"[DEBUG] Success! Total successful: {results['successful_analyses']}")
                    else:
                        results["failed_analyses"] += 1
                        print(f"[DEBUG] Failed! Total failed: {results['failed_analyses']}")

                    results["processed_applications"] += 1

                except Exception as e:
                    error_msg = f"Ошибка анализа заявки {application_id}: {e}"
                    logger.error(error_msg)
                    print(f"[DEBUG ERROR] {error_msg}")
                    import traceback
                    traceback.print_exc()
                    results["errors"].append(error_msg)
                    results["failed_analyses"] += 1
        finally:
            loop.close()
            print(f"[DEBUG] Event loop closed")

        logger.info(f"Пакетный анализ завершен: {results}")
        print(f"[DEBUG] BATCH ANALYSIS COMPLETED: {results}")
        return results

    except Exception as e:
        logger.error(f"Критическая ошибка в пакетном анализе: {e}")
        print(f"[DEBUG CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise BackgroundJobError(f"Анализ завершился с ошибкой: {e}")

    finally:
        db.close()


def run_analysis_job(job_id: str, application_ids: List[str], user_id: str):
    """
    Выполнение AI анализа резюме

    Args:
        job_id: ID фоновой задачи
        application_ids: Список ID заявок для анализа
        user_id: ID пользователя

    Returns:
        Dict: Результат выполнения анализа
    """
    db = SessionLocal()
    current_job = get_current_job()

    try:
        logger.info(f"Запуск задачи анализа {job_id}: {len(application_ids)} заявок")

        ai_analyzer = AIAnalyzer()
        results = {
            "processed_applications": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "errors": []
        }

        for i, application_id in enumerate(application_ids):
            try:
                # Обновление прогресса задачи
                if current_job:
                    current_job.meta = {
                        "progress": int((i / len(application_ids)) * 100),
                        "current_application": i + 1,
                        "total_applications": len(application_ids)
                    }
                    current_job.save_meta()

                # Анализ одной заявки
                analysis_result = analyze_single_application(
                    application_id,
                    ai_analyzer,
                    db
                )

                if analysis_result:
                    results["successful_analyses"] += 1
                else:
                    results["failed_analyses"] += 1

                results["processed_applications"] += 1

            except Exception as e:
                error_msg = f"Ошибка анализа заявки {application_id}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed_analyses"] += 1

        # Финальное обновление прогресса
        if current_job:
            current_job.meta = {
                "progress": 100,
                "completed": True,
                "results": results
            }
            current_job.save_meta()

        logger.info(f"Задача анализа {job_id} завершена: {results}")
        return results

    except Exception as e:
        logger.error(f"Критическая ошибка в задаче анализа {job_id}: {e}")
        raise BackgroundJobError(f"Анализ завершился с ошибкой: {e}", job_id=job_id)

    finally:
        db.close()


async def analyze_single_application_async(
    application_id: str,
    ai_analyzer: AIAnalyzer,
    db: Session,
    force_reanalysis: bool = False
) -> bool:
    """
    Анализ одной заявки

    Args:
        application_id: ID заявки
        ai_analyzer: AI анализатор
        db: Сессия БД
        force_reanalysis: Принудительный повторный анализ

    Returns:
        bool: Успех анализа
    """
    try:
        # Получение заявки с вакансией
        application = db.query(Application).join(Vacancy).filter(
            Application.id == application_id
        ).first()

        if not application:
            logger.error(f"Заявка {application_id} не найдена")
            return False

        if not application.resume_data:
            logger.warning(f"Отсутствуют данные резюме для заявки {application_id}")
            return False

        # Проверка существующего анализа
        existing_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.application_id == application_id
        ).first()

        if existing_analysis and not force_reanalysis:
            logger.info(f"Анализ для заявки {application_id} уже существует")
            return True

        if existing_analysis and force_reanalysis:
            logger.info(f"Принудительный повторный анализ для заявки {application_id}")
            db.delete(existing_analysis)
            db.commit()

        # Подготовка данных для анализа
        vacancy_data = {
            "title": application.vacancy.title,
            "description": application.vacancy.description,
            "key_skills": application.vacancy.key_skills,
            "experience": application.vacancy.experience,
            "salary_from": application.vacancy.salary_from,
            "salary_to": application.vacancy.salary_to,
            "currency": application.vacancy.currency
        }

        # Выполнение AI анализа
        ai_result = await ai_analyzer.analyze_resume(
            vacancy_data,
            application.resume_data
        )

        # Проверка результата анализа
        if not ai_result:
            logger.error(f"AI анализ вернул пустой результат для заявки {application_id}")
            return False

        # Сохранение результата анализа
        analysis_result = AnalysisResult(
            application_id=application_id,
            score=ai_result.get("score"),
            skills_match=ai_result.get("skills_match"),
            experience_match=ai_result.get("experience_match"),
            salary_match=ai_result.get("salary_match"),
            strengths=ai_result.get("strengths", []),
            weaknesses=ai_result.get("weaknesses", []),
            red_flags=ai_result.get("red_flags", []),
            recommendation=ai_result.get("recommendation"),
            reasoning=ai_result.get("reasoning"),
            ai_model=ai_result.get("ai_model"),
            ai_tokens_used=ai_result.get("ai_tokens_used"),
            ai_cost_rub=ai_result.get("ai_cost_rub"),
            processing_time_ms=ai_result.get("processing_time_ms")
        )

        db.add(analysis_result)

        # Обновление времени анализа в заявке
        application.analyzed_at = datetime.utcnow()

        db.commit()

        logger.info(
            f"Анализ заявки {application_id} завершен: "
            f"оценка {ai_result.get('score')}, "
            f"рекомендация {ai_result.get('recommendation')}"
        )

        return True

    except AIAnalysisError as e:
        logger.error(f"Ошибка AI анализа для заявки {application_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка анализа заявки {application_id}: {e}")
        return False


def generate_excel_export(export_job_id: str, export_config: Dict[str, Any], user_id: str):
    """
    Генерация Excel экспорта результатов анализа

    Args:
        export_job_id: ID задачи экспорта
        export_config: Конфигурация экспорта
        user_id: ID пользователя

    Returns:
        str: Путь к созданному файлу
    """
    db = SessionLocal()

    try:
        logger.info(f"Запуск генерации Excel экспорта {export_job_id}")

        # TODO: Реализовать создание Excel файла
        # 1. Получение данных для экспорта
        # 2. Создание Excel файла с помощью pandas/openpyxl
        # 3. Сохранение файла в /tmp/exports/
        # 4. Возврат пути к файлу

        vacancy_id = export_config["vacancy_id"]

        # Получение данных
        query = db.query(Application, AnalysisResult, Vacancy).join(
            AnalysisResult, Application.id == AnalysisResult.application_id
        ).join(
            Vacancy, Application.vacancy_id == Vacancy.id
        ).filter(
            Vacancy.id == vacancy_id
        )

        # Применение фильтров
        if export_config.get("min_score"):
            query = query.filter(AnalysisResult.score >= export_config["min_score"])

        if export_config.get("recommendation"):
            query = query.filter(AnalysisResult.recommendation == export_config["recommendation"])

        data = query.all()

        # Создание Excel файла
        import pandas as pd
        import os

        export_data = []
        for app, analysis, vacancy in data:
            row = {
                "Кандидат": app.candidate_name or "Не указано",
                "Email": app.candidate_email or "",
                "Телефон": app.candidate_phone or "",
                "Общая оценка": analysis.score or 0,
                "Соответствие навыков": analysis.skills_match or 0,
                "Соответствие опыта": analysis.experience_match or 0,
                "Рекомендация": analysis.recommendation or "",
                "Сильные стороны": "; ".join(analysis.strengths or []),
                "Слабые стороны": "; ".join(analysis.weaknesses or []),
                "Красные флаги": "; ".join(analysis.red_flags or []),
                "Обоснование": analysis.reasoning or "",
                "Дата анализа": analysis.created_at.strftime("%d.%m.%Y %H:%M") if analysis.created_at else ""
            }
            export_data.append(row)

        df = pd.DataFrame(export_data)

        # Создание директории для экспортов
        export_dir = "/tmp/exports"
        os.makedirs(export_dir, exist_ok=True)

        # Сохранение файла
        file_path = f"{export_dir}/{export_job_id}.xlsx"
        df.to_excel(file_path, index=False, engine='openpyxl')

        logger.info(f"Excel экспорт {export_job_id} создан: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Ошибка создания Excel экспорта {export_job_id}: {e}")
        raise BackgroundJobError(f"Ошибка экспорта: {e}", job_id=export_job_id)

    finally:
        db.close()


def cleanup_old_analysis_results(days_old: int = 30):
    """
    Очистка старых результатов анализа

    Args:
        days_old: Возраст в днях для удаления

    Returns:
        int: Количество удаленных записей
    """
    db = SessionLocal()

    try:
        # TODO: Реализовать очистку старых анализов
        # для освобождения места в БД

        deleted_count = 0
        logger.info(f"Очистка анализов старше {days_old} дней: удалено {deleted_count}")

        return deleted_count

    except Exception as e:
        logger.error(f"Ошибка очистки старых анализов: {e}")
        raise

    finally:
        db.close()