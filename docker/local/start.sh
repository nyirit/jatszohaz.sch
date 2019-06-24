#!/bin/bash
set -o errexit
set -o xtrace

source jh/bin/activate

cd jatszohaz.sch
pip install -r requirements.txt -r requirements/dev.txt --upgrade

cd jatszohaz
python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear
python3 manage.py compilemessages

python3 manage.py create_dev_admin

python3 manage.py runserver [::]:8000

