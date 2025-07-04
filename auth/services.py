from functools import wraps
from flask import flash, redirect, session, url_for
import jwt
from models import *
from config import Config


def get_current_user():
    # TODO: Convert class into dictionary
    user_found = session.get('current_user', None)
    if user_found is not None:
        user = User.query.get_or_404(user_found)
        if user is not None:
            return user
    return None
     

def reportTelegram():
    pass

def login_user(user):
    print("Logging in :")
    print(user)
    token = jwt.encode({'user':user.id, 'exp':datetime.datetime.now()+datetime.timedelta(minutes=30)}, Config.SECRET_KEY)
    session['jwt']=token
    session['current_user'] = user.id
    return token

def user_loader(user_id):
    return User.query.get_or_404(user_id)

def logout_user():
    print('Logging out user!')
    session.pop('jwt')
    session.pop('current_user')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = session.get('token') #https://
        token = session.get('jwt') #https://
        print(token)

        if not token:
            return redirect(url_for('auth.login'))

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=Config.algorithms)
            print("-----jwt-----")
            print(data)
            session['current_user'] = data['user']

        except:
            print(f'Token is invalid')
            flash(f'Token is invalid')
            return redirect(url_for('auth.login'))

        
        return f(*args, **kwargs)

    return decorated

