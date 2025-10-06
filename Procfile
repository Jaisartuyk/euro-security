release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn security_hr_system.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
