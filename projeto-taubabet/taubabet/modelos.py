from datetime import datetime

class Usuario: #modelo usuário

    def __init__(self, id, nome_completo, cpf, email, senha, telefone, saldo, foto):
        self.id = id
        self.nome_completo = nome_completo
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.saldo = saldo
        self.foto = foto
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome_completo": self.nome_completo,
            "cpf": self.cpf,
            "email": self.email,
            "senha": self.senha,
            "telefone": self.telefone,
            "foto": self.foto,
            "saldo": self.saldo
        }
    
class UsuarioVip:

    def __init__(self, id, email, senha, senha_vip):
        self.id = id
        self.email = email
        self.senha = senha
        self.senha_vip = senha_vip

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "senha": self.senha,
            "senha_vip": self.senha_vip
        }
    
class Aposta:

    def __init__(self, id, local, valor, tipo, descricao, resultado, valor_final, valor_formatado, cor, usuario_que_apostou):
        self.id = id
        self.local = local
        self.valor = valor
        self.tipo = tipo
        self.descricao = descricao
        self.resultado = resultado
        self.valor_final = valor_final
        self.valor_formatado = valor_formatado
        self.cor = cor
        self.usuario_que_apostou = usuario_que_apostou

    def to_dict(self):
        return {
            "id": self.id,
            "local": self.local,
            "valor": self.valor,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "resultado": self.resultado,
            "valor_final": self.valor_final,
            "valor_formatado": self.valor_formatado,
            "cor": self.cor,
            "usuario_que_apostou": self.usuario_que_apostou
        }
    
class ApostaContra:

    def __init__(self, id, contra_aposta, valor, descricao, usuario_que_apostou):
        self.id = id
        self.contra_aposta = contra_aposta
        self.valor = valor
        self.descricao = descricao
        self.usuario_que_apostou = usuario_que_apostou

    def to_dict(self):
        return {
            "id": self.id,
            "contra_aposta": self.contra_aposta,
            "valor": self.valor,
            "descricao": self.descricao,
            "usuario_que_apostou": self.usuario_que_apostou
        }

class Comentario:

    def __init__(self, id, titulo, descricao, feedback, denuncia, data, usuario_que_comentou):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.feedback = feedback
        self.denuncia = denuncia
        self.data = data
        self.usuario_que_comentou = usuario_que_comentou

    def to_dict(self):
        return {
            "id" : self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "feedback": self.feedback,
            "denuncia": self.denuncia,
            "data": self.data,
            "usuario_que_comentou": self.usuario_que_comentou
        }        
    
class Pagamento:

    def __init__(self, id, valor, forma_de_pagamento, usuario, data):
        self.id = id
        self.valor = valor
        self.forma_de_pagamento = forma_de_pagamento
        self.usuario = usuario
        self.data = data
    
    def to_dict(self):
        return {
            "id": self.id,
            "valor": self.valor,
            "forma_de_pagamento": self.forma_de_pagamento,
            "usuario": self.usuario,
            "data": self.data
        }
    
class Resgate:

    def __init__(self, id, valor, valor_para_usuario, usuario, data):
        self.id = id
        self.valor = valor
        self.valor_para_usuario = valor_para_usuario
        self.usuario = usuario
        self.data = data
    
    def to_dict(self):
        return {
            "id": self.id,
            "valor": self.valor,
            "valor_para_usuario": self.valor_para_usuario,
            "usuario": self.usuario,
            "data": self.data
        }