import requests
import json
from flask import Blueprint, jsonify, current_app, request

from utils.etc import send_text_email
from utils.authentication import generate_otp
state_blueprint = Blueprint('state_blueprint', __name__)

@state_blueprint.route("/ping")
def ping_the_app():
    current_app.logger.info("pinged")
    return jsonify("this app is up."),200

@state_blueprint.route("/sendotp")
def send_otp():
    otp = generate_otp()
    body = f"""access code: {otp}
    """
    title = "verify account"
    state,message = send_text_email("8ash0hegde@gmail.com", title, body)
    if state:
        return jsonify(message),200
    else:
        return jsonify(message),400
