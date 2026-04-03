#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Create superuser if it doesn't exist
if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '${DJANGO_SUPERUSER_EMAIL}'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password='${DJANGO_SUPERUSER_PASSWORD}',
        first_name='${DJANGO_SUPERUSER_FIRST_NAME:-Admin}',
        last_name='${DJANGO_SUPERUSER_LAST_NAME:-User}',
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi
