import sqlite3
from flask import g, current_app, Blueprint

db_blueprint = Blueprint('db_blueprint', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config["sqlitedb"])
    return g.db

@current_app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        current_app.logger.info(f"Closing the DB connection: {exception}")
        db.close()
