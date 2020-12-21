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
from utils.cards import Card
from utils.logging import infoLogger

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
    user = current_user
    user.get_roomId()
    infoLogger(user.roomId)
    if user.roomId:
        flash(
            f'Already a room is created. Room ID: {user.roomId}'
        )
        # if not user.roomCode:
        #     user.get_roomCode()
        return redirect(url_for('ui_blueprint.room',roomId=user.roomId))
    else:
        roomCode = random.randint(1000,9999)
        user.set_roomCode(roomCode)
        insert_row(**{
            "userId": user.userId,
            "columns": {
                "roomState": "N",
                "roomCode": roomCode,
                "host": user.userId,
                "starter": user.userId,
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
        room = Room(room_info.get("roomId"))
        room.add_host(current_user.userId)
        room.add_roomToGameStatus()
        flash(
            'created a new room'
            f' code: {roomCode}'
        )
        return redirect(url_for('ui_blueprint.room',roomId=user.roomId))
    #return render_template('createroom.html', roomId=user.roomId, roomCode=user.roomCode)

@ui_blueprint.route('/joinroom', methods=['GET','POST'])
@login_required
def joinroom():
    # current_app.logger.info("registring new person.")
    form = JoinRoomForm()

    if form.validate_on_submit():
        user = current_user
        user.roomId = str(form.roomId.data)
        user.roomCode = form.roomCode.data
        try:
            room = Room(form.roomId.data)
            room.set_roomCode(form.roomCode.data)
            if room.validate_room():
                current_app.logger.info("Adding user to room.")
                if not room.add_user(current_user.userId):
                    flash(f'you are already in the game or not allowed to join.')
                    return redirect(url_for('ui_blueprint.room',roomId=user.roomId))
                current_app.logger.info("user has been added to room.")
                flash(f'Joined room {form.roomId.data}')
                return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
            else:
                flash("Invalid Room ID or Room Code")
        except Exception as e:
            current_app.logger.error(f'failed to add {user.userId} to room.')
            current_app.logger.error(f'{e}')
            flash(
                'Unable to join room.'
            )
            return redirect(url_for('ui_blueprint.joinroom'))
        return redirect(url_for('ui_blueprint.joinroom'))
    user = User(current_user.userId)
    user.get_joinedRoomId()
    if user.roomId:
        flash(
            f'You joined a room already. Room ID: {user.roomId}'
        )
        return redirect(url_for('ui_blueprint.room',roomId=user.roomId))
    return render_template('joinroom.html', form=form)

@ui_blueprint.route('/room/<roomId>', methods=['GET','POST'])
@login_required
def room(roomId):
    room = Room(roomId)
    isHost = room.is_userHost(current_user.userId)
    gameStarted = room.is_gameStarted()
    if request.method == "POST":
        x = dict(request.form)
        if not x or not x.get("playerChosen"):
            flash('chose your team-mate.')
            return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        if not isHost:
            flash('you can\'t choose team-mate')
            return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        if gameStarted:
            flash('this game is already started')
            return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
        if x.get("playerChosen") == room.host:
            flash('you can\'t choose yourself')
            return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        if not len(room.players) == 4:
            flash('No of players is not 4.')
            return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        room.add_playersToGame(x.get("playerChosen"))
        room.set_gameStarted()
        room.distribute_cards()
        return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
    # if not isinstance(roomId,str) or not roomId.isnumeric():
    #     return jsonify("Invalid room"),400
    if not current_user.userId in room.players:
        flash(
            f'You have not joined room: {roomId}'
        )
        return redirect(url_for('ui_blueprint.joinroom'))

    if gameStarted and isHost:
        infoLogger(f'game is already started. redirecting')
        return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
    flash(
        'current room is'
        f': {room.roomId}'
    )
    if isHost:
        flash(
            'current room\'s code is'
            f': {room.get_roomCode()}'
        )

    return render_template(
        'room.html',
        roomId = room.roomId,
        isHost = isHost,
        players = room.players,
        gameStarted = gameStarted,
    )

@ui_blueprint.route('<roomId>/play', methods=['GET','POST'])
@login_required
def play(roomId):
    room = Room(roomId)
    if not room.roomState == "S":
        flash('game has not started yet or it is ended.')
        return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
    if request.method == "POST":
        x = dict(request.form)
        if not x or not x.get("gameType"):
            flash('choose game type.')
            return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
        if x.get("gameType") == "pass":
            if room.gameSelectorAlt:
                # room.pass_gameTypeSelection()
                room.update_gameSelector(room.gameSelectorAlt)
                return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
            else:
                room.drop_game()
                return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        if not room.gameSelector == current_user.userId:
            flash('you can\'t choose team-mate')
            return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
        # if not len(room.players) == 4:
        #     flash('No of players is not 4.')
        #     return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
        room.set_gameType(x.get("gameType"))
        return redirect(url_for('ui_blueprint.play',roomId=room.roomId))

    isCurrentPlayer = False
    gameSelector = False
    if not room.is_gameStarted():
        return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
    if not room.gameType:
        if current_user.userId == room.gameSelector:
            gameSelector = True
    if current_user.userId == room.currentPlayer:
        isCurrentPlayer = True
    cards = room.cards.get(current_user.userId)
    card = Card(cards)
    currentBufferCards = {}
    for player,acard in room.get_currentBufferCards().items():
        currentBufferCards[room.playersMapping[player]] = card.convert_aCardToVisual(acard)
    # pointsTable = room.get_pointsTable()
    cards = card.map_intToCard()
    if currentBufferCards:
        currentSuit = list(currentBufferCards.values())[0][0]
    isCurrentSuitAvailable = False
    for acard in cards.values():
        if currentSuit in acard:
            isCurrentSuitAvailable = True
            break
    return render_template(
        'play.html',roomId=roomId,
        cards=cards,
        gameSelector = gameSelector,
        currentPlayer=room.currentPlayer,
        isCurrentPlayer=isCurrentPlayer,
        gameType=card.suitMapper.get(room.gameType),
        gameTypes = card.suitMapper,
        currentBufferCards=currentBufferCards,
        pointsTable = room.get_pointsTable(),
        currentSuit=currentSuit,
        isCurrentSuitAvailable=isCurrentSuitAvailable,
    )

@ui_blueprint.route('<roomId>/play/<cardId>', methods=['GET','POST'])
@login_required
def played_card(roomId,cardId):
    cardId = int(cardId)
    room = Room(roomId)
    if not room.gameType:
        return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
    if not room.is_player_valid(current_user.userId):
        flash('you are not member of room.')
        redirect(url_for('ui_blueprint.index'))
    if not room.is_gameStarted():
        return redirect(url_for('ui_blueprint.room',roomId=room.roomId))
    # update gameStatus with this. (value and starter)
    # remove the card from roomStatus

    #check if user actually has the card.
    if not cardId in room.cards.get(current_user.userId):
        flash('you dont have this card.')
        return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
    room.play_aCard(current_user.userId,cardId)
    return redirect(url_for('ui_blueprint.play',roomId=room.roomId))
