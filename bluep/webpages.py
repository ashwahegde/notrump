import requests
import json
from flask import Blueprint, jsonify, current_app, request, render_template, session
from flask_login import login_user, logout_user, current_user, login_required
import random
from utils.db import init_db

from utils.db import (insert_row, select_query, update_rows, complex_query,
    check_user, get_passwordHash, init_db, select_query_dict
)
from utils.user import User
from utils.room import Room

ui_blueprint = Blueprint('ui_blueprint', __name__)

@ui_blueprint.route("/ping")
def ping_the_app():
    current_app.logger.info("pinged")
    return jsonify("this app is up."),200

@ui_blueprint.route('/')
@ui_blueprint.route('/index')
def index():
    return render_template('index.html', title='Home')

from utils.authentication import JoinRoomForm
from flask import render_template, flash, redirect, url_for, request

@ui_blueprint.route('/createroom', methods=['GET','POST'])
@login_required
def createroom():
    if session.get("userObject"):
        user = User(current_user.userId)
        user.from_json(session.get("userObject"))
    else:
        user = current_user
        current_app.logger.info("creating new room.")
    if not user.roomId:
        user.get_roomId()
    if user.roomId:
        flash(
            f'Already a room is created. Room ID: {user.roomId}'
        )
        if not user.roomCode:
            user.get_roomCode()
    else:
        roomCode = random.randint(1000,9999)
        user.set_roomCode(roomCode)
        insert_row(**{
            "userId": user.userId,
            "columns": {
                "roomState": "0",
                "roomCode": roomCode,
                "host": user.userId,
            },
            "table_name": "roomInfo"
        })
        room_info = select_query_dict(**{
            "columns": ["roomId"],
            "filters": {
                "host": user.userId,
                "roomCode": roomCode,
            },
            "table_name": "roomInfo",
            "userId": user.userId,
        })
        user.set_roomId(room_info.get("roomId"))
        room = Room(roomId=room_info.get("roomId"))
        room.add_host(current_user.userId)
        session["userObject"] = user.__dict__
        flash(
            'created a new room'
            f' code: {roomCode}'
        )
        return redirect(url_for('ui_blueprint.createroom'))
    return render_template('createroom.html', roomId=user.roomId, roomCode=user.roomCode)

@ui_blueprint.route('/joinroom', methods=['GET','POST'])
@login_required
def joinroom():
    # current_app.logger.info("registring new person.")
    form = JoinRoomForm()

    if form.validate_on_submit():
        current_app.logger.info("Room is validated.")
        room = Room(roomId=form.roomId.data)
        print("here")
        room.add_user(current_user.userId)
        # current_app.logger.info(f'{column_names}')
        try:
            # be careful with this ooutput dict
            pass

        except Exception as e:
            current_app.logger.error("unable to insert row.")
            current_app.logger.error(f'{e}')
            flash(
                'Unable to validate OTP.'
                ' Please try again or contact the owner.'
            )
            return redirect(url_for('state_blueprint.joinroom'))
        # db.session.add(user)
        # db.session.commit()
        # flash('Congratulations, you are now a registered user!')
        flash(f'Joined room {form.roomId.data}')
        return redirect(url_for('state_blueprint.index'))
    return render_template('joinroom.html', title='Register', form=form)
