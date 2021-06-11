import json
from celery import Celery
import pandas as pd
from hmda_data_app.ad_hoc import as_PlotOption

from hmda_data_app import flask_app
from hmda_data_app import plot_module

def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        backend=flask_app.config['result_backend'],
        broker=flask_app.config['broker_url']
    )
    celery.conf.update(flask_app.config)
    # celery.conf.update(task_serializer="pickle")

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_for_app = make_celery(flask_app)

@celery_for_app.task(bind=True)
def make_dashboard_plot(self, data_frame_json, plot_option_json):
    data_frame =  pd.read_json(data_frame_json)
    plot_option = json.loads(plot_option_json, object_hook=as_PlotOption)
    return plot_module.make_dashboard_plot(data_frame, plot_option)