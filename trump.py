from configparser import ConfigParser
import os
import sys
import logging
import json

import yaml
from flask import Flask
from flask_cors import CORS

def create_app(logPath):
    sys.path.insert(0, "/Users/ashwaheg/Desktop/4trump/")
    app = Flask(__name__)
    CORS(app)
    config_file_name = "app_info.conf"
    app_config = ConfigParser()
    if os.path.isfile(config_file_name):
        app_config.read(config_file_name)
    else:
        raise FileNotFoundError

    for section in app_config.sections():
        for options in app_config.options(section):
            app.config[options] = app_config.get(section, options)

    from bluep.state import state_blueprint
    app.register_blueprint(state_blueprint, url_prefix='/state')

    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    rotationHandler = logging.handlers.TimedRotatingFileHandler(logPath,
                                       when="H",
                                       interval=1,
                                       backupCount=30)
    logFormatter = logging.Formatter(
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        #fmt='%(asctime)s.%(msecs)03d %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
        )
    rotationHandler.setFormatter(logFormatter)
    gunicorn_error_logger.addHandler(rotationHandler)
    app.logger.setLevel(logging.INFO)
    gunicorn_error_logger.info("App is being started.")
    return app
