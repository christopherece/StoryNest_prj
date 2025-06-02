#!/bin/sh

set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL is ready"

# Apply database migrations
python manage.py migrate

# Create superuser if it doesn't exist
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpass

if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print(f"Created superuser: {DJANGO_SUPERUSER_USERNAME}")
END
fi

echo "Starting Django server..."

# Apply makemigrations
echo "Running makemigrations..."
python manage.py makemigrations

# Apply migrations
echo "Running migrate..."
python manage.py migrate

# Create superuser if not exists
echo "Checking/Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()
username = "$DJANGO_SUPERUSER_USERNAME"
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Start the main container command
exec "$@"
