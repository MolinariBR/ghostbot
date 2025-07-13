#!/bin/bash
# Script para auto-reload do GhostBot durante desenvolvimento

source $(dirname "$0")/.venv/bin/activate
exec watchmedo auto-restart --patterns="*.py" --recursive -- $(dirname "$0")/.venv/bin/python bot.py
