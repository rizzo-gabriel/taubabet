from taubabet import db, bcrypt
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    telefone = db.Column(db.String(15))
    saldo = db.Column(db.Float, default=0.0)
    foto = db.Column(db.String(200), nullable=True)
    # Relacionamentos
    apostas = db.relationship('Aposta', backref='usuario', lazy=True)
    comentarios = db.relationship('Comentario', backref='usuario', lazy=True)
    pagamentos = db.relationship('Pagamento', backref='usuario', lazy=True)
    resgates = db.relationship('Resgate', backref='usuario', lazy=True)
    vip = db.relationship('UsuarioVip', backref='usuario', uselist=False, lazy=True)

    def set_senha(self, senha_plana):
        self.senha_hash = bcrypt.generate_password_hash(senha_plana).decode('utf-8')

    def verificar_senha(self, senha_plana):
        return bcrypt.check_password_hash(self.senha_hash, senha_plana)

    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone,
            'saldo': self.saldo,
            'foto': self.foto
        }

class Aposta(db.Model):
    __tablename__ = 'apostas'
    id = db.Column(db.Integer, primary_key=True)
    local = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    resultado = db.Column(db.String(20))   # 'Vitória' ou 'Derrota'
    valor_final = db.Column(db.Float, default=0.0)
    data = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text)
    denuncia = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Resgate(db.Model):
    __tablename__ = 'resgates'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    valor_para_usuario = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class UsuarioVip(db.Model):
    __tablename__ = 'usuarios_vip'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    senha_vip_hash = db.Column(db.String(128), nullable=False)

    def set_senha_vip(self, senha_plana):
        self.senha_vip_hash = bcrypt.generate_password_hash(senha_plana).decode('utf-8')

    def verificar_senha_vip(self, senha_plana):
        return bcrypt.check_password_hash(self.senha_vip_hash, senha_plana)