#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings.prod

python manage.py collectstatic --no-input
python manage.py migrate --no-input
