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
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_proto=1, x_host=1)

import hmda_data_app.ad_hoc
import hmda_data_app.plot_module
import hmda_data_app.secure_views
