import pprint
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import requests
import os
from datetime import datetime
import uuid

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsapp_sessions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Session model
class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    def __repr__(self):
        return f'<Session {self.phone_number}: {self.session_id}>'

# WhatsApp API configuration
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_PERMANENT_TOKEN")

# Endpoint configuration for sending message and session
API_ENDPOINT = os.getenv("API_ENDPOINT")

# Initialize database
def init_db():
    """Initialize the database and create sessions table if it doesn't exist"""
    with app.app_context():
        db.create_all()

# Helper function to check if session exists
def check_session_exists(phone_number):
    session = Session.query.filter_by(phone_number=phone_number).first()
    return session.session_id if session else None

# Helper function to create a new session
def create_session(phone_number):
    session_id = str(uuid.uuid4())
    
    try:
        new_session = Session(
            phone_number=phone_number,
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(new_session)
        db.session.commit()
        return session_id
    except IntegrityError:
        # If session already exists, return existing session_id
        db.session.rollback()
        return check_session_exists(phone_number)

# Function to get or create session for a phone number
def get_or_create_session(phone_number):
    session = Session.query.filter_by(phone_number=phone_number).first()
    
    if session:
        return session.session_id
    else:
        return create_session(phone_number)

# Function to update session timestamp
def update_session_timestamp(phone_number):
    session = Session.query.filter_by(phone_number=phone_number).first()
    if session:
        session.updated_at = datetime.now()
        db.session.commit()

# Function to send message and session to endpoint
def send_message_to_endpoint(message, session_id, body):
    try:
        
        payload = {
            "message": message,
            "session_id": session_id,
            "payload":body,
            "channel":"whatsapp"
        }
                
        response = requests.post(API_ENDPOINT, json=payload, timeout=10)
        
        try:
            response_json = response.json()
            response.raise_for_status()
            return response_json
        except ValueError:
            response.raise_for_status()
            return {"response": response.text}
            
    except requests.exceptions.RequestException as e:
        return None

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }   
    
    print(f"[SENDING WHATSAPP MESSAGE] Sending {text} to {to}")

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Verification
@app.route("/wa/callback", methods=["GET", "POST"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    print("VERIFY_TOKEN")
    print(VERIFY_TOKEN)
    
    # Handle GET request for webhook verification
    if request.method == "GET":
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Verification successful", challenge)
            return challenge, 200
        else:
            print("Verification failed", mode, token, VERIFY_TOKEN)
            return "Verification failed", 403
    
    # Handle POST request for incoming messages
    body = request.get_json() or {}
    print("Incoming WhatsApp payload:", body)

    sender_wa_id = None
    message_text = None

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        messages = value.get("messages", [])
        if messages:
            msg = messages[0]
            sender_wa_id = msg.get("from")

            if msg.get("type") == "text":
                message_text = msg["text"]["body"]
                
            if msg.get("type") == "button":
                message_text = msg["button"]["text"]

    except Exception as e:
        print("Error parsing payload:", e)

    # ──────────────────── PROCESS MESSAGE AND SEND REPLY ─────────────────────
    if sender_wa_id and message_text:
        # Get or create session for this phone number
        session_id = get_or_create_session(sender_wa_id)
        update_session_timestamp(sender_wa_id)
        
        # Send message and session to endpoint
        api_response = send_message_to_endpoint(message_text, session_id, body)
        
        # Prepare reply text
        if api_response:
            # Extract response from API (adjust based on your API response structure)
            reply_text = api_response.get("response", api_response.get("message", "I received your message."))
        else:
            reply_text = "Hello"
        
        # Send reply back to user
        send_whatsapp_message(sender_wa_id, reply_text)
        
    return "EVENT_RECEIVED", 200


# Receiving messages
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    print("NEW WHATSAPP UPDATE:")
    pprint.pprint(data)
    
    sender_wa_id = None
    message_text = None

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        messages = value.get("messages", [])
        if messages:
            msg = messages[0]
            sender_wa_id = msg.get("from")

            if msg.get("type") == "text":
                message_text = msg["text"]["body"]

    except Exception as e:
        print("Error parsing payload:", e)

    # ──────────────────── PROCESS MESSAGE AND SEND REPLY ─────────────────────
    if sender_wa_id and message_text:
        # Get or create session for this phone number
        session_id = get_or_create_session(sender_wa_id)
        update_session_timestamp(sender_wa_id)
        
        # Send message and session to endpoint
        api_response = send_message_to_endpoint(message_text, session_id)
        
        # Prepare reply text
        if api_response:
            # Extract response from API (adjust based on your API response structure)
            reply_text = api_response.get("response", api_response.get("message", "Hello"))
        else:
            reply_text = "Hello"
        
        # Send reply back to user
        send_whatsapp_message(sender_wa_id, reply_text)

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    # Initialize database on startup
    init_db()
    app.run(port=5000, debug=True)
