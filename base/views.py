from flask import flash, request, render_template, redirect, url_for, Response, Blueprint

base = Blueprint('base', __name__, static_folder='static')


@base.route('/')
def home():
    return redirect(url_for('traces.home'))

@base.route('/about')
def about():
    return render_template('base.about.html')
