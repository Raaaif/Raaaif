#!/usr/bin/env python3
import json
from pathlib import Path

src = Path("contributions.json")
out = Path("dist")
out.mkdir(exist_ok=True)
data = json.loads(src.read_text(encoding="utf-8"))
user = data["data"]["user"]
collection = user["contributionsCollection"]
calendar = collection["contributionCalendar"]
weeks = calendar["weeks"]
total = calendar["totalContributions"]
restricted = collection.get("restrictedContributionsCount", 0)

cell, gap, step = 11, 3, 14
pad_x, pad_y = 16, 30
cols, rows = len(weeks), 7
width = pad_x * 2 + cols * step - gap
height = pad_y * 2 + rows * step - gap
levels = {"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}
rects=[]
days=[]
for x, week in enumerate(weeks):
    for day in week["contributionDays"]:
        y=int(day["weekday"]); count=int(day["contributionCount"]); level=levels.get(day["contributionLevel"],0)
        px=pad_x+x*step; py=pad_y+y*step
        plural="" if count==1 else "s"
        rects.append(f'<g><title>{day["date"]}: {count} contribution{plural}</title><rect class="d l{level}" x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2"/></g>')
        days.append((day["date"], count))

# CSS-based snake so GitHub renders the animation reliably.
def snake_css():
    x0, x1 = pad_x, pad_x + (cols-1)*step
    y0, y1 = pad_y, pad_y + 6*step
    return f'''<style>
    @keyframes snakeMove {{
      0% {{ transform: translate({x0}px,{y0}px); }}
      32% {{ transform: translate({x1}px,{y0}px); }}
      50% {{ transform: translate({x1}px,{y1}px); }}
      82% {{ transform: translate({x0}px,{y1}px); }}
      100% {{ transform: translate({x0}px,{y0}px); }}
    }}
    .snake1,.snake2,.snake3,.snake4 {{ animation: snakeMove 12s linear infinite; }}
    .snake2 {{ animation-delay:-.16s }} .snake3 {{ animation-delay:-.32s }} .snake4 {{ animation-delay:-.48s }}
    </style>
    <circle class="snake1" cx="0" cy="0" r="5.3" fill="#a855f7"/>
    <circle class="snake2" cx="0" cy="0" r="4.6" fill="#9333ea"/>
    <circle class="snake3" cx="0" cy="0" r="3.9" fill="#7e22ce"/>
    <circle class="snake4" cx="0" cy="0" r="3.2" fill="#f97316"/>'''

def grid_svg(dark):
    if dark:
        bg,empty,border,text="#0d1117","#161b22","#30363d","#c9d1d9"; colors=["#3b0764","#6b21a8","#a855f7","#f97316"]
    else:
        bg,empty,border,text="#ffffff","#ebedf0","#d0d7de","#57606a"; colors=["#ede9fe","#c4b5fd","#a855f7","#f97316"]
    style=f'<style>.bg{{fill:{bg}}}.d{{stroke:{border};stroke-width:.6}}.l0{{fill:{empty}}}.l1{{fill:{colors[0]}}}.l2{{fill:{colors[1]}}}.l3{{fill:{colors[2]}}}.l4{{fill:{colors[3]}}}.meta{{fill:{text};font:11px -apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}}</style>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">{style}<rect class="bg" width="100%" height="100%"/><text class="meta" x="{pad_x}" y="15">{total} contributions in the last year</text>'+''.join(rects)+snake_css()+'</svg>'

# Local stats card: no third-party image host.
def stats_svg(dark=True):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#c9d1d9" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    border = "#30363d" if dark else "#d0d7de"
    purple = "#a855f7"
    orange = "#f97316"
    repos = user["repositories"]["totalCount"]
    followers = user["followers"]["totalCount"]
    following = user["following"]["totalCount"]
    shown_total = total
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 170" width="760" height="170">
      <rect width="760" height="170" rx="12" fill="{bg}" stroke="{border}"/>
      <text x="28" y="38" fill="{fg}" font-size="20" font-family="Segoe UI,Arial" font-weight="700">Raaaif · GitHub</text>
      <text x="28" y="62" fill="{muted}" font-size="12" font-family="Segoe UI,Arial">Resumo do perfil público</text>
      <g font-family="Segoe UI,Arial" text-anchor="middle">
        <text x="115" y="112" fill="{purple}" font-size="28" font-weight="700">{repos}</text><text x="115" y="135" fill="{muted}" font-size="12">Repositórios públicos</text>
        <text x="300" y="112" fill="{orange}" font-size="28" font-weight="700">{shown_total}</text><text x="300" y="135" fill="{muted}" font-size="12">Contribuições visíveis</text>
        <text x="485" y="112" fill="{purple}" font-size="28" font-weight="700">{followers}</text><text x="485" y="135" fill="{muted}" font-size="12">Seguidores</text>
        <text x="645" y="112" fill="{orange}" font-size="28" font-weight="700">{following}</text><text x="645" y="135" fill="{muted}" font-size="12">Seguindo</text>
      </g>
    </svg>'''

# Local activity chart from last 90 visible contribution days.
def activity_svg(dark=True):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#c9d1d9" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    border = "#30363d" if dark else "#d0d7de"
    line = "#a855f7"
    point = "#f97316"
    vals = [c for _,c in days[-90:]] or [0]
    maxv = max(max(vals),1)
    left, top, chart_w, chart_h = 36, 42, 688, 90
    pts=[]
    for i,v in enumerate(vals):
        x = left + (chart_w * i / max(1,len(vals)-1))
        y = top + chart_h - (chart_h * v / maxv)
        pts.append(f"{x:.1f},{y:.1f}")
    lastx,lasty = pts[-1].split(',')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 170" width="760" height="170">
      <rect width="760" height="170" rx="12" fill="{bg}" stroke="{border}"/>
      <text x="28" y="28" fill="{fg}" font-size="16" font-family="Segoe UI,Arial" font-weight="700">Atividade visível · últimos 90 dias</text>
      <polyline points="{' '.join(pts)}" fill="none" stroke="{line}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="{lastx}" cy="{lasty}" r="4" fill="{point}"/>
      <text x="28" y="154" fill="{muted}" font-size="11" font-family="Segoe UI,Arial">Gerado pelo próprio workflow do perfil · sem depender de serviço externo</text>
    </svg>'''

(out/"github-contribution-grid-snake.svg").write_text(grid_svg(False),encoding="utf-8")
(out/"github-contribution-grid-snake-dark.svg").write_text(grid_svg(True),encoding="utf-8")
(out/"profile-stats.svg").write_text(stats_svg(False),encoding="utf-8")
(out/"profile-stats-dark.svg").write_text(stats_svg(True),encoding="utf-8")
(out/"activity.svg").write_text(activity_svg(False),encoding="utf-8")
(out/"activity-dark.svg").write_text(activity_svg(True),encoding="utf-8")
(out/"contribution-summary.json").write_text(json.dumps({"totalContributions":total,"restrictedContributionsCount":restricted,"weeks":cols},indent=2),encoding="utf-8")
print(f"Rendered {total} visible contributions, restricted count: {restricted}, across {cols} weeks")
