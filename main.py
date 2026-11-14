#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from html import escape
from datetime import datetime, date

path_to_todos = Path.home() / ".todos.json"

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
    subject = escape(subject)
    for p in projects:
        token = escape(f"+{p}")
        subject = subject.replace(token, f'<span style="color:{color_project};">{token}</span>')
    for c in contexts:
        token = escape(f"@{c}")
        subject = subject.replace(token, f'<span style="color:{color_context};">{token}</span>')
    style = f"color:{color_subject};"
    if completed:
        style += "text-decoration:line-through;opacity:0.6;"
    return f'<span style="{style}">{subject}</span>'


def render_todos(data):
    if not isinstance(data, list):
        raise ValueError("Expected a todo array")
    rows = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Expected a todo object")
        if not isinstance(item['subject'], str):
            raise ValueError("Expected a subject string")
        if not all(isinstance(item[field], list) and all(isinstance(v, str) for v in item[field])
                   for field in ('projects', 'contexts')):
            raise ValueError("Expected project/context arrays")
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
    return "<div>" + "".join(rows) + "</div>"


def build_output(path=None):
    path = path_to_todos if path is None else Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return render_todos(data)
    except FileNotFoundError:
        message = "ultralist: ~/.todos.json not found.<br>Run: ultralist init"
    except OSError:
        message = "ultralist: Unable to read ~/.todos.json. Check file permissions."
    except (ValueError, TypeError, KeyError, UnicodeError):
        message = "ultralist: Invalid todo data. Check JSON, required fields and due dates."
    return f'<span style="color:{color_due_overdue};">{message}</span>'


if __name__ == "__main__":
    sys.stdout.buffer.write(build_output().encode("utf-8"))
