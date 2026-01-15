"""
Excel экспорт v9.0 — HR отчёт
Под формат AI v6.0-lite: GHOST_SKILL, must-have проверка, прозрачный скоринг

2 вкладки:
- Сводка: Вывод + тип позиции + ghost skills
- Детальный анализ: Must-have, навыки, вопросы с good/bad
"""
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
import tempfile
import json


def create_excel_export(vacancy, results: list, recommendation_filter: Optional[str] = None) -> str:
    """Excel v9.0 — под AI v6.0-lite"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import DataBarRule

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    summary_ws = wb.create_sheet("Сводка", 0)
    deep_ws = wb.create_sheet("Детали", 1)

    # ══════════════════════════════════════════════════════════════
    # DESIGN SYSTEM
    # ══════════════════════════════════════════════════════════════

    PALETTE = {
        'navy': '1E293B',
        'slate': '64748B',
        'cloud': 'F8FAFC',
        'white': 'FFFFFF',
        'border': 'E2E8F0',
        'green': '059669',
        'green_bg': 'D1FAE5',
        'amber': 'D97706',
        'amber_bg': 'FEF3C7',
        'coral': 'DC2626',
        'coral_bg': 'FEE2E2',
        'purple': '7C3AED',
    }

    FONT = {
        'title': Font(name='Segoe UI', size=18, bold=True, color=PALETTE['navy']),
        'subtitle': Font(name='Segoe UI', size=10, color=PALETTE['slate']),
        'header': Font(name='Segoe UI', size=9, bold=True, color=PALETTE['white']),
        'name': Font(name='Segoe UI', size=11, bold=True, color=PALETTE['navy']),
        'body': Font(name='Segoe UI', size=10, color='374151'),
        'small': Font(name='Segoe UI', size=9, color=PALETTE['slate']),
        'link': Font(name='Segoe UI', size=10, color='2563EB', underline='single'),
        'ghost': Font(name='Segoe UI', size=9, color=PALETTE['coral']),
        'verified': Font(name='Segoe UI', size=9, color=PALETTE['green']),
    }

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

    def position_type_short(ptype):
        return {
            'RESULTS': 'RES',
            'EXPERTISE': 'EXP',
            'OPERATIONS': 'OPS',
            'COMMUNICATION': 'COM'
        }.get(ptype, '?')

    # Stats
    total = len(results)
    green_n = len([r for r, _ in results if raw(r, 'verdict') == 'GREEN'])
    yellow_n = len([r for r, _ in results if raw(r, 'verdict') == 'YELLOW'])
    red_n = total - green_n - yellow_n

    # Sort: GREEN → YELLOW → RED, then by score
    def sort_key(item):
        v = raw(item[0], 'verdict', 'RED')
        score = raw(item[0], 'score', 0) or 0
        return ({'GREEN': 0, 'YELLOW': 1, 'RED': 2}.get(v, 2), -score)

    sorted_results = sorted(results, key=sort_key)

    # ══════════════════════════════════════════════════════════════
    # SHEET 1: SUMMARY — Shortlist за 30 секунд
    # ══════════════════════════════════════════════════════════════
    ws = summary_ws

    # Column widths: ● | ИМЯ | ДОЛЖНОСТЬ | ОПЫТ | БАЛЛ | ТИП | GHOST | ВЫВОД
    widths = {'A': 4, 'B': 22, 'C': 24, 'D': 14, 'E': 7, 'F': 6, 'G': 8, 'H': 52}
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

    ws.row_dimensions[3].height = 6

    # Headers v9: ● | ИМЯ | ДОЛЖНОСТЬ | ОПЫТ | БАЛЛ | ТИП | 👻 | ВЫВОД
    headers = ['', 'ИМЯ', 'ДОЛЖНОСТЬ', 'ОПЫТ', 'БАЛЛ', 'ТИП', '👻', 'ВЫВОД']
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
        score = raw(analysis, 'score') or raw(analysis, 'rank_score') or 0
        row_fill = FILL['white'] if idx % 2 else FILL['cloud']

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
        if len(candidate_title) > 26:
            candidate_title = candidate_title[:24] + "..."
        c = ws.cell(row=row, column=3, value=candidate_title or "—")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 4: ОПЫТ — "5 лет • работает"
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
        exp_text = f"{years}л • {last_end}" if last_end else f"{years} лет"
        c = ws.cell(row=row, column=4, value=exp_text)
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 5: Score
        c = ws.cell(row=row, column=5, value=score)
        score_color = PALETTE['green'] if score >= 70 else (PALETTE['amber'] if score >= 45 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=12, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 6: Position Type (short)
        ptype = raw(analysis, 'position_type', 'RESULTS')
        c = ws.cell(row=row, column=6, value=position_type_short(ptype))
        cell_style(c, font=FONT['small'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 7: Ghost skills count
        ghost_count = raw(analysis, 'ghost_skills_count', 0) or 0
        ghost_text = str(ghost_count) if ghost_count > 0 else "—"
        c = ws.cell(row=row, column=7, value=ghost_text)
        ghost_color = PALETTE['coral'] if ghost_count >= 3 else (PALETTE['amber'] if ghost_count > 0 else PALETTE['slate'])
        cell_style(c, font=Font(name='Segoe UI', size=10, color=ghost_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 8: ВЫВОД — verdict_reason
        verdict_reason = raw(analysis, 'verdict_reason', '') or ''
        if len(verdict_reason) > 75:
            verdict_reason = verdict_reason[:73] + "..."
        c = ws.cell(row=row, column=8, value=verdict_reason or "—")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        ws.row_dimensions[row].height = 36

    ws.auto_filter.ref = f"A4:H{len(results) + 4}"

    # Data bars для Score
    if len(results) > 0:
        score_range = f"E5:E{len(results) + 4}"
        rule = DataBarRule(start_type='num', start_value=0, end_type='num', end_value=100, color='059669')
        ws.conditional_formatting.add(score_range, rule)

    # ══════════════════════════════════════════════════════════════
    # SHEET 2: DEEP DIVE — v9.0 под AI v6.0-lite
    # ══════════════════════════════════════════════════════════════
    ws = deep_ws

    # Columns: № | ИМЯ | ● | БАЛЛ | MUST-HAVE | НАВЫКИ | ПЛЮСЫ | МИНУСЫ | ВОПРОСЫ
    widths = {'A': 4, 'B': 18, 'C': 5, 'D': 7, 'E': 32, 'F': 34, 'G': 30, 'H': 30, 'I': 45}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells('A1:I1')
    c = ws.cell(row=1, column=1, value=f"Детальный анализ: {vacancy.title}")
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 32

    ws.row_dimensions[2].height = 6

    # Headers v9.0
    headers = ['№', 'ИМЯ', '', 'БАЛЛ', 'MUST-HAVE', 'НАВЫКИ', 'ПЛЮСЫ', 'МИНУСЫ', 'ВОПРОСЫ НА ИНТЕРВЬЮ']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[3].height = 28
    ws.freeze_panes = 'C4'

    def format_must_have(must_have_list):
        """Форматирование must_have проверок"""
        if not must_have_list:
            return "—"
        lines = []
        for m in must_have_list[:4]:
            if isinstance(m, dict):
                req = m.get('requirement', '')[:30]
                status = m.get('status', 'UNCLEAR')
                icon = '✅' if status == 'CONFIRMED' else ('⚠️' if status == 'UNCLEAR' else '❌')
                lines.append(f"{icon} {req}")
        return "\n".join(lines) if lines else "—"

    def format_skills_check(skills_list):
        """Форматирование проверки навыков с ghost detection"""
        if not skills_list:
            return "—"
        lines = []
        for s in skills_list[:5]:
            if isinstance(s, dict):
                skill = s.get('skill', '')[:20]
                status = s.get('status', 'MISSING')
                ghost = s.get('ghost', False)
                if ghost:
                    lines.append(f"👻 {skill}")
                elif status == 'VERIFIED':
                    lines.append(f"✅ {skill}")
                elif status == 'MENTIONED':
                    lines.append(f"⚠️ {skill}")
                else:
                    lines.append(f"❌ {skill}")
        return "\n".join(lines) if lines else "—"

    def format_questions(questions_list):
        """Форматирование вопросов с good/bad answers"""
        if not questions_list:
            return "—"
        lines = []
        for q in questions_list[:3]:
            if isinstance(q, dict):
                question = q.get('question', '')
                why = q.get('why', '')
                good = q.get('good_answer', '')
                bad = q.get('bad_answer', '')
                lines.append(f"❓ {question}")
                if why:
                    lines.append(f"   Цель: {why}")
                if good:
                    lines.append(f"   ✅ {good[:50]}")
                if bad:
                    lines.append(f"   ❌ {bad[:50]}")
                lines.append("")
            elif isinstance(q, str):
                lines.append(f"• {q}")
        return "\n".join(lines).strip() if lines else "—"

    # Data
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 3
        v = raw(analysis, 'verdict', 'YELLOW')
        fill_v, color_v, symbol = verdict_style(v)
        score = raw(analysis, 'score') or raw(analysis, 'rank_score') or 0
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
        score_color = PALETTE['green'] if score >= 70 else (PALETTE['amber'] if score >= 45 else PALETTE['coral'])
        cell_style(c, font=Font(name='Segoe UI', size=11, bold=True, color=score_color), fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 5: Must-have check
        must_have = raw(analysis, 'must_have', [])
        c = ws.cell(row=row, column=5, value=format_must_have(must_have))
        # Color based on status
        missing = sum(1 for m in (must_have or []) if isinstance(m, dict) and m.get('status') == 'MISSING')
        mh_color = PALETTE['coral'] if missing > 0 else PALETTE['green']
        cell_style(c, font=Font(name='Segoe UI', size=9, color=mh_color), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 6: Skills check (with ghost detection)
        skills = raw(analysis, 'skills_check', [])
        c = ws.cell(row=row, column=6, value=format_skills_check(skills))
        ghost_count = sum(1 for s in (skills or []) if isinstance(s, dict) and s.get('ghost'))
        sk_color = PALETTE['coral'] if ghost_count >= 3 else (PALETTE['amber'] if ghost_count > 0 else PALETTE['green'])
        cell_style(c, font=Font(name='Segoe UI', size=9, color=sk_color), fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 7: Плюсы (strengths)
        strengths = raw(analysis, 'strengths', []) or raw(analysis, 'pros', [])
        c = ws.cell(row=row, column=7, value=bullets(strengths, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 8: Минусы (concerns)
        concerns = raw(analysis, 'concerns', []) or raw(analysis, 'cons', [])
        c = ws.cell(row=row, column=8, value=bullets(concerns, 4))
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 9: Interview Questions (with good/bad)
        questions = raw(analysis, 'interview_questions', [])
        c = ws.cell(row=row, column=9, value=format_questions(questions))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['navy']), fill=row_fill, align=ALIGN['top'], border=BORDER)

        ws.row_dimensions[row].height = 110

    ws.auto_filter.ref = f"A3:I{len(results) + 3}"

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)
    temp.close()
    return temp.name
