"""
Excel экспорт для AI анализа резюме v4.0
Редизайн: Editorial/Magazine + Data Dashboard

Product-driven:
- JTBD: "За 5 секунд понять кого звонить первым"
- Фокус на Tier A/B/C как главном решении
- Executive Summary с ключевыми метриками

Design:
- Aesthetic: Editorial/Magazine (Bloomberg, FT, McKinsey)
- Typography: Calibri (современный, читаемый)
- Spacing: Щедрые отступы, высокие строки
- Hierarchy: Tier крупно, остальное — поддержка
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
    Создание Excel файла с результатами анализа v4.0
    Editorial/Magazine design

    Returns:
        str: путь к временному файлу
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
    from openpyxl.utils import get_column_letter

    # ========== СОЗДАНИЕ КНИГИ ==========
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    candidates_ws = wb.create_sheet("Кандидаты", 0)
    details_ws = wb.create_sheet("Детали", 1)
    dashboard_ws = wb.create_sheet("Дашборд", 2)

    # ========== ЦВЕТОВАЯ ПАЛИТРА ==========
    # Editorial style: сдержанные цвета, акценты только на важном
    COLORS = {
        'primary': '1A1A2E',      # Deep Navy (заголовки)
        'accent': 'E94560',       # Coral Red (акценты)
        'success': '16A34A',      # Green
        'warning': 'D97706',      # Amber
        'muted': '6B7280',        # Gray
        'light_bg': 'F8FAFC',     # Light gray bg
        'white': 'FFFFFF',
        'border': 'E2E8F0',       # Light border

        # Tier colors (пастельные, не кричащие)
        'tier_a_bg': 'DCFCE7',    # Light green
        'tier_a_text': '166534',  # Dark green
        'tier_b_bg': 'DBEAFE',    # Light blue
        'tier_b_text': '1E40AF',  # Dark blue
        'tier_c_bg': 'F3F4F6',    # Light gray
        'tier_c_text': '4B5563',  # Dark gray

        # Recommendations
        'hire_bg': 'DCFCE7',
        'hire_text': '166534',
        'interview_bg': 'FEF3C7',
        'interview_text': '92400E',
        'maybe_bg': 'FED7AA',
        'maybe_text': '9A3412',
        'reject_bg': 'F3F4F6',
        'reject_text': '6B7280',
    }

    # ========== ТИПОГРАФИКА ==========
    # Calibri — современный, профессиональный, хорошо читается
    FONTS = {
        'title': Font(name='Calibri', size=22, bold=True, color=COLORS['primary']),
        'subtitle': Font(name='Calibri', size=14, color=COLORS['muted']),
        'header': Font(name='Calibri', size=11, bold=True, color=COLORS['white']),
        'subheader': Font(name='Calibri', size=11, bold=True, color=COLORS['primary']),
        'body': Font(name='Calibri', size=11, color='374151'),
        'body_small': Font(name='Calibri', size=10, color=COLORS['muted']),
        'link': Font(name='Calibri', size=11, color=COLORS['accent'], underline='single'),
        'tier_large': Font(name='Calibri', size=16, bold=True),
        'metric_value': Font(name='Calibri', size=28, bold=True, color=COLORS['primary']),
        'metric_label': Font(name='Calibri', size=10, color=COLORS['muted']),
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

    def get_score(analysis, score_name):
        scores = get_raw(analysis, 'scores', {})
        return scores.get(score_name, 0)

    def format_bullets(items, max_items=5):
        if not items:
            return "—"
        if isinstance(items, str):
            return items
        items = items[:max_items]
        return "\n".join([f"• {item}" for item in items if item])

    def get_tier_style(tier):
        styles = {
            'A': (COLORS['tier_a_bg'], COLORS['tier_a_text']),
            'B': (COLORS['tier_b_bg'], COLORS['tier_b_text']),
            'C': (COLORS['tier_c_bg'], COLORS['tier_c_text']),
        }
        return styles.get(tier, styles['C'])

    def get_rec_style(rec):
        styles = {
            'hire': (COLORS['hire_bg'], COLORS['hire_text'], 'НАНЯТЬ'),
            'interview': (COLORS['interview_bg'], COLORS['interview_text'], 'ИНТЕРВЬЮ'),
            'maybe': (COLORS['maybe_bg'], COLORS['maybe_text'], 'ВОЗМОЖНО'),
            'reject': (COLORS['reject_bg'], COLORS['reject_text'], 'ОТКЛОНИТЬ'),
        }
        return styles.get(rec, styles.get('maybe', (COLORS['reject_bg'], COLORS['reject_text'], 'Н/Д')))

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
    tier_a = len([r for r, _ in results if get_raw(r, 'tier') == 'A'])
    tier_b = len([r for r, _ in results if get_raw(r, 'tier') == 'B'])
    tier_c = total - tier_a - tier_b

    hire_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'hire'])
    interview_count = len([r for r, _ in results if (get_raw(r, 'recommendation') or r.recommendation) == 'interview'])

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 1: КАНДИДАТЫ (Быстрое решение)
    # ═══════════════════════════════════════════════════════════════
    ws = candidates_ws

    # Ширины колонок
    col_widths = {'A': 6, 'B': 8, 'C': 28, 'D': 14, 'E': 35, 'F': 25, 'G': 12}
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    # --- HEADER SECTION ---
    # Row 1: Title
    ws.merge_cells('A1:G1')
    title_cell = ws.cell(row=1, column=1, value="TIMLY")
    apply_cell_style(title_cell, font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 35

    # Row 2: Vacancy name
    ws.merge_cells('A2:G2')
    vacancy_cell = ws.cell(row=2, column=1, value=f"Анализ кандидатов: {vacancy.title}")
    apply_cell_style(vacancy_cell, font=FONTS['subtitle'], alignment=center, fill=light_fill)
    ws.row_dimensions[2].height = 25

    # Row 3: Executive Summary (key metrics)
    ws.merge_cells('A3:G3')
    summary_text = f"Всего: {total}  │  Tier A: {tier_a}  │  Tier B: {tier_b}  │  Tier C: {tier_c}  │  Дата: {datetime.now().strftime('%d.%m.%Y')}"
    summary_cell = ws.cell(row=3, column=1, value=summary_text)
    apply_cell_style(summary_cell, font=FONTS['body_small'], alignment=center, fill=light_fill)
    ws.row_dimensions[3].height = 22

    # Row 4: Spacer
    ws.row_dimensions[4].height = 10

    # Row 5: Table headers
    headers = ['№', 'TIER', 'КАНДИДАТ', 'РЕШЕНИЕ', 'КРАТКОЕ РЕЗЮМЕ', 'КОНТАКТЫ', 'ССЫЛКА']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=header)
        apply_cell_style(cell, font=FONTS['header'], fill=header_fill, alignment=center, border=thin_border)
    ws.row_dimensions[5].height = 30
    ws.freeze_panes = 'A6'

    # --- DATA ROWS ---
    # Сортировка по Tier: A первые, потом B, потом C
    def tier_sort_key(item):
        tier = get_raw(item[0], 'tier', 'C')
        return {'A': 0, 'B': 1, 'C': 2}.get(tier, 2)

    sorted_results = sorted(results, key=tier_sort_key)

    for idx, (analysis, application) in enumerate(sorted_results, 1):
        row = idx + 5
        tier = get_raw(analysis, 'tier', 'C')
        tier_bg, tier_text = get_tier_style(tier)
        rec = get_raw(analysis, 'recommendation') or analysis.recommendation or 'unknown'
        rec_bg, rec_text, rec_label = get_rec_style(rec)

        # Alternating row colors
        row_fill = white_fill if idx % 2 == 1 else light_fill

        # № (index)
        cell = ws.cell(row=row, column=1, value=idx)
        apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=center, border=thin_border)

        # TIER (large, colored)
        cell = ws.cell(row=row, column=2, value=tier)
        tier_fill = PatternFill(start_color=tier_bg, end_color=tier_bg, fill_type="solid")
        tier_font = Font(name='Calibri', size=16, bold=True, color=tier_text)
        apply_cell_style(cell, font=tier_font, fill=tier_fill, alignment=center, border=thin_border)

        # КАНДИДАТ
        name = application.candidate_name or "Не указано"
        cell = ws.cell(row=row, column=3, value=name)
        apply_cell_style(cell, font=FONTS['subheader'], fill=row_fill, alignment=left, border=thin_border)

        # РЕШЕНИЕ (colored badge)
        cell = ws.cell(row=row, column=4, value=rec_label)
        rec_fill = PatternFill(start_color=rec_bg, end_color=rec_bg, fill_type="solid")
        rec_font = Font(name='Calibri', size=10, bold=True, color=rec_text)
        apply_cell_style(cell, font=rec_font, fill=rec_fill, alignment=center, border=thin_border)

        # КРАТКОЕ РЕЗЮМЕ
        summary = get_raw(analysis, 'summary') or get_raw(analysis, 'summary_one_line') or "—"
        cell = ws.cell(row=row, column=5, value=summary)
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left, border=thin_border)

        # КОНТАКТЫ
        contacts = []
        if application.candidate_phone:
            contacts.append(application.candidate_phone)
        if application.candidate_email:
            contacts.append(application.candidate_email)
        cell = ws.cell(row=row, column=6, value="\n".join(contacts) if contacts else "—")
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left, border=thin_border)

        # ССЫЛКА
        if application.resume_url:
            cell = ws.cell(row=row, column=7, value="Резюме →")
            cell.hyperlink = application.resume_url
            apply_cell_style(cell, font=FONTS['link'], fill=row_fill, alignment=center, border=thin_border)
        else:
            cell = ws.cell(row=row, column=7, value="—")
            apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=center, border=thin_border)

        ws.row_dimensions[row].height = 45

    ws.auto_filter.ref = f"A5:G{len(results) + 5}"

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 2: ДЕТАЛИ (Подготовка к интервью)
    # ═══════════════════════════════════════════════════════════════
    ws = details_ws

    # Ширины колонок
    col_widths = {'A': 6, 'B': 22, 'C': 8, 'D': 8, 'E': 8, 'F': 8, 'G': 8, 'H': 40, 'I': 40, 'J': 40}
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    # Header
    ws.merge_cells('A1:J1')
    title_cell = ws.cell(row=1, column=1, value=f"TIMLY | Детальный анализ: {vacancy.title}")
    apply_cell_style(title_cell, font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 35

    ws.merge_cells('A2:J2')
    ws.cell(row=2, column=1, value="Оценки по шкале 1-5 │ Вопросы помогут раскрыть gaps кандидата")
    apply_cell_style(ws.cell(row=2, column=1), font=FONTS['body_small'], alignment=center, fill=light_fill)
    ws.row_dimensions[2].height = 22

    ws.row_dimensions[3].height = 8

    # Table headers
    headers = ['№', 'КАНДИДАТ', 'TIER', 'РЕЛ.', 'ЭКСП.', 'ТРАЕК.', 'СТАБ.', 'ПЛЮСЫ', 'МИНУСЫ', 'ВОПРОСЫ ДЛЯ ИНТЕРВЬЮ']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        apply_cell_style(cell, font=FONTS['header'], fill=header_fill, alignment=center, border=thin_border)
    ws.row_dimensions[4].height = 28
    ws.freeze_panes = 'A5'

    for idx, (analysis, application) in enumerate(sorted_results, 1):
        row = idx + 4
        tier = get_raw(analysis, 'tier', 'C')
        tier_bg, tier_text = get_tier_style(tier)
        row_fill = white_fill if idx % 2 == 1 else light_fill

        # №
        cell = ws.cell(row=row, column=1, value=idx)
        apply_cell_style(cell, font=FONTS['body_small'], fill=row_fill, alignment=center, border=thin_border)

        # Кандидат
        cell = ws.cell(row=row, column=2, value=application.candidate_name or "Не указано")
        apply_cell_style(cell, font=FONTS['subheader'], fill=row_fill, alignment=left, border=thin_border)

        # Tier
        cell = ws.cell(row=row, column=3, value=tier)
        tier_fill = PatternFill(start_color=tier_bg, end_color=tier_bg, fill_type="solid")
        tier_font = Font(name='Calibri', size=14, bold=True, color=tier_text)
        apply_cell_style(cell, font=tier_font, fill=tier_fill, alignment=center, border=thin_border)

        # 4 оценки
        scores = [
            get_score(analysis, 'relevance'),
            get_score(analysis, 'expertise'),
            get_score(analysis, 'trajectory'),
            get_score(analysis, 'stability'),
        ]
        for col_idx, score in enumerate(scores, 4):
            cell = ws.cell(row=row, column=col_idx, value=score if score else "—")
            score_color = COLORS['success'] if score and score >= 4 else (COLORS['warning'] if score and score == 3 else COLORS['muted'])
            score_font = Font(name='Calibri', size=12, bold=True, color=score_color)
            apply_cell_style(cell, font=score_font, fill=row_fill, alignment=center, border=thin_border)

        # Плюсы
        pros = get_raw(analysis, 'pros') or analysis.strengths or []
        cell = ws.cell(row=row, column=8, value=format_bullets(pros, 4))
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left_top, border=thin_border)

        # Минусы
        cons = get_raw(analysis, 'cons') or analysis.weaknesses or []
        cell = ws.cell(row=row, column=9, value=format_bullets(cons, 4))
        apply_cell_style(cell, font=FONTS['body'], fill=row_fill, alignment=left_top, border=thin_border)

        # Вопросы для интервью
        questions = get_raw(analysis, 'interview_questions', [])
        cell = ws.cell(row=row, column=10, value=format_bullets(questions, 3))
        questions_font = Font(name='Calibri', size=11, color=COLORS['primary'])
        apply_cell_style(cell, font=questions_font, fill=row_fill, alignment=left_top, border=thin_border)

        ws.row_dimensions[row].height = 85

    ws.auto_filter.ref = f"A4:J{len(results) + 4}"

    # ═══════════════════════════════════════════════════════════════
    # ЛИСТ 3: ДАШБОРД (Для руководителя)
    # ═══════════════════════════════════════════════════════════════
    ws = dashboard_ws

    for col in range(1, 7):
        ws.column_dimensions[get_column_letter(col)].width = 18

    # Header
    ws.merge_cells('A1:F1')
    title_cell = ws.cell(row=1, column=1, value="TIMLY | ДАШБОРД")
    apply_cell_style(title_cell, font=FONTS['title'], alignment=center)
    ws.row_dimensions[1].height = 40

    ws.merge_cells('A2:F2')
    ws.cell(row=2, column=1, value=f"Вакансия: {vacancy.title} │ {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    apply_cell_style(ws.cell(row=2, column=1), font=FONTS['subtitle'], alignment=center, fill=light_fill)
    ws.row_dimensions[2].height = 28

    ws.row_dimensions[3].height = 15

    # --- METRIC CARDS ---
    def create_metric_card(ws, start_row, col, value, label, color=None):
        """Создаёт карточку метрики"""
        # Value cell
        cell = ws.cell(row=start_row, column=col, value=value)
        value_font = Font(name='Calibri', size=32, bold=True, color=color or COLORS['primary'])
        apply_cell_style(cell, font=value_font, alignment=center, fill=white_fill, border=thin_border)

        # Label cell
        cell = ws.cell(row=start_row + 1, column=col, value=label)
        apply_cell_style(cell, font=FONTS['metric_label'], alignment=center, fill=light_fill, border=thin_border)

    # Row heights for metric cards
    ws.row_dimensions[4].height = 55
    ws.row_dimensions[5].height = 28

    # Key metrics row 1
    create_metric_card(ws, 4, 1, total, "ВСЕГО", COLORS['primary'])
    create_metric_card(ws, 4, 2, tier_a, "TIER A", COLORS['tier_a_text'])
    create_metric_card(ws, 4, 3, tier_b, "TIER B", COLORS['tier_b_text'])
    create_metric_card(ws, 4, 4, tier_c, "TIER C", COLORS['tier_c_text'])
    create_metric_card(ws, 4, 5, hire_count, "НАНЯТЬ", COLORS['success'])
    create_metric_card(ws, 4, 6, interview_count, "ИНТЕРВЬЮ", COLORS['warning'])

    # Spacer
    ws.row_dimensions[6].height = 20

    # --- TIER DISTRIBUTION ---
    ws.merge_cells('A7:F7')
    cell = ws.cell(row=7, column=1, value="РАСПРЕДЕЛЕНИЕ ПО TIER")
    apply_cell_style(cell, font=FONTS['subheader'], alignment=center, fill=header_fill)
    cell.font = FONTS['header']
    ws.row_dimensions[7].height = 28

    # Visual bar representation
    ws.row_dimensions[8].height = 35

    # Calculate percentages
    pct_a = round(tier_a / total * 100) if total > 0 else 0
    pct_b = round(tier_b / total * 100) if total > 0 else 0
    pct_c = 100 - pct_a - pct_b

    # Tier A bar
    ws.merge_cells('A8:B8')
    cell = ws.cell(row=8, column=1, value=f"A: {tier_a} ({pct_a}%)")
    tier_a_fill = PatternFill(start_color=COLORS['tier_a_bg'], end_color=COLORS['tier_a_bg'], fill_type="solid")
    apply_cell_style(cell, font=Font(name='Calibri', size=14, bold=True, color=COLORS['tier_a_text']),
                     fill=tier_a_fill, alignment=center, border=thin_border)

    # Tier B bar
    ws.merge_cells('C8:D8')
    cell = ws.cell(row=8, column=3, value=f"B: {tier_b} ({pct_b}%)")
    tier_b_fill = PatternFill(start_color=COLORS['tier_b_bg'], end_color=COLORS['tier_b_bg'], fill_type="solid")
    apply_cell_style(cell, font=Font(name='Calibri', size=14, bold=True, color=COLORS['tier_b_text']),
                     fill=tier_b_fill, alignment=center, border=thin_border)

    # Tier C bar
    ws.merge_cells('E8:F8')
    cell = ws.cell(row=8, column=5, value=f"C: {tier_c} ({pct_c}%)")
    tier_c_fill = PatternFill(start_color=COLORS['tier_c_bg'], end_color=COLORS['tier_c_bg'], fill_type="solid")
    apply_cell_style(cell, font=Font(name='Calibri', size=14, bold=True, color=COLORS['tier_c_text']),
                     fill=tier_c_fill, alignment=center, border=thin_border)

    # Spacer
    ws.row_dimensions[9].height = 20

    # --- AVERAGE SCORES ---
    ws.merge_cells('A10:F10')
    cell = ws.cell(row=10, column=1, value="СРЕДНИЕ ОЦЕНКИ (шкала 1-5)")
    apply_cell_style(cell, font=FONTS['header'], alignment=center, fill=header_fill)
    ws.row_dimensions[10].height = 28

    def avg_score(score_name):
        scores = [get_score(r, score_name) for r, _ in results if get_score(r, score_name)]
        return round(sum(scores) / len(scores), 1) if scores else 0

    avg_scores = [
        ('Релевантность', avg_score('relevance')),
        ('Экспертиза', avg_score('expertise')),
        ('Траектория', avg_score('trajectory')),
        ('Стабильность', avg_score('stability')),
    ]

    ws.row_dimensions[11].height = 45
    ws.row_dimensions[12].height = 25

    for col, (label, value) in enumerate(avg_scores, 1):
        # Value
        cell = ws.cell(row=11, column=col, value=value)
        score_color = COLORS['success'] if value >= 4 else (COLORS['warning'] if value >= 3 else COLORS['muted'])
        apply_cell_style(cell, font=Font(name='Calibri', size=24, bold=True, color=score_color),
                         alignment=center, fill=white_fill, border=thin_border)
        # Label
        cell = ws.cell(row=12, column=col, value=label)
        apply_cell_style(cell, font=FONTS['metric_label'], alignment=center, fill=light_fill, border=thin_border)

    # Empty columns 5-6
    ws.cell(row=11, column=5, value="")
    ws.cell(row=11, column=6, value="")
    ws.cell(row=12, column=5, value="")
    ws.cell(row=12, column=6, value="")

    # Spacer
    ws.row_dimensions[13].height = 20

    # --- TOP CANDIDATES ---
    ws.merge_cells('A14:F14')
    cell = ws.cell(row=14, column=1, value="ТОП-5 КАНДИДАТОВ (TIER A)")
    apply_cell_style(cell, font=FONTS['header'], alignment=center, fill=header_fill)
    ws.row_dimensions[14].height = 28

    top_candidates = [r for r in sorted_results if get_raw(r[0], 'tier') == 'A'][:5]

    if top_candidates:
        for idx, (analysis, application) in enumerate(top_candidates, 1):
            row = 14 + idx
            ws.merge_cells(f'A{row}:C{row}')

            name = application.candidate_name or "Не указано"
            cell = ws.cell(row=row, column=1, value=f"{idx}. {name}")
            apply_cell_style(cell, font=FONTS['subheader'], alignment=left, fill=white_fill, border=thin_border)

            ws.merge_cells(f'D{row}:F{row}')
            summary = get_raw(analysis, 'summary') or "—"
            cell = ws.cell(row=row, column=4, value=summary[:60] + "..." if len(summary) > 60 else summary)
            apply_cell_style(cell, font=FONTS['body_small'], alignment=left, fill=light_fill, border=thin_border)

            ws.row_dimensions[row].height = 28
    else:
        ws.merge_cells('A15:F15')
        cell = ws.cell(row=15, column=1, value="Нет кандидатов Tier A")
        apply_cell_style(cell, font=FONTS['body_small'], alignment=center, fill=light_fill)
        ws.row_dimensions[15].height = 28

    # --- FOOTER ---
    footer_row = 14 + max(len(top_candidates), 1) + 2
    ws.merge_cells(f'A{footer_row}:F{footer_row}')
    cell = ws.cell(row=footer_row, column=1, value="Создано с помощью TIMLY — AI-платформа для скрининга резюме │ timly-hr.ru")
    apply_cell_style(cell, font=Font(name='Calibri', size=9, italic=True, color=COLORS['muted']), alignment=center)

    # ========== СОХРАНЕНИЕ ==========
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    temp_file.close()

    return temp_file.name
