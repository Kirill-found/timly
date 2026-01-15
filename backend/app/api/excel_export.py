"""
Excel экспорт v8.0 — HR отчёт
Под формат AI v5.1: метрики, вывод, конкретика

2 вкладки:
- Сводка: Вывод + опыт за 30 секунд
- Детальный анализ: Плюсы, минусы, что уточнить
"""
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
import tempfile
import json


def create_excel_export(vacancy, results: list, recommendation_filter: Optional[str] = None) -> str:
    """Excel v8.0 — под AI v5.1"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import DataBarRule

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    summary_ws = wb.create_sheet("Сводка", 0)
    deep_ws = wb.create_sheet("Детали", 1)

    # ══════════════════════════════════════════════════════════════
    # DESIGN SYSTEM — Refined, not generic
    # ══════════════════════════════════════════════════════════════

    PALETTE = {
        # Core
        'navy': '1E293B',        # Deep navy — primary
        'slate': '64748B',       # Muted text
        'cloud': 'F8FAFC',       # Off-white bg
        'white': 'FFFFFF',
        'border': 'E2E8F0',

        # Verdict — muted, sophisticated
        'green': '059669',
        'green_bg': 'D1FAE5',
        'amber': 'D97706',
        'amber_bg': 'FEF3C7',
        'coral': 'DC2626',
        'coral_bg': 'FEE2E2',
    }

    # Typography hierarchy
    FONT = {
        'title': Font(name='Segoe UI', size=18, bold=True, color=PALETTE['navy']),
        'subtitle': Font(name='Segoe UI', size=10, color=PALETTE['slate']),
        'header': Font(name='Segoe UI', size=9, bold=True, color=PALETTE['white']),
        'name': Font(name='Segoe UI', size=11, bold=True, color=PALETTE['navy']),
        'body': Font(name='Segoe UI', size=10, color='374151'),
        'small': Font(name='Segoe UI', size=9, color=PALETTE['slate']),
        'link': Font(name='Segoe UI', size=10, color='2563EB', underline='single'),
        'score': Font(name='Segoe UI', size=12, bold=True),
        'metric': Font(name='Segoe UI', size=36, bold=True),
    }

    # Fills
    FILL = {
        'header': PatternFill(start_color=PALETTE['navy'], fill_type="solid"),
        'cloud': PatternFill(start_color=PALETTE['cloud'], fill_type="solid"),
        'white': PatternFill(start_color=PALETTE['white'], fill_type="solid"),
        'green': PatternFill(start_color=PALETTE['green_bg'], fill_type="solid"),
        'amber': PatternFill(start_color=PALETTE['amber_bg'], fill_type="solid"),
        'coral': PatternFill(start_color=PALETTE['coral_bg'], fill_type="solid"),
    }

    BORDER = Border(
        left=Side(style='thin', color=PALETTE['border']),
        right=Side(style='thin', color=PALETTE['border']),
        top=Side(style='thin', color=PALETTE['border']),
        bottom=Side(style='thin', color=PALETTE['border'])
    )

    ALIGN = {
        'center': Alignment(horizontal="center", vertical="center", wrap_text=True),
        'left': Alignment(horizontal="left", vertical="center", wrap_text=True),
        'top': Alignment(horizontal="left", vertical="top", wrap_text=True),
    }

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def raw(analysis, key, default=None):
        r = getattr(analysis, 'raw_result', None) or {}
        return r.get(key, default)

    def verdict_style(v):
        return {
            'GREEN': (FILL['green'], PALETTE['green'], '●'),
            'YELLOW': (FILL['amber'], PALETTE['amber'], '●'),
            'RED': (FILL['coral'], PALETTE['coral'], '●'),
        }.get(v, (FILL['amber'], PALETTE['amber'], '●'))

    def bullets(items, max_n=5):
        if not items: return "—"
        if isinstance(items, str): return items
        return "\n".join([f"• {i}" for i in items[:max_n] if i])

    def cell_style(cell, font=None, fill=None, align=None, border=None):
        if font: cell.font = font
        if fill: cell.fill = fill
        if align: cell.alignment = align
        if border: cell.border = border

    # Stats
    total = len(results)
    green_n = len([r for r, _ in results if raw(r, 'verdict') == 'GREEN'])
    yellow_n = len([r for r, _ in results if raw(r, 'verdict') == 'YELLOW'])
    red_n = total - green_n - yellow_n

    # Sort: GREEN → YELLOW → RED
    def sort_key(item):
        v = raw(item[0], 'verdict', 'RED')
        return {'GREEN': 0, 'YELLOW': 1, 'RED': 2}.get(v, 2)

    sorted_results = sorted(results, key=sort_key)

    # ══════════════════════════════════════════════════════════════
    # SHEET 1: SUMMARY — Shortlist за 30 секунд
    # ══════════════════════════════════════════════════════════════
    ws = summary_ws

    # Column widths: ● | ИМЯ | ДОЛЖНОСТЬ | ОПЫТ | БАЛЛ | ЗАРПЛАТА | ВЫВОД | СТАТУС
    widths = {'A': 4, 'B': 22, 'C': 24, 'D': 16, 'E': 7, 'F': 14, 'G': 50, 'H': 10}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells('A1:H1')
    c = ws.cell(row=1, column=1, value=f"{vacancy.title}")
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 32

    # Stats bar
    ws.merge_cells('A2:H2')
    stats = f"● {green_n} звонить   ● {yellow_n} рассмотреть   ● {red_n} отклонить   │   {total} всего"
    c = ws.cell(row=2, column=1, value=stats)
    cell_style(c, font=FONT['subtitle'], align=ALIGN['center'], fill=FILL['cloud'])
    ws.row_dimensions[2].height = 24

    # Spacer
    ws.row_dimensions[3].height = 6

    # Headers v8: ● | ИМЯ | ДОЛЖНОСТЬ | ОПЫТ | БАЛЛ | ЗАРПЛАТА | ВЫВОД | СТАТУС
    headers = ['', 'ИМЯ', 'ДОЛЖНОСТЬ', 'ОПЫТ', 'БАЛЛ', 'ЗАРПЛАТА', 'ВЫВОД', 'СТАТУС']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=4, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[4].height = 28
    ws.freeze_panes = 'A5'

    # Data rows
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 4
        v = raw(analysis, 'verdict', 'YELLOW')
        fill_v, color_v, symbol = verdict_style(v)
        score = raw(analysis, 'rank_score') or getattr(analysis, 'rank_score', 0) or 0
        row_fill = FILL['white'] if idx % 2 else FILL['cloud']

        # Парсим resume_data
        resume = app.resume_data or {}
        if isinstance(resume, str):
            try:
                resume = json.loads(resume)
            except:
                resume = {}

        # Col 1: Verdict indicator
        c = ws.cell(row=row, column=1, value=symbol)
        cell_style(c, font=Font(name='Segoe UI', size=14, color=color_v), fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Col 2: Name (with link)
        name = app.candidate_name or "—"
        c = ws.cell(row=row, column=2, value=name)
        if app.resume_url:
            c.hyperlink = app.resume_url
            cell_style(c, font=FONT['link'], fill=row_fill, align=ALIGN['left'], border=BORDER)
        else:
            cell_style(c, font=FONT['name'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 3: Должность
        candidate_title = resume.get('title', '') or ''
        if len(candidate_title) > 28:
            candidate_title = candidate_title[:26] + "..."
        c = ws.cell(row=row, column=3, value=candidate_title or "—")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 4: ОПЫТ — "5 лет • работает" или "3 года • до 2023"
        total_exp = resume.get('total_experience', {})
        months = total_exp.get('months', 0) if isinstance(total_exp, dict) else 0
        years = months // 12 if months else 0
        exp_list = resume.get('experience', [])
        last_end = None
        if exp_list and isinstance(exp_list[0], dict):
            end = exp_list[0].get('end')
            if end is None:
                last_end = "работает"
            elif isinstance(end, str):
                last_end = f"до {end[:4]}" if len(end) >= 4 else "—"
            elif isinstance(end, dict):
                last_end = f"до {end.get('year', '?')}"
        exp_text = f"{years} лет • {last_end}" if last_end else f"{years} лет"
        c = ws.cell(row=row, column=4, value=exp_text)
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 5: Score
        c = ws.cell(row=row, column=5, value=score)
        score_color = PALETTE['green'] if score >= 75 else (PALETTE['amber'] if score >= 50 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=12, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 6: Зарплата — с дельтой если есть
        sal = raw(analysis, 'salary_fit', {})
        if isinstance(sal, dict):
            status = sal.get('status', '—')
            delta = sal.get('delta_percent', 0)
            if delta and status == 'выше бюджета':
                sal_text = f"+{delta}%"
            elif delta and status == 'ниже бюджета':
                sal_text = f"−{abs(delta)}%"
            else:
                sal_text = "ОК" if status == 'в бюджете' else status
        else:
            sal_text = sal if sal else "—"
        c = ws.cell(row=row, column=6, value=sal_text)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 7: ВЫВОД — verdict_reason (главная колонка!)
        verdict_reason = raw(analysis, 'verdict_reason', '') or ''
        if len(verdict_reason) > 70:
            verdict_reason = verdict_reason[:68] + "..."
        c = ws.cell(row=row, column=7, value=verdict_reason or "—")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 8: Status (пустая колонка для заметок)
        c = ws.cell(row=row, column=8, value="")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        ws.row_dimensions[row].height = 36

    # Auto filter
    ws.auto_filter.ref = f"A4:H{len(results) + 4}"

    # Data bars для Score (col E)
    if len(results) > 0:
        score_range = f"E5:E{len(results) + 4}"
        rule = DataBarRule(
            start_type='num', start_value=0,
            end_type='num', end_value=100,
            color='059669'
        )
        ws.conditional_formatting.add(score_range, rule)

    # ══════════════════════════════════════════════════════════════
    # SHEET 2: DEEP DIVE — Под капотом (v8.0 под AI v5.1)
    # ══════════════════════════════════════════════════════════════
    ws = deep_ws

    # Columns v8: № | ИМЯ | ● | БАЛЛ | ЗАДАЧИ | МЕТРИКИ | ПЛЮСЫ | МИНУСЫ | УТОЧНИТЬ | ВОПРОСЫ
    widths = {'A': 4, 'B': 20, 'C': 5, 'D': 7, 'E': 28, 'F': 32, 'G': 34, 'H': 34, 'I': 28, 'J': 35}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells('A1:J1')
    c = ws.cell(row=1, column=1, value=f"Детальный анализ: {vacancy.title}")
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 32

    ws.row_dimensions[2].height = 6

    # Headers v8.0 — под формат AI v5.1
    headers = ['№', 'ИМЯ', '', 'БАЛЛ', 'ЗАДАЧИ ВАКАНСИИ', 'МЕТРИКИ КАНДИДАТА', 'ПЛЮСЫ', 'МИНУСЫ', 'УТОЧНИТЬ', 'ВОПРОСЫ']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[3].height = 28
    ws.freeze_panes = 'C4'

    def format_metrics(metrics):
        """Форматирование candidate_metrics в читаемый вид"""
        if not metrics or not isinstance(metrics, list):
            return "—"
        lines = []
        for m in metrics[:4]:
            if isinstance(m, dict):
                name = m.get('name', '')
                value = m.get('value')
                period = m.get('period')
                if value and value != 'null':
                    line = f"• {name}: {value}"
                    if period and period != 'null':
                        line += f" ({period})"
                    lines.append(line)
                else:
                    lines.append(f"• {name}: —")
        return "\n".join(lines) if lines else "—"

    # Data
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 3
        v = raw(analysis, 'verdict', 'YELLOW')
        fill_v, color_v, symbol = verdict_style(v)
        score = raw(analysis, 'rank_score') or getattr(analysis, 'rank_score', 0) or 0
        row_fill = FILL['white'] if idx % 2 else FILL['cloud']

        # Col 1: №
        c = ws.cell(row=row, column=1, value=idx)
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 2: Name (with link)
        name = app.candidate_name or "—"
        c = ws.cell(row=row, column=2, value=name)
        if app.resume_url:
            c.hyperlink = app.resume_url
            cell_style(c, font=FONT['link'], fill=row_fill, align=ALIGN['left'], border=BORDER)
        else:
            cell_style(c, font=FONT['name'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 3: Verdict indicator
        c = ws.cell(row=row, column=3, value=symbol)
        cell_style(c, font=Font(name='Segoe UI', size=12, color=color_v), fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Col 4: Score
        c = ws.cell(row=row, column=4, value=score)
        score_color = PALETTE['green'] if score >= 75 else (PALETTE['amber'] if score >= 50 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=11, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 5: Задачи вакансии (vacancy_needs)
        needs = raw(analysis, 'vacancy_needs', [])
        c = ws.cell(row=row, column=5, value=bullets(needs, 3))
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 6: Метрики кандидата (candidate_metrics)
        metrics = raw(analysis, 'candidate_metrics', [])
        c = ws.cell(row=row, column=6, value=format_metrics(metrics))
        # Цвет в зависимости от заполненности
        filled = sum(1 for m in (metrics or []) if isinstance(m, dict) and m.get('value') and m.get('value') != 'null')
        metrics_color = PALETTE['green'] if filled >= 2 else (PALETTE['amber'] if filled >= 1 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=9, color=metrics_color), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 7: Плюсы (pros)
        pros = raw(analysis, 'pros', [])
        c = ws.cell(row=row, column=7, value=bullets(pros, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 8: Минусы (cons)
        cons = raw(analysis, 'cons', [])
        c = ws.cell(row=row, column=8, value=bullets(cons, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 9: Уточнить (missing_info)
        missing = raw(analysis, 'missing_info', [])
        c = ws.cell(row=row, column=9, value=bullets(missing, 3))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['amber']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 10: Вопросы на интервью
        questions = raw(analysis, 'interview_questions', [])
        c = ws.cell(row=row, column=10, value=bullets(questions, 3))
        cell_style(c, font=Font(name='Segoe UI', size=10, color=PALETTE['navy']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        ws.row_dimensions[row].height = 95

    ws.auto_filter.ref = f"A3:J{len(results) + 3}"

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)
    temp.close()
    return temp.name
