import requests
from connect.services import sendTelegram
from models import *
from forms import *
from flask import render_template, url_for, flash, redirect, request, Blueprint
from auth.services import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()   

    if request.method == 'POST':
        print(form.data)

        user = User.query.filter_by(email = form.email.data).first()
        print("user found :")
        print(user)

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print(user)
            
            jwt_token = login_user(user)
            print(jwt_token)

            sendTelegram(f"{user.username} has logged in to the dashboard.")
            return redirect(url_for('connect.dashboard'))
        
        else:
            flash(f'These credentials are not valid')

    return render_template('login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash(f'Successfully logged you out.')
    return redirect(url_for('connect.home'))

