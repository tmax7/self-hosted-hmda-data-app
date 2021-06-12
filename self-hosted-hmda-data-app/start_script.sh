#!/bin/bash
celery --app hmda_data_app.tasks worker --detach --logfile=./logs/celery_hmda_data_app.log --loglevel=WARNING
gunicorn --config ./gunicorn.conf.py
