from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_muito_segura_para_taubabet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taubabet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# Garante que a pasta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Importar as rotas depois de definir app, db e bcrypt
from . import rotas

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)