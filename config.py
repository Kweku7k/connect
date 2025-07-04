

import os


class Config:
    algorithms = ["HS256"]
    algorithm = "HS256"
    SECRET_KEY = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
    JWT_SECRET_KEY = 'c288b2157916b13s523242q3wede00ba242sdqwc676dfde'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECT_DB_URL', 'postgresql://postgres:adumatta@localhost:5432/connect' )
    
    
    baseUrl = os.environ.get('CONNECT_BASE_URL', 'https://connect.prestoghana.com')
    prestoUrl = os.environ.get('PRESTO_PROD_URL', 'https://prestoghana.com')
    server = os.environ.get('SERVER', None)
    environment = os.environ.get('ENVIRONEMT', 'DEV')

    chat_id = os.environ.get('CONNECT_TELGRAM')
    telegramToken = os.environ['PRESTO_TELEGRAM_BOT_TOKEN']
    
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)