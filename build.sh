#!/bin/sh
set -e # stops execution on error
rm -rf jatszohaz/migrations
python jatszohaz/manage.py makemigrations
python jatszohaz/manage.py migrate
python jatszohaz/manage.py test
