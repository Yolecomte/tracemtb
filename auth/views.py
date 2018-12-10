from flask import Flask, flash, request, render_template, redirect, url_for, Response, Blueprint
from flask import current_app as app
from traceVtt import db
from traceVtt.models import Users
import os

auth = Blueprint('auth',__name__, template_folder='templates', static_folder='static')


@auth.route('/users')
def users():
    users = Users.query.all()
    return render_template('auth/users.html', users=users, home_button=True)

@auth.route('/user/<user_id>')
def user_detail(user_id):
    user = Users.query.get(user_id)
    return render_template('auth/user_detail.html',
                           user=user, 
                           home_button=True)