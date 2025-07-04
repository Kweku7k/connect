import uuid
from models import *
from flask import redirect, request, jsonify, session, url_for
import datetime
from sqlalchemy.exc import SQLAlchemyError

def create_sender_id(sender_id, description, app_id):
    
    new_sender_id = SenderId(
        sender_id=sender_id,
        description=description,
        app_id=app_id
    )
    db.session.add(new_sender_id)
    db.session.commit()
    
    return {'message': 'Sender ID created successfully'}, 200 



def register_user(username, email, phone, password, appId):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {'message': 'Email already registered'}, 403

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    raw_token = str(uuid.uuid4())
    hashed_token = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(
        username=username, 
        email=email, 
        phone=phone, 
        password=password_hash, 
        appId=appId, 
        total=100, 
        balance=100, 
        credits=100,
        added=datetime.datetime.now(),
        api_token = hashed_token
    )
    db.session.add(new_user)
    db.session.commit()

    return {
        'message': 'User registered successfully.',
        'user': new_user,
        'api_token': raw_token
    }, 200




def register_user(username, email, phone, password, appId):
    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'Email already registered'}, 403

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        raw_token = str(uuid.uuid4())
        
        hashed_token = bcrypt.generate_password_hash(raw_token).decode('utf-8') 
        
        new_user = User(
            username=username, 
            email=email, 
            phone=phone, 
            password=password_hash, 
            appId=appId, 
            total=100, 
            balance=100, 
            credits=100,
            added=datetime.datetime.now(),
            api_token = hashed_token
        )
        db.session.add(new_user)
        db.session.commit()

        return {
            'message': 'User registered successfully.',
            'user': new_user,
            'api_token': raw_token
        }, 200

    except SQLAlchemyError as e:
        db.session.rollback()  
        print(f"Database error during user registration: {e}") 
        return {'message': 'Database error during registration. Please try again later.'}, 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'message': 'An unexpected error occurred during registration.'}, 500




