from flask import Flask, redirect, render_template, request, jsonify, Blueprint, url_for
from auth.services import login_user
from mnotifyservices import sendMnotifyApiSms
from models import *
from api.services import *
from forms import *

api = Blueprint('api', __name__)

@api.route('/api/requestsenderid', methods=['POST'])
@api_key_required
def requestSenderId(user):
    print(user)
    data = request.get_json()
    senderId = data.get('senderId')
    description = data.get('description') 
    appId = data.get('appId')
    
    print(f"Received request with senderId: {senderId}, description: {description}, appId: {appId}")

    if not senderId:
        print("Missing senderId")
        return {'message': 'Sender Id required'}, 400
    elif not description:
        print("Missing description") 
        return {'message': 'Description is required'}, 400
    elif not appId:
        print("Missing appId")
        return {'message': 'App Id is required'}, 400
    
    print("Creating sender ID...")
    response, status = create_sender_id(senderId, description, appId)
    
    if status == 200:
        print(f"Successfully created sender ID. Response: {response}")
        return jsonify({'message': response['message']}), status
    print(f"Request completed with status: {status}")
    return jsonify({'message': 'Success'}), status

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

@api.route('/api/sendMessage', methods=['POST'])
@api_key_required
def sendApiMessage(user):
    data = request.get_json()
    senderId = data.get('senderId')
    recipients = data.get('recipients') 
    message = data.get('message')
    
    if senderId is None:
        return jsonify({'message': 'senderId is required'}), 400
    elif recipients is None:
        return jsonify({'message': 'recipients are required'}), 400
    elif message is None:
        return jsonify({'message': 'message is required'}), 400
    
    response = sendMnotifyApiSms(senderId, recipients, message)
    
    return response
    

















































