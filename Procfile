web: gunicorn security_hr_system.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --noinput
release: python manage.py collectstatic --noinput
