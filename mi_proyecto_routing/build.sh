#!/usr/bin/env bash
set -o errexit
set -o nounset

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input
# El plan Free no ofrece pre-deploy command ni consola Shell.
python manage.py migrate --no-input
python manage.py initialize_deployment
