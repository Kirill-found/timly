"""
Excel экспорт для AI анализа резюме v2.0
Улучшенное форматирование с 3 листами: Сводка, Детальный анализ, Статистика
"""
from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import tempfile


def create_excel_export(
    vacancy,
    results: list,
    recommendation_filter: Optional[str] = None
) -> str:
    """
    Создание Excel файла с результатами анализа v2.0

    Returns:
        str: путь к временному файлу
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.formatting.rule import ColorScaleRule
    from openpyxl.utils import get_column_letter

    # ========== СОЗДАНИЕ КНИГИ ==========
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    summary_ws = wb.create_sheet("Сводка", 0)
    details_ws = wb.create_sheet("Детальный анализ", 1)
    stats_ws = wb.create_sheet("Статистика", 2)

    # ========== СТИЛИ ==========
    BRAND_PRIMARY = "6366F1"
    HEADER_BG = "4F46E5"
    LIGHT_BG = "F3F4F6"

    title_font = Font(bold=True, size=18, color="FFFFFF", name="Arial")
    header_font = Font(bold=True, size=11, color="FFFFFF", name="Arial")
    subheader_font = Font(bold=True, size=10, color="374151", name="Arial")
    normal_font = Font(size=10, color="374151", name="Arial")
    link_font = Font(size=10, color="2563EB", underline="single")

    header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
    brand_fill = PatternFill(start_color=BRAND_PRIMARY, end_color=BRAND_PRIMARY, fill_type="solid")
    light_fill = PatternFill(start_color=LIGHT_BG, end_color=LIGHT_BG, fill_type="solid")

    rec_styles = {
        'hire': {'fill': PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), 'font': Font(bold=True, size=10, color="065F46"), 'text': "НАНЯТЬ"},
        'interview': {'fill': PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), 'font': Font(bold=True, size=10, color="92400E"), 'text': "СОБЕСЕДОВАНИЕ"},
        'maybe': {'fill': PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), 'font': Font(bold=True, size=10, color="991B1B"), 'text': "ВОЗМОЖНО"},
        'reject': {'fill': PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid"), 'font': Font(bold=True, size=10, color="6B7280"), 'text': "ОТКЛОНИТЬ"}
    }

    career_styles = {
        'growth': {'fill': PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), 'font': Font(bold=True, size=10, color="065F46"), 'text': "Рост"},
        'stable': {'fill': PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), 'font': Font(bold=True, size=10, color="92400E"), 'text': "Стабильно"},
        'decline': {'fill': PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), 'font': Font(bold=True, size=10, color="991B1B"), 'text': "Снижение"},
        'unknown': {'fill': PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid"), 'font': Font(size=10, color="6B7280"), 'text': "Н/Д"}
    }

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )

    def format_list_as_bullets(items):
        """Форматирует список в строку с буллетами"""
        if not items:
            return "—"
        return "\n".join([f"• {item}" for item in items if item])

    def safe_get(obj, attr, default="—"):
        """Безопасное получение атрибута"""
        val = getattr(obj, attr, None)
        return val if val is not None else default

    # ========== ЛИСТ 1: СВОДКА ==========
    summary_ws.merge_cells('A1:K2')
    title_cell = summary_ws.cell(row=1, column=1, value=f"TIMLY | Анализ кандидатов: {vacancy.title}")
    title_cell.font = title_font
    title_cell.fill = brand_fill
    title_cell.alignment = center_align
    summary_ws.row_dimensions[1].height = 25
    summary_ws.row_dimensions[2].height = 25

    summary_ws.merge_cells('A3:K3')
    date_cell = summary_ws.cell(row=3, column=1, value=f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Всего кандидатов: {len(results)}")
    date_cell.font = Font(size=10, color="6B7280", italic=True)
    date_cell.alignment = center_align
    date_cell.fill = light_fill

    # Заголовки с фиксированными ширинами
    summary_headers = [
        ("№", 5), ("Кандидат", 25), ("Контакты", 30), ("Оценка", 10),
        ("Навыки %", 10), ("Опыт %", 10), ("Карьера", 15),
        ("Рекомендация", 18), ("Зарплата", 15), ("Ключевое", 40), ("Резюме", 12)
    ]

    for col, (header, width) in enumerate(summary_headers, 1):
        cell = summary_ws.cell(row=5, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
        summary_ws.column_dimensions[get_column_letter(col)].width = width

    summary_ws.row_dimensions[5].height = 25
    summary_ws.freeze_panes = "A6"

    # Данные сводки
    for idx, (analysis, application) in enumerate(results, 1):
        row = idx + 5

        summary_ws.cell(row=row, column=1, value=idx).alignment = center_align
        summary_ws.cell(row=row, column=2, value=application.candidate_name or "Не указано").font = subheader_font

        # Контакты
        contacts = []
        if application.candidate_email:
            contacts.append(application.candidate_email)
        if application.candidate_phone:
            contacts.append(application.candidate_phone)
        summary_ws.cell(row=row, column=3, value="\n".join(contacts) if contacts else "—").alignment = left_align

        # Оценка
        score_cell = summary_ws.cell(row=row, column=4, value=analysis.score or 0)
        score_cell.alignment = center_align
        score_cell.font = Font(bold=True, size=12)

        # Навыки и опыт
        summary_ws.cell(row=row, column=5, value=analysis.skills_match or 0).alignment = center_align
        summary_ws.cell(row=row, column=6, value=analysis.experience_match or 0).alignment = center_align

        # Карьерная траектория
        career = safe_get(analysis, 'career_trajectory', 'unknown')
        career_style = career_styles.get(career, career_styles['unknown'])
        career_cell = summary_ws.cell(row=row, column=7, value=career_style['text'])
        career_cell.fill = career_style['fill']
        career_cell.font = career_style['font']
        career_cell.alignment = center_align

        # Рекомендация
        rec = analysis.recommendation or 'unknown'
        rec_style = rec_styles.get(rec, rec_styles.get('maybe'))
        rec_cell = summary_ws.cell(row=row, column=8, value=rec_style['text'])
        rec_cell.fill = rec_style['fill']
        rec_cell.font = rec_style['font']
        rec_cell.alignment = center_align

        # Зарплата
        salary_map = {'match': 'Совпадает', 'higher': 'Выше', 'lower': 'Ниже', 'unknown': 'Н/Д'}
        summary_ws.cell(row=row, column=9, value=salary_map.get(analysis.salary_match, 'Н/Д')).alignment = center_align

        # Ключевое обоснование
        reasoning_cell = summary_ws.cell(row=row, column=10, value=analysis.reasoning or "—")
        reasoning_cell.alignment = left_align
        reasoning_cell.font = normal_font

        # Ссылка на резюме
        if application.resume_url:
            link_cell = summary_ws.cell(row=row, column=11, value="Открыть")
            link_cell.hyperlink = application.resume_url
            link_cell.font = link_font
            link_cell.alignment = center_align
        else:
            summary_ws.cell(row=row, column=11, value="—").alignment = center_align

        # Границы
        for col in range(1, 12):
            summary_ws.cell(row=row, column=col).border = thin_border
        summary_ws.row_dimensions[row].height = 45

    # Условное форматирование для оценок
    score_rule = ColorScaleRule(
        start_type='num', start_value=0, start_color='FEE2E2',
        mid_type='num', mid_value=60, mid_color='FEF3C7',
        end_type='num', end_value=100, end_color='D1FAE5'
    )
    summary_ws.conditional_formatting.add(f"D6:D{len(results) + 5}", score_rule)
    summary_ws.conditional_formatting.add(f"E6:E{len(results) + 5}", score_rule)
    summary_ws.conditional_formatting.add(f"F6:F{len(results) + 5}", score_rule)
    summary_ws.auto_filter.ref = f"A5:K{len(results) + 5}"

    # ========== ЛИСТ 2: ДЕТАЛЬНЫЙ АНАЛИЗ ==========
    details_ws.merge_cells('A1:H2')
    title_cell = details_ws.cell(row=1, column=1, value=f"TIMLY | Детальный анализ: {vacancy.title}")
    title_cell.font = title_font
    title_cell.fill = brand_fill
    title_cell.alignment = center_align
    details_ws.row_dimensions[1].height = 25
    details_ws.row_dimensions[2].height = 25

    # Ширины колонок
    detail_widths = [5, 25, 12, 18, 35, 35, 35, 35]
    for col, width in enumerate(detail_widths, 1):
        details_ws.column_dimensions[get_column_letter(col)].width = width

    detail_headers = ["№", "Кандидат", "Оценка", "Рекомендация", "Сильные стороны", "Слабые стороны", "Skill Gaps", "Вопросы для интервью"]
    for col, header in enumerate(detail_headers, 1):
        cell = details_ws.cell(row=4, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    details_ws.row_dimensions[4].height = 25
    details_ws.freeze_panes = "A5"

    for idx, (analysis, application) in enumerate(results, 1):
        row = idx + 4

        details_ws.cell(row=row, column=1, value=idx).alignment = center_align
        name_cell = details_ws.cell(row=row, column=2, value=application.candidate_name or "Не указано")
        name_cell.font = subheader_font
        name_cell.alignment = left_align

        score_cell = details_ws.cell(row=row, column=3, value=analysis.score or 0)
        score_cell.alignment = center_align
        score_cell.font = Font(bold=True, size=14)

        rec = analysis.recommendation or 'unknown'
        rec_style = rec_styles.get(rec, rec_styles.get('maybe'))
        rec_cell = details_ws.cell(row=row, column=4, value=rec_style['text'])
        rec_cell.fill = rec_style['fill']
        rec_cell.font = rec_style['font']
        rec_cell.alignment = center_align

        # Сильные стороны с буллетами
        strengths_cell = details_ws.cell(row=row, column=5, value=format_list_as_bullets(analysis.strengths or []))
        strengths_cell.alignment = left_align
        strengths_cell.font = normal_font

        # Слабые стороны с буллетами
        weaknesses_cell = details_ws.cell(row=row, column=6, value=format_list_as_bullets(analysis.weaknesses or []))
        weaknesses_cell.alignment = left_align
        weaknesses_cell.font = normal_font

        # Skill Gaps (новое поле v2.0)
        skill_gaps = safe_get(analysis, 'skill_gaps', [])
        skill_gaps_text = format_list_as_bullets(skill_gaps) if isinstance(skill_gaps, list) else "—"
        skill_gaps_cell = details_ws.cell(row=row, column=7, value=skill_gaps_text)
        skill_gaps_cell.alignment = left_align
        skill_gaps_cell.font = normal_font

        # Вопросы для интервью (новое поле v2.0)
        interview_questions = safe_get(analysis, 'interview_questions', [])
        questions_text = format_list_as_bullets(interview_questions) if isinstance(interview_questions, list) else "—"
        questions_cell = details_ws.cell(row=row, column=8, value=questions_text)
        questions_cell.alignment = left_align
        questions_cell.font = normal_font

        for col in range(1, 9):
            details_ws.cell(row=row, column=col).border = thin_border
        details_ws.row_dimensions[row].height = 80

    details_ws.conditional_formatting.add(f"C5:C{len(results) + 4}", score_rule)
    details_ws.auto_filter.ref = f"A4:H{len(results) + 4}"

    # ========== ЛИСТ 3: СТАТИСТИКА ==========
    stats_ws.merge_cells('A1:D2')
    title_cell = stats_ws.cell(row=1, column=1, value="TIMLY | Статистика анализа")
    title_cell.font = title_font
    title_cell.fill = brand_fill
    title_cell.alignment = center_align
    stats_ws.row_dimensions[1].height = 25
    stats_ws.row_dimensions[2].height = 25

    stats_ws.merge_cells('A3:D3')
    vacancy_cell = stats_ws.cell(row=3, column=1, value=f"Вакансия: {vacancy.title}")
    vacancy_cell.font = subheader_font
    vacancy_cell.alignment = center_align
    vacancy_cell.fill = light_fill

    for col in range(1, 5):
        stats_ws.column_dimensions[get_column_letter(col)].width = 25

    # Подсчёт статистики
    total_count = len(results)
    hire_count = len([r for r, _ in results if r.recommendation == 'hire'])
    interview_count = len([r for r, _ in results if r.recommendation == 'interview'])
    maybe_count = len([r for r, _ in results if r.recommendation == 'maybe'])
    reject_count = len([r for r, _ in results if r.recommendation == 'reject'])

    scores = [r.score for r, _ in results if r.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score_val = min(scores) if scores else 0

    growth_count = len([r for r, _ in results if safe_get(r, 'career_trajectory') == 'growth'])
    stable_count = len([r for r, _ in results if safe_get(r, 'career_trajectory') == 'stable'])
    decline_count = len([r for r, _ in results if safe_get(r, 'career_trajectory') == 'decline'])

    stats_data = [
        ("ОБЩИЕ МЕТРИКИ", "", "", ""),
        ("Всего кандидатов", total_count, "Средний балл", f"{avg_score:.1f}"),
        ("Макс. балл", max_score, "Мин. балл", min_score_val),
        ("", "", "", ""),
        ("РЕКОМЕНДАЦИИ", "", "", ""),
        ("Нанять", hire_count, "Собеседование", interview_count),
        ("Возможно", maybe_count, "Отклонить", reject_count),
        ("", "", "", ""),
        ("КАРЬЕРНАЯ ДИНАМИКА", "", "", ""),
        ("Рост", growth_count, "Стабильно", stable_count),
        ("Снижение", decline_count, "", ""),
    ]

    row = 5
    for data in stats_data:
        for col, val in enumerate(data, 1):
            cell = stats_ws.cell(row=row, column=col, value=val)
            if col in [1, 3]:
                cell.font = subheader_font
            else:
                cell.font = Font(bold=True, size=12, color="4F46E5")
            cell.alignment = center_align

            if str(val) in ["ОБЩИЕ МЕТРИКИ", "РЕКОМЕНДАЦИИ", "КАРЬЕРНАЯ ДИНАМИКА"]:
                stats_ws.merge_cells(f'A{row}:D{row}')
                cell.font = Font(bold=True, size=12, color="FFFFFF")
                cell.fill = brand_fill
                break
        stats_ws.row_dimensions[row].height = 25
        row += 1

    # ========== СОХРАНЕНИЕ ==========
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    temp_file.close()

    return temp_file.name
