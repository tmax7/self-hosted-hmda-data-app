"""
The flask application package.
"""
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

flask_app = Flask(__name__)
flask_app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    broker_url='redis://redis-for-hmda-data-app:6379',
    result_backend='redis://redis-for-hmda-data-app:6379'
)

import hmda_data_app.ad_hoc
import hmda_data_app.plot_module
import hmda_data_app.secure_views
