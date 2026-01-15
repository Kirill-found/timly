"""
Excel экспорт для AI анализа резюме v3.0
Обновлённый формат с композитным скорингом (Tier A/B/C)
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
    Создание Excel файла с результатами анализа v3.0

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
    BRAND_PRIMARY = "1E3A5F"  # Deep Navy
    BRAND_ACCENT = "F97316"   # Warm Orange
    HEADER_BG = "1E3A5F"
    LIGHT_BG = "FAF8F5"

    title_font = Font(bold=True, size=18, color="FFFFFF", name="Arial")
    header_font = Font(bold=True, size=11, color="FFFFFF", name="Arial")
    subheader_font = Font(bold=True, size=10, color="1E3A5F", name="Arial")
    normal_font = Font(size=10, color="374151", name="Arial")
    link_font = Font(size=10, color="F97316", underline="single", bold=True)

    header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
    brand_fill = PatternFill(start_color=BRAND_PRIMARY, end_color=BRAND_PRIMARY, fill_type="solid")
    light_fill = PatternFill(start_color=LIGHT_BG, end_color=LIGHT_BG, fill_type="solid")
    accent_fill = PatternFill(start_color=BRAND_ACCENT, end_color=BRAND_ACCENT, fill_type="solid")

    # Стили для Tier (A/B/C)
    tier_styles = {
        'A': {'fill': PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), 'font': Font(bold=True, size=14, color="065F46")},
        'B': {'fill': PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), 'font': Font(bold=True, size=14, color="92400E")},
        'C': {'fill': PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), 'font': Font(bold=True, size=14, color="991B1B")},
    }

    rec_styles = {
        'hire': {'fill': PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), 'font': Font(bold=True, size=10, color="065F46"), 'text': "НАНЯТЬ"},
        'interview': {'fill': PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), 'font': Font(bold=True, size=10, color="92400E"), 'text': "СОБЕСЕДОВАНИЕ"},
        'maybe': {'fill': PatternFill(start_color="FED7AA", end_color="FED7AA", fill_type="solid"), 'font': Font(bold=True, size=10, color="9A3412"), 'text': "ВОЗМОЖНО"},
        'reject': {'fill': PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid"), 'font': Font(bold=True, size=10, color="6B7280"), 'text': "ОТКЛОНИТЬ"}
    }

    confidence_styles = {
        'high': {'fill': PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), 'font': Font(size=10, color="065F46"), 'text': "Высокая"},
        'medium': {'fill': PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), 'font': Font(size=10, color="92400E"), 'text': "Средняя"},
        'low': {'fill': PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), 'font': Font(size=10, color="991B1B"), 'text': "Низкая"},
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
        if isinstance(items, str):
            return items
        return "\n".join([f"• {item}" for item in items if item])

    def safe_get(obj, attr, default="—"):
        """Безопасное получение атрибута"""
        val = getattr(obj, attr, None)
        return val if val is not None else default

    def get_raw(analysis, key, default=None):
        """Получение значения из raw_result JSON"""
        raw = getattr(analysis, 'raw_result', None) or {}
        return raw.get(key, default)

    def get_score(analysis, score_name):
        """Получение оценки 1-5 из raw_result.scores"""
        scores = get_raw(analysis, 'scores', {})
        return scores.get(score_name, 0)

    # ========== ЛИСТ 1: СВОДКА ==========
    summary_ws.merge_cells('A1:L2')
    title_cell = summary_ws.cell(row=1, column=1, value=f"TIMLY | Анализ кандидатов: {vacancy.title}")
    title_cell.font = title_font
    title_cell.fill = brand_fill
    title_cell.alignment = center_align
    summary_ws.row_dimensions[1].height = 25
    summary_ws.row_dimensions[2].height = 25

    summary_ws.merge_cells('A3:L3')
    date_cell = summary_ws.cell(row=3, column=1, value=f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Всего кандидатов: {len(results)}")
    date_cell.font = Font(size=10, color="6B7280", italic=True)
    date_cell.alignment = center_align
    date_cell.fill = light_fill

    # Заголовки v3.0
    summary_headers = [
        ("№", 5), ("Tier", 8), ("Кандидат", 25), ("Контакты", 28),
        ("Релев.", 8), ("Эксп.", 8), ("Траект.", 8), ("Стаб.", 8),
        ("Рекомендация", 16), ("Уверенность", 12), ("Резюме", 40), ("Ссылка", 10)
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

        # Tier (A/B/C)
        tier = get_raw(analysis, 'tier', 'C')
        tier_style = tier_styles.get(tier, tier_styles['C'])
        tier_cell = summary_ws.cell(row=row, column=2, value=tier)
        tier_cell.fill = tier_style['fill']
        tier_cell.font = tier_style['font']
        tier_cell.alignment = center_align

        # Кандидат
        summary_ws.cell(row=row, column=3, value=application.candidate_name or "Не указано").font = subheader_font

        # Контакты
        contacts = []
        if application.candidate_email:
            contacts.append(application.candidate_email)
        if application.candidate_phone:
            contacts.append(application.candidate_phone)
        summary_ws.cell(row=row, column=4, value="\n".join(contacts) if contacts else "—").alignment = left_align

        # Оценки 1-5 (из scores)
        relevance = get_score(analysis, 'relevance')
        expertise = get_score(analysis, 'expertise')
        trajectory = get_score(analysis, 'trajectory')
        stability = get_score(analysis, 'stability')

        for col_idx, score_val in enumerate([relevance, expertise, trajectory, stability], 5):
            score_cell = summary_ws.cell(row=row, column=col_idx, value=score_val or "—")
            score_cell.alignment = center_align
            if isinstance(score_val, int) and score_val >= 4:
                score_cell.font = Font(bold=True, size=11, color="065F46")
            elif isinstance(score_val, int) and score_val <= 2:
                score_cell.font = Font(bold=True, size=11, color="991B1B")
            else:
                score_cell.font = Font(size=11, color="374151")

        # Рекомендация
        rec = get_raw(analysis, 'recommendation') or analysis.recommendation or 'unknown'
        rec_style = rec_styles.get(rec, rec_styles.get('maybe'))
        rec_cell = summary_ws.cell(row=row, column=9, value=rec_style['text'])
        rec_cell.fill = rec_style['fill']
        rec_cell.font = rec_style['font']
        rec_cell.alignment = center_align

        # Уверенность
        confidence = get_raw(analysis, 'confidence', 'medium')
        conf_style = confidence_styles.get(confidence, confidence_styles['medium'])
        conf_cell = summary_ws.cell(row=row, column=10, value=conf_style['text'])
        conf_cell.fill = conf_style['fill']
        conf_cell.font = conf_style['font']
        conf_cell.alignment = center_align

        # Резюме (summary)
        summary_text = get_raw(analysis, 'summary') or get_raw(analysis, 'summary_one_line') or analysis.reasoning or "—"
        summary_cell = summary_ws.cell(row=row, column=11, value=summary_text)
        summary_cell.alignment = left_align
        summary_cell.font = normal_font

        # Ссылка на резюме
        if application.resume_url:
            link_cell = summary_ws.cell(row=row, column=12, value="Открыть")
            link_cell.hyperlink = application.resume_url
            link_cell.font = link_font
            link_cell.alignment = center_align
        else:
            summary_ws.cell(row=row, column=12, value="—").alignment = center_align

        # Границы
        for col in range(1, 13):
            summary_ws.cell(row=row, column=col).border = thin_border
        summary_ws.row_dimensions[row].height = 50

    summary_ws.auto_filter.ref = f"A5:L{len(results) + 5}"

    # ========== ЛИСТ 2: ДЕТАЛЬНЫЙ АНАЛИЗ ==========
    details_ws.merge_cells('A1:I2')
    title_cell = details_ws.cell(row=1, column=1, value=f"TIMLY | Детальный анализ: {vacancy.title}")
    title_cell.font = title_font
    title_cell.fill = brand_fill
    title_cell.alignment = center_align
    details_ws.row_dimensions[1].height = 25
    details_ws.row_dimensions[2].height = 25

    # Ширины колонок
    detail_widths = [5, 25, 8, 16, 35, 35, 30, 35, 35]
    for col, width in enumerate(detail_widths, 1):
        details_ws.column_dimensions[get_column_letter(col)].width = width

    detail_headers = ["№", "Кандидат", "Tier", "Рекомендация", "Плюсы", "Минусы", "Навыки (gaps)", "Вопросы для интервью", "Red Flags"]
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

        # Tier
        tier = get_raw(analysis, 'tier', 'C')
        tier_style = tier_styles.get(tier, tier_styles['C'])
        tier_cell = details_ws.cell(row=row, column=3, value=tier)
        tier_cell.fill = tier_style['fill']
        tier_cell.font = tier_style['font']
        tier_cell.alignment = center_align

        # Рекомендация
        rec = get_raw(analysis, 'recommendation') or analysis.recommendation or 'unknown'
        rec_style = rec_styles.get(rec, rec_styles.get('maybe'))
        rec_cell = details_ws.cell(row=row, column=4, value=rec_style['text'])
        rec_cell.fill = rec_style['fill']
        rec_cell.font = rec_style['font']
        rec_cell.alignment = center_align

        # Плюсы (pros или strengths)
        pros = get_raw(analysis, 'pros') or analysis.strengths or []
        pros_cell = details_ws.cell(row=row, column=5, value=format_list_as_bullets(pros))
        pros_cell.alignment = left_align
        pros_cell.font = normal_font

        # Минусы (cons или weaknesses)
        cons = get_raw(analysis, 'cons') or analysis.weaknesses or []
        cons_cell = details_ws.cell(row=row, column=6, value=format_list_as_bullets(cons))
        cons_cell.alignment = left_align
        cons_cell.font = normal_font

        # Навыки (gaps)
        skills_analysis = get_raw(analysis, 'skills_analysis', {})
        missing_skills = skills_analysis.get('missing', []) if isinstance(skills_analysis, dict) else []
        matching_skills = skills_analysis.get('matching', []) if isinstance(skills_analysis, dict) else []
        match_percent = skills_analysis.get('match_percent', 0) if isinstance(skills_analysis, dict) else 0

        skills_text = f"Совпадение: {match_percent}%\n\n"
        if matching_skills:
            skills_text += "✓ " + ", ".join(matching_skills[:5]) + "\n"
        if missing_skills:
            skills_text += "✗ " + ", ".join(missing_skills[:5])

        skills_cell = details_ws.cell(row=row, column=7, value=skills_text.strip())
        skills_cell.alignment = left_align
        skills_cell.font = normal_font

        # Вопросы для интервью
        interview_questions = get_raw(analysis, 'interview_questions', [])
        questions_cell = details_ws.cell(row=row, column=8, value=format_list_as_bullets(interview_questions))
        questions_cell.alignment = left_align
        questions_cell.font = normal_font

        # Red Flags
        red_flags = get_raw(analysis, 'red_flags') or analysis.red_flags or []
        red_flags_cell = details_ws.cell(row=row, column=9, value=format_list_as_bullets(red_flags) if red_flags else "—")
        red_flags_cell.alignment = left_align
        if red_flags:
            red_flags_cell.font = Font(size=10, color="991B1B")
        else:
            red_flags_cell.font = normal_font

        for col in range(1, 10):
            details_ws.cell(row=row, column=col).border = thin_border
        details_ws.row_dimensions[row].height = 90

    details_ws.auto_filter.ref = f"A4:I{len(results) + 4}"

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

    # Подсчёт статистики v3.0
    total_count = len(results)

    # Tier статистика
    tier_a = len([r for r, _ in results if get_raw(r, 'tier') == 'A'])
    tier_b = len([r for r, _ in results if get_raw(r, 'tier') == 'B'])
    tier_c = len([r for r, _ in results if get_raw(r, 'tier') == 'C' or get_raw(r, 'tier') is None])

    # Рекомендации
    hire_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'hire'])
    interview_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'interview'])
    maybe_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'maybe'])
    reject_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'reject'])

    # Средние оценки
    def avg_score(score_name):
        scores = [get_score(r, score_name) for r, _ in results if get_score(r, score_name)]
        return round(sum(scores) / len(scores), 1) if scores else 0

    avg_relevance = avg_score('relevance')
    avg_expertise = avg_score('expertise')
    avg_trajectory = avg_score('trajectory')
    avg_stability = avg_score('stability')

    # Confidence
    high_conf = len([r for r, _ in results if get_raw(r, 'confidence') == 'high'])
    medium_conf = len([r for r, _ in results if get_raw(r, 'confidence') == 'medium'])
    low_conf = len([r for r, _ in results if get_raw(r, 'confidence') == 'low'])

    stats_data = [
        ("ОБЩИЕ МЕТРИКИ", "", "", ""),
        ("Всего кандидатов", total_count, "", ""),
        ("", "", "", ""),
        ("РАСПРЕДЕЛЕНИЕ ПО TIER", "", "", ""),
        ("Tier A (топ)", tier_a, "Tier B (средние)", tier_b),
        ("Tier C (слабые)", tier_c, "", ""),
        ("", "", "", ""),
        ("РЕКОМЕНДАЦИИ", "", "", ""),
        ("Нанять", hire_count, "Собеседование", interview_count),
        ("Возможно", maybe_count, "Отклонить", reject_count),
        ("", "", "", ""),
        ("СРЕДНИЕ ОЦЕНКИ (1-5)", "", "", ""),
        ("Релевантность", avg_relevance, "Экспертиза", avg_expertise),
        ("Траектория", avg_trajectory, "Стабильность", avg_stability),
        ("", "", "", ""),
        ("УВЕРЕННОСТЬ ОЦЕНКИ", "", "", ""),
        ("Высокая", high_conf, "Средняя", medium_conf),
        ("Низкая", low_conf, "", ""),
    ]

    row = 5
    for data in stats_data:
        for col, val in enumerate(data, 1):
            cell = stats_ws.cell(row=row, column=col, value=val)
            if col in [1, 3]:
                cell.font = subheader_font
            else:
                cell.font = Font(bold=True, size=12, color="F97316")
            cell.alignment = center_align

            if str(val) in ["ОБЩИЕ МЕТРИКИ", "РАСПРЕДЕЛЕНИЕ ПО TIER", "РЕКОМЕНДАЦИИ", "СРЕДНИЕ ОЦЕНКИ (1-5)", "УВЕРЕННОСТЬ ОЦЕНКИ"]:
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
