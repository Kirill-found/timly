"""
Excel экспорт v6.0 — Premium HR Design
Принципы: Luxury/Refined + Industrial/Utilitarian

2 вкладки:
- Summary: Shortlist за 30 секунд
- Deep Dive: Полный анализ под капотом
"""
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
import tempfile


def create_excel_export(vacancy, results: list, recommendation_filter: Optional[str] = None) -> str:
    """Excel v6.0 — Premium HR Design"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import DataBarRule

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    summary_ws = wb.create_sheet("Summary", 0)
    deep_ws = wb.create_sheet("Deep Dive", 1)

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

    # Column widths
    widths = {'A': 5, 'B': 25, 'C': 20, 'D': 8, 'E': 12, 'F': 35, 'G': 30, 'H': 15}
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

    # Headers: Verdict | Name | Role | Score | Salary | Key Pro | Key Risk | Status
    headers = ['', 'NAME', 'ROLE', 'SCORE', 'SALARY', 'KEY PRO', 'KEY RISK', 'STATUS']
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

        # Verdict indicator
        c = ws.cell(row=row, column=1, value=symbol)
        cell_style(c, font=Font(name='Segoe UI', size=14, color=color_v), fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Name (with link)
        name = app.candidate_name or "—"
        c = ws.cell(row=row, column=2, value=name)
        if app.resume_url:
            c.hyperlink = app.resume_url
            cell_style(c, font=FONT['link'], fill=row_fill, align=ALIGN['left'], border=BORDER)
        else:
            cell_style(c, font=FONT['name'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Role
        exp = raw(analysis, 'experience_summary', {}) or {}
        role = exp.get('last_position', '') if isinstance(exp, dict) else ''
        company = exp.get('best_company') or exp.get('last_company', '')
        role_text = f"{role[:22]}..." if len(role) > 22 else role
        if company:
            role_text += f"\n@ {company[:18]}"
        c = ws.cell(row=row, column=3, value=role_text or "—")
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Score
        c = ws.cell(row=row, column=4, value=score)
        score_color = PALETTE['green'] if score >= 75 else (PALETTE['amber'] if score >= 50 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=12, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Salary
        sal = raw(analysis, 'salary_fit', '—')
        sal_text = {'в бюджете': '✓ В бюджете', 'выше бюджета': '↑ Дорого', 'ниже рынка': '↓ Дёшево'}.get(sal, sal)
        c = ws.cell(row=row, column=5, value=sal_text)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Key Pro (первый из pros)
        pros = raw(analysis, 'pros', []) or []
        key_pro = pros[0] if pros else "—"
        if len(key_pro) > 50: key_pro = key_pro[:50] + "..."
        c = ws.cell(row=row, column=6, value=key_pro)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Key Risk (первый из cons или red_flags)
        cons = raw(analysis, 'cons', []) or []
        flags = raw(analysis, 'red_flags', []) or []
        key_risk = flags[0] if flags else (cons[0] if cons else "—")
        if len(key_risk) > 45: key_risk = key_risk[:45] + "..."
        c = ws.cell(row=row, column=7, value=key_risk)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Status (пустая колонка для заметок)
        c = ws.cell(row=row, column=8, value="")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        ws.row_dimensions[row].height = 42

    # Auto filter
    ws.auto_filter.ref = f"A4:H{len(results) + 4}"

    # Data bars для Score
    if len(results) > 0:
        score_range = f"D5:D{len(results) + 4}"
        rule = DataBarRule(
            start_type='num', start_value=0,
            end_type='num', end_value=100,
            color='059669'
        )
        ws.conditional_formatting.add(score_range, rule)

    # ══════════════════════════════════════════════════════════════
    # SHEET 2: DEEP DIVE — Под капотом
    # ══════════════════════════════════════════════════════════════
    ws = deep_ws

    # Columns: №, Name, Verdict, Score, Pain Points, Verified Skills, Unverified, Missing, Pros, Cons, Questions
    widths = {'A': 4, 'B': 20, 'C': 5, 'D': 7, 'E': 30, 'F': 28, 'G': 22, 'H': 20, 'I': 32, 'J': 32, 'K': 35}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells('A1:K1')
    c = ws.cell(row=1, column=1, value=f"Deep Dive: {vacancy.title}")
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 32

    ws.row_dimensions[2].height = 6

    # Headers
    headers = ['#', 'NAME', '', 'SCORE', 'PAIN POINTS', 'VERIFIED SKILLS', 'UNVERIFIED', 'MISSING', 'PROS', 'CONS', 'INTERVIEW Q']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[3].height = 28
    ws.freeze_panes = 'C4'

    # Data
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 3
        v = raw(analysis, 'verdict', 'YELLOW')
        fill_v, color_v, symbol = verdict_style(v)
        score = raw(analysis, 'rank_score') or getattr(analysis, 'rank_score', 0) or 0
        row_fill = FILL['white'] if idx % 2 else FILL['cloud']

        # #
        c = ws.cell(row=row, column=1, value=idx)
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Name
        c = ws.cell(row=row, column=2, value=app.candidate_name or "—")
        cell_style(c, font=FONT['name'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Verdict
        c = ws.cell(row=row, column=3, value=symbol)
        cell_style(c, font=Font(name='Segoe UI', size=12, color=color_v), fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Score
        c = ws.cell(row=row, column=4, value=score)
        score_color = PALETTE['green'] if score >= 75 else (PALETTE['amber'] if score >= 50 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=11, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Pain Points
        pain = raw(analysis, 'vacancy_pain_points', [])
        c = ws.cell(row=row, column=5, value=bullets(pain, 3))
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Skills analysis
        skills = raw(analysis, 'skills', {}) or raw(analysis, 'skills_analysis', {}) or {}

        # Verified
        verified = skills.get('verified', [])
        c = ws.cell(row=row, column=6, value=bullets(verified, 4))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['green']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Unverified (+ contextual)
        unverified = skills.get('unverified', []) + skills.get('contextual', [])
        c = ws.cell(row=row, column=7, value=bullets(unverified, 3))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['amber']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Missing
        missing = skills.get('missing', [])
        c = ws.cell(row=row, column=8, value=bullets(missing, 3))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['coral']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Pros
        pros = raw(analysis, 'pros', [])
        c = ws.cell(row=row, column=9, value=bullets(pros, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Cons
        cons = raw(analysis, 'cons', [])
        c = ws.cell(row=row, column=10, value=bullets(cons, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Interview Questions
        questions = raw(analysis, 'interview_questions', [])
        c = ws.cell(row=row, column=11, value=bullets(questions, 3))
        cell_style(c, font=Font(name='Segoe UI', size=10, color=PALETTE['navy']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        ws.row_dimensions[row].height = 95

    ws.auto_filter.ref = f"A3:K{len(results) + 3}"

    # Group detailed columns (можно скрыть E-H)
    ws.column_dimensions.group('E', 'H', hidden=False, outline_level=1)

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)
    temp.close()
    return temp.name
