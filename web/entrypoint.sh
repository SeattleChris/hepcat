#!/bin/bash

# Move this file to /web directory?
# change PROJECT to correct project name
# chmod to allow this to run the script

set -e

cd /src

echo "======================== Collect static files ========================"
python manage.py collectstatic --noinput
# echo "======================== Skip Make migration files ========================"
python manage.py makemigrations --noinput
echo "============================= Migrate DB ============================="
python manage.py migrate --noinput

python manage.py runserver 0.0.0.0:8000
# gunicorn hepcat.wsgi:application -w 3 -b :8000
