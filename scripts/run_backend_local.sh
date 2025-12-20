#!/bin/bash
source /home/badr/.local/share/mamba/etc/profile.d/mamba.sh
mamba activate bookgen-ai

cd backend

echo "Starting Backend on port 8000..."
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
