#!/bin/bash
cd backend
source venv/bin/activate

echo "Starting Backend on port 8000..."
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
