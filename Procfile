release: python manage.py migrate
web: gunicorn travel_companion.wsgi:application --log-file - --log-level info
