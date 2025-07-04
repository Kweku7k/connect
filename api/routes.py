from flask import Flask, redirect, render_template, request, jsonify, Blueprint, url_for
from auth.services import login_user
from models import *
from api.services import *
from forms import *

api = Blueprint('api', __name__)


@api.route('/api/requestsenderid')
def request_sender_id(sender_id, description, app_id):
    if not (sender_id and description and app_id):
        return {'message': 'All fields are required'}, 400
    
    response, status = create_sender_id(sender_id, description, app_id)
    
    if status == 200:
        return redirect(url_for('connect.senderId', message=response['message']))
    return redirect(url_for('connect.dashboard'))
    
    


@api.route('/api/register', methods=['POST', 'GET'])
def register():

    form = RegisterForm()
    
    if form.validate_on_submit():
        response, status = register_user(form.username.data, form.email.data, form.phone.data, form.password.data, form.appId.data)
    
        if status == 403:
            print('user already exist')
            return redirect(url_for('auth.login'))

        if status == 200:
            login_user(response['user'])
            print('logged user in')
            return redirect(url_for('connect.dashboard', api_token=response['api_token']))
    
    return render_template('onboard.html', form=form)



















































