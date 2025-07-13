#!/bin/bash
# Script para auto-reload do GhostBot durante desenvolvimento

source .venv/bin/activate
watchmedo auto-restart --patterns="*.py" --recursive -- python3 bot.py
