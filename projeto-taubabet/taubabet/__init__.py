from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
 
app = Flask(__name__)
 
app.config['UPLOAD_FOLDER'] = 'taubabet/static/uploads'
 
app.secret_key = 'chave_secreta'
app.permanent_session_lifetime = 3600  # 1 hora
 
# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taubabet.db'
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)
 
from taubabet import rotas