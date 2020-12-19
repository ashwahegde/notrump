import requests
import json
from flask import Blueprint, jsonify, current_app, request
import flask

from utils.etc import send_text_email
from utils.authentication import generate_otp
from utils.db import (insert_row, select_query, update_rows, complex_query,
    check_user, get_passwordHash, init_db, select_query_dict
)


from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from utils.authentication import LoginForm, RegistrationForm, OtpForm

from werkzeug.security import generate_password_hash, check_password_hash

from utils.user import User

state_blueprint = Blueprint('state_blueprint', __name__)

@state_blueprint.route("/ping")
def ping_the_app():
    current_app.logger.info("pinged")
    return jsonify("this app is up."),200

# @state_blueprint.route("/sendotp")
# def send_otp():
#     otp = generate_otp()
#     body = f"""access code: {otp}
#     """
#     title = "verify account"
#     state,message = send_text_email("8ash0hegde@gmail.com", title, body)
#     if state:
#         return jsonify(message),200
#     else:
#         return jsonify(message),400


# @state_blueprint.route("/db")
# # @login_required
# def db_state():
#     try:
#         # init_db()
#
#         # print(get_passwordHash("ashwath"))
#         # if get_passwordHash("ashwath"):
#         #     print("exists")
#         # else:
#         #     print("no")
#
#         # userId = request.cookies.get("userId")
#         # current_app.logger.info(
#         #     f'userId from cookies: {userId}'
#         #     f'userId from login: {current_user.id}'
#         # )
#         # columns = ["emailId"]
#         # filters = {
#         #     "userId": userId,
#         # }
#         # c = select_query_dict(userId=userId,table_name="users",columns=columns,filters=filters)
#         # current_app.logger.info(f'{c}')
#         # return jsonify(c),200
#     except Exception as e:
#         current_app.logger.info(f'{e}')
#     return jsonify("UP"),200





@state_blueprint.route('/')
@state_blueprint.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@state_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == "POST":
        print(request.form)
    if current_user.is_authenticated:
        return redirect(url_for('state_blueprint.index'))
    form = LoginForm()
    if form.validate_on_submit():
        userId = form.username.data
        if not check_user(userId):
            flash('Invalid username or password')
            return redirect(url_for('state_blueprint.login'))
        passwordHash = get_passwordHash(userId)
        if not check_password_hash(passwordHash,form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('state_blueprint.login'))
        user = User(id=userId)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('state_blueprint.index')
        return redirect(next_page or url_for('state_blueprint.index'))
    return render_template('login.html', title='Sign In', form=form)


@state_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('state_blueprint.index'))


@state_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('state_blueprint.index'))
    # current_app.logger.info("registring new person.")
    form = RegistrationForm()
    if form.validate_on_submit():
        user_info = {
            "userId": form.username.data,
            "emailId": form.email.data,
            "passwordHash": generate_password_hash(form.password.data),
        }
        current_app.logger.info("registring new person.")
        current_app.logger.info(f'{user_info}')
        try:
            insert_row(
                userId=form.username.data,
                table_name = "tempUsers",
                columns = user_info,
            )
        except Exception as e:
            current_app.logger.error("unable to insert row.")
            current_app.logger.error(f'{e}')
            flash(
                'Unable to save your your info.'
                ' Please try again or contact the owner.'
            )
            render_template('register.html', title='Register', form=form)
        try:
            send_otp(user_info)
        except Exception as e:
            current_app.logger.error(f'{e}')
        # flash('Congratulations, you are now a registered user!')
        flash('Please validate your email.')
        res = flask.make_response(redirect(url_for('state_blueprint.otp')))
        res.set_cookie('userId', form.username.data)
        return res
    return render_template('register.html', title='Register', form=form)

@state_blueprint.route('/otp', methods=['GET','POST'])
def otp():
    if current_user.is_authenticated:
        return redirect(url_for('state_blueprint.index'))
    # current_app.logger.info("registring new person.")
    form = OtpForm()
    current_app.logger.info(f'current user is {request.cookies.get("userId")}')
    if not request.cookies.get("userId"):
        flash('Please register to verify account.')
        return redirect(url_for('state_blueprint.register'))

    if form.validate_on_submit():
        current_app.logger.info("OTP is validated.")
        # current_app.logger.info(f'{column_names}')
        try:
            # be careful with this ooutput dict
            user_info = select_query_dict(**{
                "columns": ["userId", "emailId", "passwordHash"],
                "filters": {
                    "userId": request.cookies.get("userId"),
                },
                "table_name": "tempUsers",
                "userId": request.cookies.get("userId"),
            })
            insert_row(**{
                "userId": user_info["userId"],
                "columns": user_info,
                "table_name": "users"
            })

        except Exception as e:
            current_app.logger.error("unable to insert row.")
            current_app.logger.error(f'{e}')
            flash(
                'Unable to validate OTP.'
                ' Please try again or contact the owner.'
            )
            return redirect(url_for('state_blueprint.otp'))
        # db.session.add(user)
        # db.session.commit()
        # flash('Congratulations, you are now a registered user!')
        flash('Email has been Successfully validated.')
        return redirect(url_for('state_blueprint.login'))
    return render_template('otp.html', title='Register', form=form)

def send_otp(user_info):
    current_app.logger.info(f'sending OTP to {user_info["emailId"]}')
    otp = generate_otp()
    body = f"""access code: {otp}
    """
    title = "verify account"
    state,message = send_text_email(user_info["emailId"], title, body)
    if state:
        if not update_rows(**{
            "table_name": "tempUsers",
            "userId": user_info["userId"],
            "columns": {
                "otp": otp,
            },
            "filters": {
                "emailId": user_info["emailId"],
            }
        }):
            raise Exception("failed to store OTP")
    else:
        raise Exception("failed to send OTP through email")
