#!/bin/bash
# Creates log files
hmda_data_app_log_dir='/var/log/self-hosted-hmda-data-app/logs'
touch "$hmda_data_app_log_dir/celery_hmda_data_app.log"
touch "$hmda_data_app_log_dir/gunicorn_hmda_data_app.log"
# Runs celery and gunicorn
celery --app hmda_data_app.tasks worker --detach --logfile="$hmda_data_app_log_dir/celery_hmda_data_app.log" --loglevel=WARNING
gunicorn --config /self-hosted-hmda-data-app/gunicorn.conf.py --log-file="$hmda_data_app_log_dir/gunicorn_hmda_data_app.log" --log-level="warning"
