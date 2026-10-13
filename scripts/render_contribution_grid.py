#!/usr/bin/env python3
import json
from pathlib import Path

src = Path("contributions.json")
out = Path("dist")
out.mkdir(exist_ok=True)
data = json.loads(src.read_text(encoding="utf-8"))
collection = data["data"]["user"]["contributionsCollection"]
calendar = collection["contributionCalendar"]
weeks = calendar["weeks"]
total = calendar["totalContributions"]

cell, gap, step = 11, 3, 14
pad_x, pad_y = 16, 30
cols, rows = len(weeks), 7
width = pad_x * 2 + cols * step - gap
height = pad_y * 2 + rows * step - gap
levels = {"NONE":0,"FIRST_QUARTILE":1,"SECOND_QUARTILE":2,"THIRD_QUARTILE":3,"FOURTH_QUARTILE":4}
rects=[]
active=[]
for x, week in enumerate(weeks):
    for day in week["contributionDays"]:
        y=int(day["weekday"]); count=int(day["contributionCount"]); level=levels.get(day["contributionLevel"],0)
        px=pad_x+x*step; py=pad_y+y*step
        plural="" if count==1 else "s"
        rects.append(f'<g><title>{day["date"]}: {count} contribution{plural}</title><rect class="d l{level}" x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2"/></g>')
        if count>0: active.append((px+cell/2,py+cell/2))

def snake():
    if not active: return ""
    pts=active if len(active)>1 else active*2
    path="M "+" L ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    dur=max(7,min(20,len(active)*0.18))
    return f'<path id="snakePath" d="{path}" fill="none" stroke="none"/><circle r="5.2" class="snake-head"><animateMotion dur="{dur:.1f}s" repeatCount="indefinite"><mpath href="#snakePath"/></animateMotion></circle><circle r="3" class="snake-tail" opacity=".75"><animateMotion dur="{dur:.1f}s" begin="-0.35s" repeatCount="indefinite"><mpath href="#snakePath"/></animateMotion></circle>'

def svg(dark):
    if dark:
        bg,empty,border,text="#0d1117","#161b22","#30363d","#c9d1d9"; colors=["#3b0764","#6b21a8","#a855f7","#f97316"]
    else:
        bg,empty,border,text="#ffffff","#ebedf0","#d0d7de","#57606a"; colors=["#ede9fe","#c4b5fd","#a855f7","#f97316"]
    style=f'<style>.bg{{fill:{bg}}}.d{{stroke:{border};stroke-width:.6}}.l0{{fill:{empty}}}.l1{{fill:{colors[0]}}}.l2{{fill:{colors[1]}}}.l3{{fill:{colors[2]}}}.l4{{fill:{colors[3]}}}.snake-head{{fill:#a855f7}}.snake-tail{{fill:#f97316}}.meta{{fill:{text};font:11px -apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}}</style>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">{style}<rect class="bg" width="100%" height="100%"/><text class="meta" x="{pad_x}" y="15">{total} contributions in the last year</text>'+''.join(rects)+snake()+'</svg>'

(out/"github-contribution-grid-snake.svg").write_text(svg(False),encoding="utf-8")
(out/"github-contribution-grid-snake-dark.svg").write_text(svg(True),encoding="utf-8")
(out/"contribution-summary.json").write_text(json.dumps({"totalContributions":total,"weeks":cols},indent=2),encoding="utf-8")
print(f"Rendered {total} contributions across {cols} weeks")
