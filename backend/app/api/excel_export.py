"""
Excel экспорт v10.0 — HR отчёт для AI Analyzer v7.0 (Hybrid Expert)

Design: Dark Industrial — монохром с акцентами
Формат: Вердикты High/Medium/Low/Mismatch + Must-haves + Reasoning

2 вкладки:
- Шортлист: Быстрый обзор кандидатов за 30 секунд
- Полный анализ: reasoning_for_hr, must-haves, вопросы с checks
"""
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
import tempfile
import json


def create_excel_export(vacancy, results: list, recommendation_filter: Optional[str] = None) -> str:
    """Excel v10.0 — под AI v7.0 Hybrid Expert"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import DataBarRule

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    shortlist_ws = wb.create_sheet("Шортлист", 0)
    deep_ws = wb.create_sheet("Полный анализ", 1)

    # ══════════════════════════════════════════════════════════════
    # DESIGN SYSTEM — Dark Industrial
    # Монохромная база (zinc) + яркие акценты для вердиктов
    # ══════════════════════════════════════════════════════════════

    PALETTE = {
        # Base — Dark Industrial
        'ink': '18181B',       # zinc-900 — заголовки
        'charcoal': '27272A',  # zinc-800 — header bg
        'steel': '3F3F46',     # zinc-700 — secondary
        'slate': '71717A',     # zinc-500 — muted text
        'silver': 'A1A1AA',    # zinc-400 — subtle
        'cloud': 'F4F4F5',     # zinc-100 — row alt
        'white': 'FFFFFF',
        'border': 'E4E4E7',    # zinc-200

        # Verdict accents — Bold & Clear
        'emerald': '059669',      # High — рекомендую
        'emerald_bg': 'D1FAE5',
        'blue': '2563EB',         # Medium — на рассмотрение
        'blue_bg': 'DBEAFE',
        'amber': 'D97706',        # Low — сомнительно
        'amber_bg': 'FEF3C7',
        'red': 'DC2626',          # Mismatch — не подходит
        'red_bg': 'FEE2E2',
    }

    # Typography — Clean & Professional
    FONT = {
        'title': Font(name='Segoe UI Semibold', size=16, bold=True, color=PALETTE['ink']),
        'subtitle': Font(name='Segoe UI', size=10, color=PALETTE['slate']),
        'header': Font(name='Segoe UI Semibold', size=9, bold=True, color=PALETTE['white']),
        'name': Font(name='Segoe UI Semibold', size=11, bold=True, color=PALETTE['ink']),
        'body': Font(name='Segoe UI', size=10, color=PALETTE['steel']),
        'small': Font(name='Segoe UI', size=9, color=PALETTE['slate']),
        'link': Font(name='Segoe UI', size=10, color=PALETTE['blue'], underline='single'),
        'reasoning': Font(name='Segoe UI', size=10, color=PALETTE['ink']),
    }

    FILL = {
        'header': PatternFill(start_color=PALETTE['charcoal'], fill_type="solid"),
        'cloud': PatternFill(start_color=PALETTE['cloud'], fill_type="solid"),
        'white': PatternFill(start_color=PALETTE['white'], fill_type="solid"),
        # Verdict backgrounds
        'high': PatternFill(start_color=PALETTE['emerald_bg'], fill_type="solid"),
        'medium': PatternFill(start_color=PALETTE['blue_bg'], fill_type="solid"),
        'low': PatternFill(start_color=PALETTE['amber_bg'], fill_type="solid"),
        'mismatch': PatternFill(start_color=PALETTE['red_bg'], fill_type="solid"),
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
        """Получить значение из raw_result"""
        r = getattr(analysis, 'raw_result', None) or {}
        return r.get(key, default)

    def get_verdict(analysis):
        """Получить вердикт v7.0 или смапить из старого формата"""
        v = raw(analysis, 'verdict')
        if v in ['High', 'Medium', 'Low', 'Mismatch']:
            return v
        # Маппинг старых значений
        old_v = raw(analysis, 'verdict', '')
        if old_v == 'GREEN':
            return 'High'
        elif old_v == 'YELLOW':
            return 'Medium'
        elif old_v == 'RED':
            return 'Low'
        # По score если нет verdict
        score = raw(analysis, 'score', 0) or 0
        if score >= 75:
            return 'High'
        elif score >= 50:
            return 'Medium'
        elif score >= 25:
            return 'Low'
        return 'Mismatch'

    def verdict_display(v):
        """Вердикт → (label_ru, fill, color, icon)"""
        return {
            'High': ('Рекомендую', FILL['high'], PALETTE['emerald'], '★'),
            'Medium': ('На рассмотрение', FILL['medium'], PALETTE['blue'], '◆'),
            'Low': ('Сомнительно', FILL['low'], PALETTE['amber'], '▲'),
            'Mismatch': ('Не подходит', FILL['mismatch'], PALETTE['red'], '✕'),
        }.get(v, ('—', FILL['white'], PALETTE['slate'], '?'))

    def get_priority(analysis):
        """Получить приоритет v7.2"""
        p = raw(analysis, 'priority', 'basic')
        return p if p in ['top', 'strong', 'basic'] else 'basic'

    def priority_stars(p):
        """Приоритет → звёзды"""
        return {'top': '★★★', 'strong': '★★', 'basic': '★'}.get(p, '★')

    def get_one_liner(analysis):
        """Получить one_liner или fallback"""
        one = raw(analysis, 'one_liner', '')
        if one:
            return one
        # Fallback to verdict_reason
        return raw(analysis, 'verdict_reason', '') or ''

    def get_salary_from_resume(app):
        """Получить зарплату из резюме кандидата"""
        resume = app.resume_data or {}
        if isinstance(resume, str):
            try:
                resume = json.loads(resume)
            except:
                return None
        salary = resume.get('salary', {})
        if isinstance(salary, dict):
            amount = salary.get('amount', 0) or salary.get('from', 0) or 0
            if amount:
                return int(amount * 1.15)  # NET → GROSS
        return None

    def has_cover_letter(app):
        """Проверить наличие сопроводительного письма"""
        resume = app.resume_data or {}
        if isinstance(resume, str):
            try:
                resume = json.loads(resume)
            except:
                return False
        cover = resume.get('cover_letter', '') or resume.get('message', '')
        return bool(cover and len(str(cover).strip()) > 10)

    def bullets(items, max_n=5):
        if not items:
            return "—"
        if isinstance(items, str):
            return items
        return "\n".join([f"• {i}" for i in items[:max_n] if i])

    def cell_style(cell, font=None, fill=None, align=None, border=None):
        if font:
            cell.font = font
        if fill:
            cell.fill = fill
        if align:
            cell.alignment = align
        if border:
            cell.border = border

    def format_must_haves_v7(must_haves):
        """Форматирование must-haves v7.0 (yes/maybe/no)"""
        if not must_haves:
            return "—"
        lines = []
        for m in must_haves[:5]:
            if isinstance(m, dict):
                req = m.get('requirement', '')
                status = m.get('status', 'no')
                icon = '✓' if status == 'yes' else ('?' if status == 'maybe' else '✗')
                evidence = m.get('evidence', '') or ''
                line = f"{icon} {req}"
                if evidence:
                    line += f"\n   → {evidence}"
                lines.append(line)
        return "\n".join(lines) if lines else "—"

    def format_interview_questions_v7(questions):
        """Форматирование вопросов v7.0 (question + checks)"""
        if not questions:
            return "—"
        lines = []
        for i, q in enumerate(questions[:4], 1):
            if isinstance(q, dict):
                question = q.get('question', '')
                checks = q.get('checks', '')
                lines.append(f"{i}. {question}")
                if checks:
                    lines.append(f"   Проверяем: {checks}")
                lines.append("")
            elif isinstance(q, str):
                lines.append(f"{i}. {q}")
        return "\n".join(lines).strip() if lines else "—"

    def format_growth_pattern(pattern):
        """Траектория карьеры"""
        return {
            'растёт': '↗ Растёт',
            'стабилен': '→ Стабилен',
            'деградирует': '↘ Деградирует',
            'непонятно': '? Непонятно',
        }.get(pattern, '—')

    def format_salary_fit(salary_fit):
        """Соответствие зарплаты"""
        if not salary_fit:
            return "—"
        if isinstance(salary_fit, dict):
            status = salary_fit.get('status', '')
            comment = salary_fit.get('comment', '')
            return f"{status}" + (f" ({comment})" if comment else "")
        return str(salary_fit)

    # ══════════════════════════════════════════════════════════════
    # STATISTICS
    # ══════════════════════════════════════════════════════════════

    total = len(results)
    high_n = len([r for r, _ in results if get_verdict(r) == 'High'])
    medium_n = len([r for r, _ in results if get_verdict(r) == 'Medium'])
    low_n = len([r for r, _ in results if get_verdict(r) == 'Low'])
    mismatch_n = total - high_n - medium_n - low_n

    # Сортировка: High+top → High+strong → High+basic → Medium → Low → Mismatch
    def sort_key(item):
        v = get_verdict(item[0])
        p = get_priority(item[0])
        verdict_order = {'High': 0, 'Medium': 1, 'Low': 2, 'Mismatch': 3}
        priority_order = {'top': 0, 'strong': 1, 'basic': 2}
        score = raw(item[0], 'score', 0) or 0
        return (verdict_order.get(v, 3), priority_order.get(p, 2), -score)

    sorted_results = sorted(results, key=sort_key)

    # ══════════════════════════════════════════════════════════════
    # SHEET 1: ШОРТЛИСТ — Быстрый обзор за 30 секунд
    # ══════════════════════════════════════════════════════════════
    ws = shortlist_ws

    # Column widths v7.2: Приоритет | Кандидат | Вердикт | Зарплата | Письмо | Почему этот кандидат
    widths = {'A': 6, 'B': 22, 'C': 14, 'D': 14, 'E': 7, 'F': 70}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title row
    ws.merge_cells('A1:F1')
    c = ws.cell(row=1, column=1, value=vacancy.title)
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 36

    # Stats bar v7.2
    ws.merge_cells('A2:F2')
    # Count top priority
    top_count = len([r for r, _ in results if get_verdict(r) == 'High' and get_priority(r) == 'top'])
    stats = f"★★★ {top_count} топ   │   ★ {high_n} рекомендую   ◆ {medium_n} рассмотреть   ▲ {low_n} сомнительно   ✕ {mismatch_n} нет   │   {total} всего"
    c = ws.cell(row=2, column=1, value=stats)
    cell_style(c, font=FONT['subtitle'], align=ALIGN['center'], fill=FILL['cloud'])
    ws.row_dimensions[2].height = 26

    # Spacer
    ws.row_dimensions[3].height = 6

    # Headers v7.2
    headers = ['★', 'КАНДИДАТ', 'ВЕРДИКТ', 'ЗАРПЛАТА', '📝', 'ПОЧЕМУ ЭТОТ КАНДИДАТ']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=4, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[4].height = 28
    ws.freeze_panes = 'A5'

    # Data rows v7.2
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 4
        verdict = get_verdict(analysis)
        priority = get_priority(analysis)
        label_ru, fill_v, color_v, icon = verdict_display(verdict)
        row_fill = FILL['white'] if idx % 2 else FILL['cloud']

        # Col 1: Priority stars (только для High)
        if verdict == 'High':
            stars = priority_stars(priority)
            c = ws.cell(row=row, column=1, value=stars)
            cell_style(c, font=Font(name='Segoe UI', size=11, color=PALETTE['amber']),
                       fill=row_fill, align=ALIGN['center'], border=BORDER)
        else:
            c = ws.cell(row=row, column=1, value=icon)
            cell_style(c, font=Font(name='Segoe UI', size=12, color=color_v),
                       fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Col 2: Name (with link)
        name = app.candidate_name or "—"
        c = ws.cell(row=row, column=2, value=name)
        if app.resume_url:
            c.hyperlink = app.resume_url
            cell_style(c, font=FONT['link'], fill=row_fill, align=ALIGN['left'], border=BORDER)
        else:
            cell_style(c, font=FONT['name'], fill=row_fill, align=ALIGN['left'], border=BORDER)

        # Col 3: Verdict label
        c = ws.cell(row=row, column=3, value=label_ru)
        cell_style(c, font=Font(name='Segoe UI Semibold', size=10, bold=True, color=color_v),
                   fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Col 4: Salary from resume
        salary = get_salary_from_resume(app)
        if salary:
            salary_text = f"{salary:,}".replace(',', ' ') + " ₽"
        else:
            salary_text = "—"
        c = ws.cell(row=row, column=4, value=salary_text)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 5: Cover letter indicator
        has_cover = has_cover_letter(app)
        c = ws.cell(row=row, column=5, value="✓" if has_cover else "—")
        cover_color = PALETTE['emerald'] if has_cover else PALETTE['slate']
        cell_style(c, font=Font(name='Segoe UI', size=10, color=cover_color),
                   fill=row_fill, align=ALIGN['center'], border=BORDER)

        # Col 6: One-liner (почему этот кандидат)
        one_liner = get_one_liner(analysis)
        c = ws.cell(row=row, column=6, value=one_liner or "—")
        cell_style(c, font=FONT['reasoning'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        ws.row_dimensions[row].height = 52

    ws.auto_filter.ref = f"A4:F{len(results) + 4}"

    # ══════════════════════════════════════════════════════════════
    # SHEET 2: ПОЛНЫЙ АНАЛИЗ — v7.0 Hybrid Expert
    # ══════════════════════════════════════════════════════════════
    ws = deep_ws

    # Columns: № | КАНДИДАТ | ВЕРДИКТ | MUST-HAVES | РЕЗЮМЕ КАРЬЕРЫ | ПЛЮСЫ/МИНУСЫ | ВОПРОСЫ
    widths = {'A': 4, 'B': 18, 'C': 14, 'D': 36, 'E': 42, 'F': 32, 'G': 48}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells('A1:G1')
    c = ws.cell(row=1, column=1, value=f"Полный анализ: {vacancy.title}")
    cell_style(c, font=FONT['title'], align=ALIGN['center'])
    ws.row_dimensions[1].height = 36

    # Spacer
    ws.row_dimensions[2].height = 6

    # Headers
    headers = ['№', 'КАНДИДАТ', 'ВЕРДИКТ', 'MUST-HAVES', 'АНАЛИЗ КАРЬЕРЫ', 'ОЦЕНКА', 'ВОПРОСЫ ДЛЯ ИНТЕРВЬЮ']
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=i, value=h)
        cell_style(c, font=FONT['header'], fill=FILL['header'], align=ALIGN['center'], border=BORDER)
    ws.row_dimensions[3].height = 28
    ws.freeze_panes = 'C4'

    # Data
    for idx, (analysis, app) in enumerate(sorted_results, 1):
        row = idx + 3
        verdict = get_verdict(analysis)
        label_ru, fill_v, color_v, icon = verdict_display(verdict)
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

        # Col 3: Verdict
        verdict_text = f"{icon} {label_ru}"
        c = ws.cell(row=row, column=3, value=verdict_text)
        cell_style(c, font=Font(name='Segoe UI Semibold', size=10, bold=True, color=color_v),
                   fill=fill_v, align=ALIGN['center'], border=BORDER)

        # Col 4: Must-haves v7.0
        must_haves = raw(analysis, 'must_haves', []) or raw(analysis, 'must_have', [])
        c = ws.cell(row=row, column=4, value=format_must_haves_v7(must_haves))
        # Color by status
        no_count = sum(1 for m in (must_haves or []) if isinstance(m, dict) and m.get('status') == 'no')
        mh_color = PALETTE['red'] if no_count > 0 else PALETTE['emerald']
        cell_style(c, font=Font(name='Segoe UI', size=9, color=mh_color),
                   fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 5: Career analysis (holistic + reasoning)
        holistic = raw(analysis, 'holistic_analysis', {}) or {}
        career_summary = holistic.get('career_summary', '') if isinstance(holistic, dict) else ''
        relevance = holistic.get('relevance_assessment', '') if isinstance(holistic, dict) else ''
        growth = holistic.get('growth_pattern', '') if isinstance(holistic, dict) else ''
        reasoning = raw(analysis, 'reasoning_for_hr', '') or ''

        career_text_parts = []
        if career_summary:
            career_text_parts.append(f"Карьера: {career_summary}")
        if relevance:
            career_text_parts.append(f"Релевантность: {relevance}")
        if growth:
            career_text_parts.append(f"Траектория: {format_growth_pattern(growth)}")
        if reasoning:
            career_text_parts.append(f"\n{reasoning}")

        career_text = "\n".join(career_text_parts) if career_text_parts else "—"
        c = ws.cell(row=row, column=5, value=career_text)
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 6: Pros/Cons + Concerns + Salary
        concerns = raw(analysis, 'concerns', []) or []
        salary_fit = raw(analysis, 'salary_fit', None)
        strengths = raw(analysis, 'strengths', []) or raw(analysis, 'pros', []) or []
        weaknesses = raw(analysis, 'weaknesses', []) or raw(analysis, 'cons', []) or []

        assessment_parts = []
        if strengths:
            assessment_parts.append("Плюсы:\n" + bullets(strengths, 3))
        if weaknesses or concerns:
            all_concerns = list(weaknesses) + list(concerns)
            assessment_parts.append("Минусы:\n" + bullets(all_concerns, 3))
        if salary_fit:
            assessment_parts.append(f"Зарплата: {format_salary_fit(salary_fit)}")

        c = ws.cell(row=row, column=6, value="\n\n".join(assessment_parts) if assessment_parts else "—")
        cell_style(c, font=FONT['body'], fill=row_fill, align=ALIGN['top'], border=BORDER)

        # Col 7: Interview Questions v7.0 (with checks)
        questions = raw(analysis, 'interview_questions_v7', []) or raw(analysis, 'interview_questions', [])
        c = ws.cell(row=row, column=7, value=format_interview_questions_v7(questions))
        cell_style(c, font=Font(name='Segoe UI', size=9, color=PALETTE['ink']),
                   fill=row_fill, align=ALIGN['top'], border=BORDER)

        ws.row_dimensions[row].height = 130

    ws.auto_filter.ref = f"A3:G{len(results) + 3}"

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)
    temp.close()
    return temp.name
