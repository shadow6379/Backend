#!/bin/bash
set -e

if [ "$ENV" = 'DEV' ]; then
	echo "Running Development Server"
	exec python manage.py runserver 0.0.0.0:8000
elif [ "$ENV" = 'UNIT' ]; then
	echo "Running Unit Tests"
	exec python manage.py test
else
	echo "Running Production Server"
	exec uwsgi --http 0.0.0.0:8000 --module web_server.wsgi
fi

