"""
Excel экспорт для AI анализа резюме v5.0
Редизайн под критику HR-директора

Ключевые изменения:
- Светофор 🟢/🟡/🔴 вместо абстрактных Tier
- SCORE (0-100) виден сразу
- ОПЫТ, ПОЗИЦИЯ, ЗП — ключевые данные
- Verified/Unverified навыки
- Red Flags колонка
- Убраны аббревиатуры
- Дашборд: 3 цифры вместо 15 графиков

HR-принцип: "Мне не нужны 15 графиков. Мне нужно 3 цифры."
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
    Создание Excel файла с результатами анализа v5.0
    HR-ориентированный дизайн

    Returns:
        str: путь к временному файлу
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    # ========== СОЗДАНИЕ КНИГИ ==========
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    candidates_ws = wb.create_sheet("Кандидаты", 0)
    details_ws = wb.create_sheet("Детали", 1)
    dashboard_ws = wb.create_sheet("Сводка", 2)

    # ========== ЦВЕТОВАЯ ПАЛИТРА ==========
    COLORS = {
        'primary': '1A1A2E',
        'success': '16A34A',      # Green
        'warning': 'D97706',      # Amber/Yellow
        'danger': 'DC2626',       # Red
        'muted': '6B7280',
        'light_bg': 'F8FAFC',
        'white': 'FFFFFF',
        'border': 'E2E8F0',

        # Светофор
        'green_bg': 'DCFCE7',
        'green_text': '166534',
        'yellow_bg': 'FEF3C7',
        'yellow_text': '92400E',
        'red_bg': 'FEE2E2',
        'red_text': 'DC2626',
    }

    # ========== ТИПОГРАФИКА ==========
    FONTS = {
        'title': Font(name='Calibri', size=20, bold=True, color=COLORS['primary']),
        'subtitle': Font(name='Calibri', size=12, color=COLORS['muted']),
        'header': Font(name='Calibri', size=10, bold=True, color=COLORS['white']),
        'subheader': Font(name='Calibri', size=11, bold=True, color=COLORS['primary']),
        'body': Font(name='Calibri', size=10, color='374151'),
        'body_small': Font(name='Calibri', size=9, color=COLORS['muted']),
        'link': Font(name='Calibri', size=10, color='2563EB', underline='single'),
        'score_large': Font(name='Calibri', size=14, bold=True),
        'metric_value': Font(name='Calibri', size=36, bold=True, color=COLORS['primary']),
        'metric_label': Font(name='Calibri', size=11, color=COLORS['muted']),
    }

    # ========== СТИЛИ ==========
    header_fill = PatternFill(start_color=COLORS['primary'], end_color=COLORS['primary'], fill_type="solid")
    light_fill = PatternFill(start_color=COLORS['light_bg'], end_color=COLORS['light_bg'], fill_type="solid")
    white_fill = PatternFill(start_color=COLORS['white'], end_color=COLORS['white'], fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color=COLORS['border']),
        right=Side(style='thin', color=COLORS['border']),
        top=Side(style='thin', color=COLORS['border']),
        bottom=Side(style='thin', color=COLORS['border'])
    )

    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    left_top = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # ========== ХЕЛПЕРЫ ==========
    def get_raw(analysis, key, default=None):
        raw = getattr(analysis, 'raw_result', None) or {}
        return raw.get(key, default)

    def get_nested(analysis, *keys, default=None):
        """Получение вложенных ключей"""
        raw = getattr(analysis, 'raw_result', None) or {}
        result = raw
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return default
        return result if result is not None else default

    def format_bullets(items, max_items=5):
        if not items:
            return "—"
        if isinstance(items, str):
            return items
        items = items[:max_items]
        return "\n".join([f"• {item}" for item in items if item])

    def get_verdict_style(verdict):
        """Стиль для светофора"""
        styles = {
            'GREEN': (COLORS['green_bg'], COLORS['green_text'], '🟢'),
            'YELLOW': (COLORS['yellow_bg'], COLORS['yellow_text'], '🟡'),
            'RED': (COLORS['red_bg'], COLORS['red_text'], '🔴'),
        }
        return styles.get(verdict, styles['YELLOW'])

    def apply_cell_style(cell, font=None, fill=None, alignment=None, border=None):
        if font:
            cell.font = font
        if fill:
            cell.fill = fill
        if alignment:
            cell.alignment = alignment
        if border:
            cell.border = border

    # ========== ПОДСЧЁТ СТАТИСТИКИ ==========
    total = len(results)
    green_count = len([r for r, _ in results if get_raw(r, 'verdict') == 'GREEN'])
    yellow_count = len([r for r, _ in results if get_raw(r, 'verdict') == 'YELLOW'])
    red_count = total - green_count - yellow_count

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 1: КАНДИДАТЫ (Быстрое решение за 5 секунд)
    # ═══════════════════════════════════════════════════════════════
    ws = candidates_ws

    # Ширины колонок: Светофор, Score, Имя, Опыт, Позиция, ЗП, Резюме, Ссылка
    col_widths = {'A': 4, 'B': 8, 'C': 24, 'D': 8, 'E': 22, 'F': 12, 'G': 35, 'H': 10}
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    # --- HEADER ---
    ws.merge_cells('A1:H1')
    title_cell = ws.cell(row=1, column=1, value=f"TIMLY | {vacancy.title}")
    apply_cell_style(title_cell, font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:H2')
    summary_text = f"🟢 Звонить: {green_count}  │  🟡 Рассмотреть: {yellow_count}  │  🔴 Отклонить: {red_count}  │  Всего: {total}"
    ws.cell(row=2, column=1, value=summary_text)
    apply_cell_style(ws.cell(row=2, column=1), font=FONTS['subtitle'], alignment=center, fill=light_fill)
    ws.row_dimensions[2].height = 22

    ws.row_dimensions[3].height = 8

    # Table headers
    headers = ['', 'SCORE', 'КАНДИДАТ', 'ОПЫТ', 'ПОЗИЦИЯ', 'ЗП ОЖ.', 'ВЕРДИКТ', 'ССЫЛКА']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        apply_cell_style(cell, font=FONTS['header'], fill=header_fill, alignment=center, border=thin_border)
    ws.row_dimensions[4].height = 26
    ws.freeze_panes = 'A5'

    # Сортировка: GREEN первые, потом YELLOW, потом RED
    def verdict_sort_key(item):
        verdict = get_raw(item[0], 'verdict', 'RED')
        return {'GREEN': 0, 'YELLOW': 1, 'RED': 2}.get(verdict, 2)

    sorted_results = sorted(results, key=verdict_sort_key)

    for idx, (analysis, application) in enumerate(sorted_results, 1):
        row = idx + 4
        verdict = get_raw(analysis, 'verdict', 'YELLOW')
        verdict_bg, verdict_text, verdict_emoji = get_verdict_style(verdict)
        rank_score = get_raw(analysis, 'rank_score', 0) or getattr(analysis, 'rank_score', 0) or 0

        row_fill = white_fill if idx % 2 == 1 else light_fill

        # Светофор (эмодзи)
        cell = ws.cell(row=row, column=1, value=verdict_emoji)
        verdict_fill = PatternFill(start_color=verdict_bg, end_color=verdict_bg, fill_type="solid")
        apply_cell_style(cell, font=Font(name='Calibri', size=14), fill=verdict_fill, alignment=center, border=thin_border)

        # SCORE
        cell = ws.cell(row=row, column=2, value=rank_score)
        score_color = COLORS['success'] if rank_score >= 75 else (COLORS['warning'] if rank_score >= 50 else COLORS['danger'])
        apply_cell_style(cell, font=Font(name='Calibri', size=12, bold=True, color=score_color),
                        fill=row_fill, alignment=center, border=thin_border)

        # КАНДИДАТ
        name = application.candidate_name or "Не указано"
        cell = ws.cell(row=row, column=3, value=name)
        apply_cell_style(cell, font=FONTS['subheader'], fill=row_fill, alignment=left, border=thin_border)

        # ОПЫТ (лет)
        exp_summary = get_raw(analysis, 'experience_summary', {})
        total_years = exp_summary.get('total_years', 0) if isinstance(exp_summary, dict) else 0
        cell = ws.cell(row=row, column=4, value=f"{total_years} лет" if total_years else "—")
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=center, border=thin_border)

        # ПОЗИЦИЯ
        last_position = exp_summary.get('last_position', '') if isinstance(exp_summary, dict) else ''
        last_company = exp_summary.get('last_company', '') if isinstance(exp_summary, dict) else ''
        position_text = last_position[:25] + "..." if len(last_position) > 25 else last_position
        if last_company:
            position_text += f"\n@ {last_company[:20]}"
        cell = ws.cell(row=row, column=5, value=position_text or "—")
        apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=left, border=thin_border)

        # ЗП ОЖИДАНИЯ
        salary_analysis = get_raw(analysis, 'salary_analysis', {})
        candidate_salary = salary_analysis.get('candidate_net', 0) if isinstance(salary_analysis, dict) else 0
        if candidate_salary:
            salary_text = f"{candidate_salary // 1000}k"
            salary_match = salary_analysis.get('match', 'unknown')
            if salary_match == 'above':
                salary_text += " ⬆️"
            elif salary_match == 'below':
                salary_text += " ⬇️"
        else:
            salary_text = "—"
        cell = ws.cell(row=row, column=6, value=salary_text)
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=center, border=thin_border)

        # ВЕРДИКТ (одна строка)
        verdict_reason = get_raw(analysis, 'verdict_reason', '') or get_raw(analysis, 'summary_for_recruiter', '') or ''
        cell = ws.cell(row=row, column=7, value=verdict_reason[:60] + "..." if len(verdict_reason) > 60 else verdict_reason)
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left, border=thin_border)

        # ССЫЛКА
        if application.resume_url:
            cell = ws.cell(row=row, column=8, value="Открыть →")
            cell.hyperlink = application.resume_url
            apply_cell_style(cell, font=FONTS['link'], fill=row_fill, alignment=center, border=thin_border)
        else:
            cell = ws.cell(row=row, column=8, value="—")
            apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=center, border=thin_border)

        ws.row_dimensions[row].height = 38

    ws.auto_filter.ref = f"A4:H{len(results) + 4}"

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 2: ДЕТАЛИ (Подготовка к интервью)
    # ═══════════════════════════════════════════════════════════════
    ws = details_ws

    # Колонки: №, Кандидат, Светофор, Score, Навыки ✓, Навыки ?, Навыки ✗, Red Flags, Плюсы, Минусы, Вопросы
    col_widths = {
        'A': 4, 'B': 20, 'C': 4, 'D': 7,
        'E': 30, 'F': 25, 'G': 20,
        'H': 20, 'I': 30, 'J': 30, 'K': 35
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    # Header
    ws.merge_cells('A1:K1')
    ws.cell(row=1, column=1, value=f"TIMLY | Детальный анализ: {vacancy.title}")
    apply_cell_style(ws.cell(row=1, column=1), font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 30

    ws.row_dimensions[2].height = 8

    # Table headers — БЕЗ АББРЕВИАТУР!
    headers = ['№', 'КАНДИДАТ', '', 'SCORE',
               'НАВЫКИ ✓', 'НАВЫКИ ?', 'НАВЫКИ ✗',
               'RED FLAGS', 'ПЛЮСЫ', 'МИНУСЫ', 'ВОПРОСЫ ДЛЯ ИНТЕРВЬЮ']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        apply_cell_style(cell, font=FONTS['header'], fill=header_fill, alignment=center, border=thin_border)
    ws.row_dimensions[3].height = 26
    ws.freeze_panes = 'A4'

    for idx, (analysis, application) in enumerate(sorted_results, 1):
        row = idx + 3
        verdict = get_raw(analysis, 'verdict', 'YELLOW')
        verdict_bg, verdict_text, verdict_emoji = get_verdict_style(verdict)
        rank_score = get_raw(analysis, 'rank_score', 0) or getattr(analysis, 'rank_score', 0) or 0

        row_fill = white_fill if idx % 2 == 1 else light_fill

        # №
        cell = ws.cell(row=row, column=1, value=idx)
        apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=center, border=thin_border)

        # Кандидат
        cell = ws.cell(row=row, column=2, value=application.candidate_name or "Не указано")
        apply_cell_style(cell, font=FONTS['subheader'], fill=row_fill, alignment=left, border=thin_border)

        # Светофор
        cell = ws.cell(row=row, column=3, value=verdict_emoji)
        verdict_fill = PatternFill(start_color=verdict_bg, end_color=verdict_bg, fill_type="solid")
        apply_cell_style(cell, font=Font(name='Calibri', size=12), fill=verdict_fill, alignment=center, border=thin_border)

        # Score
        cell = ws.cell(row=row, column=4, value=rank_score)
        score_color = COLORS['success'] if rank_score >= 75 else (COLORS['warning'] if rank_score >= 50 else COLORS['danger'])
        apply_cell_style(cell, font=Font(name='Calibri', size=11, bold=True, color=score_color),
                        fill=row_fill, alignment=center, border=thin_border)

        # Навыки анализ
        skills_analysis = get_raw(analysis, 'skills_analysis', {})

        # Навыки ✓ (verified)
        verified = skills_analysis.get('verified', []) if isinstance(skills_analysis, dict) else []
        cell = ws.cell(row=row, column=5, value=format_bullets(verified, 4))
        apply_cell_style(cell, font=Font(name='Calibri', size=9, color=COLORS['success']),
                        fill=row_fill, alignment=left_top, border=thin_border)

        # Навыки ? (unverified)
        unverified = skills_analysis.get('unverified', []) if isinstance(skills_analysis, dict) else []
        cell = ws.cell(row=row, column=6, value=format_bullets(unverified, 3))
        apply_cell_style(cell, font=Font(name='Calibri', size=9, color=COLORS['warning']),
                        fill=row_fill, alignment=left_top, border=thin_border)

        # Навыки ✗ (missing)
        missing = skills_analysis.get('missing', []) if isinstance(skills_analysis, dict) else []
        cell = ws.cell(row=row, column=7, value=format_bullets(missing, 3))
        apply_cell_style(cell, font=Font(name='Calibri', size=9, color=COLORS['danger']),
                        fill=row_fill, alignment=left_top, border=thin_border)

        # Red Flags
        red_flags = get_raw(analysis, 'red_flags', [])
        yellow_flags = get_raw(analysis, 'yellow_flags', [])
        all_flags = (red_flags or []) + (yellow_flags or [])
        cell = ws.cell(row=row, column=8, value=format_bullets(all_flags, 3) if all_flags else "—")
        flag_font = Font(name='Calibri', size=9, color=COLORS['danger']) if red_flags else Font(name='Calibri', size=9, color=COLORS['warning'])
        apply_cell_style(cell, font=flag_font, fill=row_fill, alignment=left_top, border=thin_border)

        # Плюсы
        pros = get_raw(analysis, 'pros', []) or getattr(analysis, 'strengths', []) or []
        cell = ws.cell(row=row, column=9, value=format_bullets(pros, 4))
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left_top, border=thin_border)

        # Минусы
        cons = get_raw(analysis, 'cons', []) or getattr(analysis, 'weaknesses', []) or []
        cell = ws.cell(row=row, column=10, value=format_bullets(cons, 4))
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left_top, border=thin_border)

        # Вопросы для интервью
        questions = get_raw(analysis, 'interview_questions', [])
        cell = ws.cell(row=row, column=11, value=format_bullets(questions, 3))
        apply_cell_style(cell, font=Font(name='Calibri', size=10, color=COLORS['primary']),
                        fill=row_fill, alignment=left_top, border=thin_border)

        ws.row_dimensions[row].height = 90

    ws.auto_filter.ref = f"A3:K{len(results) + 3}"

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 3: СВОДКА (3 цифры для руководителя)
    # ═══════════════════════════════════════════════════════════════
    ws = dashboard_ws

    # "Мне не нужны 15 графиков. Мне нужно 3 цифры."
    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 20

    # Header
    ws.merge_cells('A1:D1')
    ws.cell(row=1, column=1, value=f"TIMLY | {vacancy.title}")
    apply_cell_style(ws.cell(row=1, column=1), font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 35

    ws.merge_cells('A2:D2')
    ws.cell(row=2, column=1, value=f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    apply_cell_style(ws.cell(row=2, column=1), font=FONTS['subtitle'], alignment=center, fill=light_fill)
    ws.row_dimensions[2].height = 25

    ws.row_dimensions[3].height = 20

    # === 3 ГЛАВНЫЕ МЕТРИКИ ===
    ws.row_dimensions[4].height = 70
    ws.row_dimensions[5].height = 30

    # 🟢 Звонить сегодня
    cell = ws.cell(row=4, column=1, value=green_count)
    apply_cell_style(cell, font=Font(name='Calibri', size=48, bold=True, color=COLORS['success']),
                    alignment=center, fill=white_fill, border=thin_border)
    cell = ws.cell(row=5, column=1, value="🟢 ЗВОНИТЬ")
    apply_cell_style(cell, font=Font(name='Calibri', size=12, bold=True, color=COLORS['success']),
                    alignment=center, fill=PatternFill(start_color=COLORS['green_bg'], fill_type="solid"), border=thin_border)

    # 🟡 Рассмотреть
    cell = ws.cell(row=4, column=2, value=yellow_count)
    apply_cell_style(cell, font=Font(name='Calibri', size=48, bold=True, color=COLORS['warning']),
                    alignment=center, fill=white_fill, border=thin_border)
    cell = ws.cell(row=5, column=2, value="🟡 РАССМОТРЕТЬ")
    apply_cell_style(cell, font=Font(name='Calibri', size=12, bold=True, color=COLORS['warning']),
                    alignment=center, fill=PatternFill(start_color=COLORS['yellow_bg'], fill_type="solid"), border=thin_border)

    # 🔴 Отклонить
    cell = ws.cell(row=4, column=3, value=red_count)
    apply_cell_style(cell, font=Font(name='Calibri', size=48, bold=True, color=COLORS['danger']),
                    alignment=center, fill=white_fill, border=thin_border)
    cell = ws.cell(row=5, column=3, value="🔴 ОТКЛОНИТЬ")
    apply_cell_style(cell, font=Font(name='Calibri', size=12, bold=True, color=COLORS['danger']),
                    alignment=center, fill=PatternFill(start_color=COLORS['red_bg'], fill_type="solid"), border=thin_border)

    # ВСЕГО
    cell = ws.cell(row=4, column=4, value=total)
    apply_cell_style(cell, font=Font(name='Calibri', size=48, bold=True, color=COLORS['primary']),
                    alignment=center, fill=white_fill, border=thin_border)
    cell = ws.cell(row=5, column=4, value="ВСЕГО")
    apply_cell_style(cell, font=Font(name='Calibri', size=12, bold=True, color=COLORS['muted']),
                    alignment=center, fill=light_fill, border=thin_border)

    ws.row_dimensions[6].height = 25

    # === ТОП-5 КАНДИДАТОВ (Зелёные) ===
    ws.merge_cells('A7:D7')
    cell = ws.cell(row=7, column=1, value="🟢 ТОП КАНДИДАТЫ (звонить первыми)")
    apply_cell_style(cell, font=FONTS['header'], alignment=center, fill=header_fill)
    ws.row_dimensions[7].height = 28

    green_candidates = [r for r in sorted_results if get_raw(r[0], 'verdict') == 'GREEN'][:5]

    if green_candidates:
        for idx, (analysis, application) in enumerate(green_candidates, 1):
            row_num = 7 + idx
            ws.merge_cells(f'A{row_num}:B{row_num}')

            name = application.candidate_name or "Не указано"
            score = get_raw(analysis, 'rank_score', 0) or getattr(analysis, 'rank_score', 0)
            cell = ws.cell(row=row_num, column=1, value=f"{idx}. {name} (Score: {score})")
            apply_cell_style(cell, font=FONTS['subheader'], alignment=left, fill=white_fill, border=thin_border)

            ws.merge_cells(f'C{row_num}:D{row_num}')
            verdict_reason = get_raw(analysis, 'verdict_reason', '') or get_raw(analysis, 'summary_for_recruiter', '')
            cell = ws.cell(row=row_num, column=3, value=verdict_reason[:50] + "..." if len(verdict_reason) > 50 else verdict_reason)
            apply_cell_style(cell, font=FONTS['body_small'], alignment=left, fill=light_fill, border=thin_border)

            ws.row_dimensions[row_num].height = 26
    else:
        ws.merge_cells('A8:D8')
        cell = ws.cell(row=8, column=1, value="Нет зелёных кандидатов. Рассмотрите жёлтых.")
        apply_cell_style(cell, font=FONTS['body'], alignment=center, fill=light_fill)
        ws.row_dimensions[8].height = 26

    # Footer
    footer_row = 7 + max(len(green_candidates), 1) + 2
    ws.merge_cells(f'A{footer_row}:D{footer_row}')
    cell = ws.cell(row=footer_row, column=1, value="TIMLY — AI-скрининг резюме │ timly-hr.ru")
    apply_cell_style(cell, font=Font(name='Calibri', size=9, italic=True, color=COLORS['muted']), alignment=center)

    # ========== СОХРАНЕНИЕ ==========
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    temp_file.close()

    return temp_file.name
