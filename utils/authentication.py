from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from utils.db import check_user, check_email, check_otp
import flask

import random


def generate_otp(n=3):
    return random.randint(10**n, 10**(n+1)-1)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if check_user(username.data):
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if check_email(email.data):
            raise ValidationError('This email is already used.')


class OtpForm(FlaskForm):
    otp = PasswordField('OTP', validators=[DataRequired()])
    submit = SubmitField('Confirm OTP')

    def validate_otp(self, otp):
        otpReceived = otp.data
        if not isinstance(otpReceived, str) or not otpReceived.isnumeric():
            raise ValidationError('Please enter valid OTP.')
        otpReceived = int(otpReceived)

        userId = flask.request.cookies.get("userId")
        if not check_otp({
            "otp": otpReceived,
            "userId": userId,
        }):
            raise ValidationError('Please enter valid OTP.')


class JoinRoomForm(FlaskForm):
    roomId = StringField('Room ID', validators=[DataRequired()])
    roomCode = PasswordField('Room Code', validators=[DataRequired()])

    submit = SubmitField('Enter Room')

    def validate_roomId(self, roomId):
        roomIdReceived = roomId.data
        if (
            not isinstance(roomIdReceived, str) or
            not roomIdReceived.isnumeric()
        ):
            raise ValidationError('Please enter valid roomId.')
        roomId.data = int(roomIdReceived)
        if not roomIdReceived:
            raise ValidationError('Please enter valid OTP.')

    def validate_roomCode(self, roomCode):
        roomCodeReceived = roomCode.data
        if (
            not isinstance(roomCodeReceived, str) or
            not roomCodeReceived.isnumeric()
        ):
            raise ValidationError('Please enter valid roomId.')
        roomCode.data = int(roomCodeReceived)
        if not roomCodeReceived:
            raise ValidationError('Please enter valid OTP.')
