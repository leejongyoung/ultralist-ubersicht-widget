#!/usr/bin/env python3

import json
import sys
import getpass
from datetime import datetime, date

path_to_todos  = "/Users/" + getpass.getuser() + "/.todos.json"

# Display settings
line_spacing   = "10px"
show_completed = False  # Set to True to show completed todos

# Colors
color_id       = "#0099FF"
color_due      = "#f0d847"
color_due_today   = "#FF9500"
color_due_overdue = "#FF3B30"
color_subject  = "#f2f3fa"
color_project  = "#9dd6d8"
color_context  = "#c8c2df"

def format_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%a, %b %d')

def render_id(id):
    label = str(id) if id >= 10 else "0" + str(id)
    return f'<span style="color:{color_id};">{label}&nbsp;&nbsp;</span>'

def render_due(due):
    if not due:
        return ''
    today     = date.today()
    due_date  = datetime.strptime(due, '%Y-%m-%d').date()
    if due_date < today:
        style = f"color:{color_due_overdue};font-weight:bold;"
    elif due_date == today:
        style = f"color:{color_due_today};font-weight:bold;"
    else:
        style = f"color:{color_due};"
    return f'<span style="{style}">{format_date(due)}&nbsp;&nbsp;</span>'

def render_subject(subject, projects, contexts, completed):
    for p in projects:
        subject = subject.replace(f"+{p}", f'<span style="color:{color_project};">+{p}</span>')
    for c in contexts:
        subject = subject.replace(f"@{c}", f'<span style="color:{color_context};">@{c}</span>')
    style = f"color:{color_subject};"
    if completed:
        style += "text-decoration:line-through;opacity:0.6;"
    return f'<span style="{style}">{subject}</span>'

try:
    with open(path_to_todos, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    msg = f'<span style="color:{color_due_overdue};">ultralist: ~/.todos.json not found.<br>Run: ultralist init</span>'
    sys.stdout.buffer.write(msg.encode("utf-8"))
    sys.exit(0)

rows = []
for item in data:
    if item['archived']:
        continue
    if item['completed'] and not show_completed:
        continue
    row = (
        f'<div style="padding-top:{line_spacing};">'
        + render_id(item['id'])
        + render_due(item['due'])
        + render_subject(item['subject'], item['projects'], item['contexts'], item['completed'])
        + '</div>'
    )
    rows.append(row)

out = "<div>" + "".join(rows) + "</div>"
sys.stdout.buffer.write(out.encode("utf-8"))
