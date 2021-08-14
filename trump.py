from configparser import ConfigParser
import os
import sys
import logging
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager


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
    app.config["SECRET_KEY"] = app.config["secret_key"]

    # create db
    if not os.path.isfile(app.config["sqlitedb"]):
        with app.app_context():
            from utils.db import init_db
            init_db()
    with app.app_context():
        from bluep.db import db_blueprint
        app.register_blueprint(db_blueprint, url_prefix='/db')
    from bluep.state import state_blueprint
    app.register_blueprint(state_blueprint, url_prefix='/state')
    from bluep.webpages import ui_blueprint
    app.register_blueprint(ui_blueprint, url_prefix='/')

    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    rotationHandler = logging.handlers.TimedRotatingFileHandler(
        logPath,
        when="H",
        interval=1,
        backupCount=30,
    )
    logFormatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        # fmt='%(asctime)s.%(msecs)03d %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    rotationHandler.setFormatter(logFormatter)
    gunicorn_error_logger.addHandler(rotationHandler)
    app.logger.setLevel(logging.INFO)
    gunicorn_error_logger.info("App is being started.")
    # login part
    login = LoginManager(app)
    login.login_view = 'state_blueprint.login'

    from utils.db import check_user
    from utils.user import User

    @login.user_loader
    def load_user(id):
        if check_user(id):
            return User(id=id)
        else:
            return None
    return app
