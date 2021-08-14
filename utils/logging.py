from flask import current_app
from flask_login import current_user


def infoLogger(message):
    userId = current_user.userId
    if not userId:
        userId = "anonymousUser"
    current_app.logger.info(f'U={userId} M={message}')
