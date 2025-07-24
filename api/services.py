from functools import wraps
import uuid
from models import *
from flask import redirect, request, jsonify, session, url_for
import datetime
from sqlalchemy.exc import SQLAlchemyError

def create_sender_id(senderId, description, appId):
    
    new_sender_id = SenderId(
        senderId=senderId,
        description=description,
        appId=appId
    )
    db.session.add(new_sender_id)
    db.session.commit()
    
    return {'message': 'verification of Sender Id is pending'}, 200 

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Starting API key authentication process...")
        print("Checking API key authentication")
        api_key = request.headers.get('x-api-key')
        print(f"Received API key from headers: {api_key}")

        if not api_key:
            print("API key missing in request headers")
            print("Authentication failed - returning 401")
            return jsonify({'message': 'API key is missing'}), 401

        try:
            print(f"Validating API key: {api_key}")
            print("Querying database for API key...")
            key = ApiKey.query.filter_by(api_key=api_key).first()
            if not key:
                print("Invalid API key provided")
                print("Authentication failed - returning 401") 
                return jsonify({'message': 'Invalid API key'}), 401
            print(f"API key found with ID: {key.id}")
            print(f"Looking up associated user with ID: {key.user_id}")
            user = User.query.filter_by(id=key.user_id).first()
            print(f"User authenticated successfully: {user.id}")
            print(f"User details - Username: {user.username}, Email: {user.email}")
            
            return f(user)

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")
            print("Rolling back database session")
            print("Returning 500 error response")
            return jsonify({'message': 'Database error occurred. Please try again later.'}), 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Returning 500 error response")
            return jsonify({'message': 'An unexpected error occurred.'}), 500

    return decorated_function

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



