"""
This script runs the hmda data application using a development server.
"""

from os import environ
from hmda_data_app import flask_app

if __name__ == '__main__':
    # WARNING IF DEBUGGING IS ENABLED YOU NEED TO SET THIS TO
    # 127.0.0.1 SO YOUR COMPUTER IS NOT ATTACKED
    # This tests it:
    if not flask_app.config['DEBUG']:
        HOST = "0.0.0.0"
        try:
            PORT = int(environ.get('PORT', '5000'))
        except ValueError:
            PORT = 5000
        flask_app.run(HOST, PORT)
