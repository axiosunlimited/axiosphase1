#!/usr/bin/env sh
set -e

python manage.py makemigrations --noinput
python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '${DJANGO_SUPERUSER_EMAIL}'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password='${DJANGO_SUPERUSER_PASSWORD}',
        first_name='${DJANGO_SUPERUSER_FIRST_NAME:-System}',
        last_name='${DJANGO_SUPERUSER_LAST_NAME:-Admin}',
    )
    print('Created dev superuser:', email)
else:
    print('Dev superuser already exists:', email)
"
fi

python manage.py runserver 0.0.0.0:8000
