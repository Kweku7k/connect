from app import create_app, db
from flask_migrate import Migrate

app = create_app()

if __name__ == '__main__':
    app.run(port=5000,host='0.0.0.0',debug=True)