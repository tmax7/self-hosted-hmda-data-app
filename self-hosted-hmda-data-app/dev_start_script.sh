#!/bin/bash
# Creates log files
mkdir /logs
touch /logs/celery_hmda_data_app.log
touch /logs/gunicorn_hmda_data_app.log
# Runs celery and gunicorn
celery --app hmda_data_app.tasks worker --detach --logfile=/logs/celery_hmda_data_app.log --loglevel=WARNING
gunicorn --config /self-hosted-hmda-data-app/gunicorn.conf.py