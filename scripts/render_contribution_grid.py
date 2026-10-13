#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

src = Path("contributions.json")
out = Path("dist")
out.mkdir(exist_ok=True)
data = json.loads(src.read_text(encoding="utf-8"))
user = data["data"]["user"]
collection = user["contributionsCollection"]
calendar = collection["contributionCalendar"]
weeks = calendar["weeks"]
total = int(calendar["totalContributions"])
restricted = int(collection.get("restrictedContributionsCount", 0))

cell, gap, step = 11, 3, 14
pad_x, pad_y = 16, 30
cols = len(weeks)
width = pad_x * 2 + cols * step - gap
height = pad_y * 2 + 7 * step - gap
levels = {"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}

rects, active, days = [], [], []
for x, week in enumerate(weeks):
    for d in week["contributionDays"]:
        y = int(d["weekday"])
        count = int(d["contributionCount"])
        level = levels.get(d["contributionLevel"], 0)
        px, py = pad_x + x * step, pad_y + y * step
        plural = "" if count == 1 else "s"
        rects.append(f'<g><title>{d["date"]}: {count} contribution{plural}</title><rect class="d l{level}" x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2"/></g>')
        if count > 0:
            active.append((px + cell/2, py + cell/2))
        days.append((date.fromisoformat(d["date"]), count))

active_days = sum(1 for _, c in days if c > 0)


def streaks(items):
    longest = 0
    longest_start = longest_end = None
    run = 0
    run_start = None
    prev = None
    for dt, count in items:
        if count > 0:
            if run == 0 or (prev and (dt-prev).days != 1):
                run = 0
                run_start = dt
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, run_start, dt
        else:
            run = 0
            run_start = None
        prev = dt

    current = 0
    current_start = current_end = None
    if items and items[-1][1] > 0:
        prev = None
        for dt, count in reversed(items):
            if count <= 0 or (prev and (prev-dt).days != 1):
                break
            current += 1
            prev = dt
        current_start = items[-current][0]
        current_end = items[-1][0]
    return current, current_start, current_end, longest, longest_start, longest_end

current, current_start, current_end, longest, longest_start, longest_end = streaks(days)


def fmt(dt):
    return dt.strftime("%d %b %Y") if dt else "-"


def snake_markup():
    if not active:
        return ""
    duration = max(10.0, min(28.0, len(active) * .18))
    total_pts = max(1, len(active)-1)
    css = ["<style>", "@keyframes snakeMove{"]
    for i, (x, y) in enumerate(active):
        pct = i / total_pts * 100
        css.append(f"{pct:.2f}%{{transform:translate({x:.1f}px,{y:.1f}px)}}")
    css.append("}")
    specs = [(5.2,"#a855f7"),(4.7,"#9333ea"),(4.2,"#7e22ce"),(3.8,"#6b21a8"),(3.4,"#581c87"),(3.0,"#4c1d95"),(2.6,"#f97316")]
    for i in range(len(specs)):
        delay = i * duration / 18
        css.append(f".s{i}{{animation:snakeMove {duration:.1f}s linear infinite;animation-delay:-{delay:.2f}s;transform-box:fill-box;transform-origin:center}}")
    css.append("</style>")
    parts = ["".join(css)]
    parts.append('<g class="s0"><circle cx="0" cy="0" r="5.2" fill="#a855f7"/><circle cx="1.6" cy="-1.4" r=".9" fill="#fff"/><circle cx="1.6" cy="1.4" r=".9" fill="#fff"/><circle cx="2" cy="-1.4" r=".35" fill="#111827"/><circle cx="2" cy="1.4" r=".35" fill="#111827"/></g>')
    for i, (r, color) in enumerate(specs[1:], 1):
        parts.append(f'<circle class="s{i}" cx="0" cy="0" r="{r}" fill="{color}"/>')
    return "".join(parts)


def grid_svg(dark):
    if dark:
        bg, empty, border, text, sub = "#0d1117", "#161b22", "#30363d", "#c9d1d9", "#8b949e"
        colors = ["#3b0764","#6b21a8","#a855f7","#f97316"]
    else:
        bg, empty, border, text, sub = "#ffffff", "#ebedf0", "#d0d7de", "#24292f", "#57606a"
        colors = ["#ede9fe","#c4b5fd","#a855f7","#f97316"]
    style = f'<style>.bg{{fill:{bg}}}.d{{stroke:{border};stroke-width:.6}}.l0{{fill:{empty}}}.l1{{fill:{colors[0]}}}.l2{{fill:{colors[1]}}}.l3{{fill:{colors[2]}}}.l4{{fill:{colors[3]}}}.meta{{fill:{text};font:700 11px Segoe UI,Arial,sans-serif}}.sub{{fill:{sub};font:11px Segoe UI,Arial,sans-serif}}</style>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">{style}<rect class="bg" width="100%" height="100%"/><text class="meta" x="{pad_x}" y="15">{total} contributions in the last year</text><text class="sub" x="{width-160}" y="15">{active_days} active days</text>'+''.join(rects)+snake_markup()+'</svg>'


def stats_svg(dark):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#c9d1d9" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    border = "#30363d" if dark else "#d0d7de"
    repos = user["repositories"]["totalCount"]
    followers = user["followers"]["totalCount"]
    values = [(repos,"Repositorios publicos","#a855f7"),(total,"Contribuicoes no ano","#f97316"),(followers,"Seguidores","#a855f7"),(active_days,"Dias ativos","#f97316")]
    cards=[]
    for i,(value,label,color) in enumerate(values):
        x=22+i*183
        cards.append(f'<rect x="{x}" y="82" width="168" height="72" rx="12" fill="none" stroke="{border}"/><text x="{x+84}" y="114" text-anchor="middle" fill="{color}" font-size="28" font-family="Segoe UI,Arial" font-weight="700">{value}</text><text x="{x+84}" y="137" text-anchor="middle" fill="{muted}" font-size="12" font-family="Segoe UI,Arial">{label}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 176" width="760" height="176"><rect width="760" height="176" rx="14" fill="{bg}" stroke="{border}"/><text x="28" y="36" fill="{fg}" font-size="20" font-family="Segoe UI,Arial" font-weight="700">Raaaif - GitHub Overview</text><text x="28" y="58" fill="{muted}" font-size="12" font-family="Segoe UI,Arial">Metricas geradas pelo proprio workflow do perfil</text>{"".join(cards)}</svg>'


def activity_svg(dark):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#c9d1d9" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    border = "#30363d" if dark else "#d0d7de"
    line, point = "#a855f7", "#f97316"
    vals=[c for _,c in days[-90:]] or [0]
    maxv=max(max(vals),1)
    left,top,w,h=38,48,684,92
    pts=[]
    for i,v in enumerate(vals):
        x=left+w*i/max(1,len(vals)-1)
        y=top+h-h*v/maxv
        pts.append((x,y,v))
    poly=" ".join(f"{x:.1f},{y:.1f}" for x,y,_ in pts)
    area=f"{left},{top+h} {poly} {left+w},{top+h}"
    grids=''.join(f'<line x1="{left}" y1="{top+h*i/4:.1f}" x2="{left+w}" y2="{top+h*i/4:.1f}" stroke="{border}" stroke-dasharray="3 4"/>' for i in range(5))
    lx,ly,lv=pts[-1]
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 190" width="760" height="190"><rect width="760" height="190" rx="14" fill="{bg}" stroke="{border}"/><text x="24" y="28" fill="{fg}" font-size="16" font-family="Segoe UI,Arial" font-weight="700">Atividade visivel - ultimos 90 dias</text><text x="24" y="45" fill="{muted}" font-size="11" font-family="Segoe UI,Arial">Pico: {max(vals)} contribuicao(oes) em um dia</text>{grids}<polygon points="{area}" fill="#a855f733"/><polyline points="{poly}" fill="none" stroke="{line}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{point}"/><text x="{lx-7:.1f}" y="{ly-10:.1f}" fill="{point}" font-size="11" font-family="Segoe UI,Arial">{lv}</text><text x="24" y="173" fill="{muted}" font-size="11" font-family="Segoe UI,Arial">Gerado no proprio workflow do perfil - sem depender de servico externo</text></svg>'


def streak_svg(dark):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#c9d1d9" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    border = "#30363d" if dark else "#d0d7de"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 185" width="760" height="185"><rect width="760" height="185" rx="14" fill="{bg}" stroke="{border}"/><text x="28" y="36" fill="{fg}" font-size="20" font-family="Segoe UI,Arial" font-weight="700">GitHub Streak</text><text x="28" y="58" fill="{muted}" font-size="12" font-family="Segoe UI,Arial">Calculado com os mesmos dados privados usados pela cobrinha</text><line x1="253" y1="78" x2="253" y2="158" stroke="{border}"/><line x1="507" y1="78" x2="507" y2="158" stroke="{border}"/><g font-family="Segoe UI,Arial" text-anchor="middle"><text x="126" y="111" fill="#f97316" font-size="30" font-weight="700">{total}</text><text x="126" y="133" fill="{muted}" font-size="12">Contribuicoes no ano</text><text x="126" y="151" fill="{muted}" font-size="11">{fmt(days[0][0])} - {fmt(days[-1][0])}</text><text x="380" y="111" fill="#a855f7" font-size="30" font-weight="700">{current}</text><text x="380" y="133" fill="{muted}" font-size="12">Current streak</text><text x="380" y="151" fill="{muted}" font-size="11">{fmt(current_start)} - {fmt(current_end)}</text><text x="634" y="111" fill="#f97316" font-size="30" font-weight="700">{longest}</text><text x="634" y="133" fill="{muted}" font-size="12">Longest streak</text><text x="634" y="151" fill="{muted}" font-size="11">{fmt(longest_start)} - {fmt(longest_end)}</text></g></svg>'

(out/"github-contribution-grid-snake.svg").write_text(grid_svg(False),encoding="utf-8")
(out/"github-contribution-grid-snake-dark.svg").write_text(grid_svg(True),encoding="utf-8")
(out/"profile-stats.svg").write_text(stats_svg(False),encoding="utf-8")
(out/"profile-stats-dark.svg").write_text(stats_svg(True),encoding="utf-8")
(out/"activity.svg").write_text(activity_svg(False),encoding="utf-8")
(out/"activity-dark.svg").write_text(activity_svg(True),encoding="utf-8")
(out/"streak.svg").write_text(streak_svg(False),encoding="utf-8")
(out/"streak-dark.svg").write_text(streak_svg(True),encoding="utf-8")
(out/"contribution-summary.json").write_text(json.dumps({"totalContributions":total,"restrictedContributionsCount":restricted,"weeks":cols,"activeDays":active_days,"currentStreak":current,"longestStreak":longest},indent=2),encoding="utf-8")
print(f"Rendered {total} contributions; active days={active_days}; current streak={current}; longest streak={longest}")
