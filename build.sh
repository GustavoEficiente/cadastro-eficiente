#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); username='gustavo'; email='seuemail@email.com'; password='12345678'; User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"