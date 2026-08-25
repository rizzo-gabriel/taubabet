import random
import os
import string
import qrcode

from werkzeug.utils import secure_filename 
from flask import Flask, render_template, request, redirect, url_for, session
from modelos import Usuario, Aposta, ApostaContra, Comentario, Pagamento, Resgate, UsuarioVip
from functools import wraps
from datetime import datetime, date

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.secret_key = 'chavequesejarealmentesecreta'
app.permanent_session_lifetime = 600000000 #1 google

usuarios = []

# decorador para proteger rotas que exigem autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('pagina_login'))
        return f(*args, **kwargs)
    return decorated_function


# ROTAS PARA HTML
@app.route("/")
def pagina_entrada():
    return render_template("entrada.html")

@app.route("/pagina-principal")
@login_required
def home():
    usuario = [usuario for usuario in usuarios if usuario.id == session.get('usuario_id')]
    return render_template("index.html", usuario=usuario[0] if usuario else None, saldo_negativo=saldo_negativo(), saldo=int(float(session['saldo'])))

@app.route("/pagina-cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

@app.route("/pagina-aposta")
@login_required
def pagina_aposta():
    l_a = ler_apostas()
    return render_template("apostas.html", lista_apostas=l_a, nome_usuario=session['nome_usuario'])

@app.route("/pagina-aposta-contra")
@login_required
def pagina_aposta_contra():
    l_a = ler_apostas()
    return render_template("apostas_contra.html", lista_apostas=l_a, nome_usuario=session['nome_usuario'])

@app.route("/pagina-comentario")
@login_required
def pagina_comentario():
    l_c = ler_comentarios()
    return render_template("comentarios.html", lista_comentarios=l_c, nome_usuario=session['nome_usuario'])

@app.route("/pagina-login")
def pagina_login():
    return render_template("login.html")

@app.route("/pagina-configuracoes")
def pagina_configuracoes():

    tema = session.get("tema", "escuro")
    cookies = session.get("cookies", "desativado")

    esse_usuario_e_vip = False

    l_uv = ler_usuariosvip()

    for usuariovip in l_uv:
        if usuariovip.email == session['usuario']:
            esse_usuario_e_vip = True

    return render_template("configuracoes.html", tema=tema, cookies=cookies, esse_usuario_e_vip=esse_usuario_e_vip)

@app.route("/pagina-lista-apostas")
def pagina_lista_apostas():
    l_a = ler_apostas()
    return render_template("div_apostas.html", lista_apostas=l_a)

@app.route("/pagina-lista-comentarios")
def pagina_lista_comentarios():
    l_c = ler_comentarios()
    return render_template("div_comentarios.html", lista_comentarios=l_c)

@app.route("/pagina-visualizar-perfil")
@login_required
def pagina_visualizar_perfil():
    usuario = [usuario for usuario in usuarios if usuario.id == session.get('usuario_id')]
    return render_template("div_usuario.html", usuario=usuario[0] if usuario else None)

@app.route("/pagina-resgate")
@login_required
def pagina_resgate():
    return render_template("resgate.html", nome_usuario=session['nome_usuario'], saldo=session['saldo'])

@app.route("/pagina-adicionar-saldo")
@login_required
def pagina_adicionar_saldo():
    return render_template("adicionar_saldo.html")

@app.route("/pagina-cartao-de-credito")
@login_required
def pagina_cartao_de_credito():
    return render_template("pagar_cartao_de_credito.html")

@app.route("/pagina-cartao-de-debito")
@login_required
def pagina_cartao_de_debito():
    return render_template("pagar_cartao_de_debito.html")

@app.route("/pagina-pix")
@login_required
def pagina_pix():
    return render_template("pagar_pix.html")

@app.route("/pagina-comprovante")
@login_required
def pagina_comprovante():
    return render_template("pagar_comprovante.html")

@app.route("/pagina-confirmar-admin-apostas")
def pagina_confirmar_admin_apostas():
    return render_template("confirmar_admin_apostas.html")

@app.route("/pagina-confirmar-admin-comentarios")
def pagina_confirmar_admin_comentarios():
    return render_template("confirmar_admin_comentarios.html")

@app.route("/pagina-pagar-vip")
@login_required
def pagina_pagar_vip():
    return render_template("pagar_vip.html")

# CADASTRAR
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome_completo = request.form.get("nome")
    cpf = request.form.get("cpf")
    email = request.form.get("email")
    senha = request.form.get("senha")
    telefone = request.form.get("telefone")
    saldo = request.form.get("saldo") 

    if nome_completo and cpf and senha and email and telefone and saldo:
        for usuario in usuarios:
            if usuario.email == email:
                return render_template("cadastro.html", resultado="Email já existe.")
        usuarios.append(Usuario(len(usuarios)+1, nome_completo, cpf, email, senha, telefone, saldo, foto=None))
        salvar_usuarios_json()
    return redirect("/")

# AUTENTICAR
@app.route("/autenticar", methods=["POST"])
def autenticar():
    email = request.form.get("email")
    senha = request.form.get("senha")

    for usuario in usuarios:
        if usuario.email == email and usuario.senha == senha:
            session.permanent = True
            session['usuario'] = usuario.email
            session['nome_usuario'] = usuario.nome_completo
            session['usuario_senha'] = usuario.senha
            session['usuario_id'] = usuario.id
            session['saldo'] = usuario.saldo
            return redirect("/pagina-principal")
    return render_template("login.html")

# APOSTAR
@app.route("/apostar/<nome_usuario>", methods=["POST"])
def apostar(nome_usuario):
    local = request.form.get("local")
    valor = request.form.get("valor")
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao")

    vitoria = random.randint(0, 1000)
    if vitoria%2==0:
        resultado="Derrota"
        valor_final = 0
    else:
        resultado="Vitória"
        acrescimo = random.randint(1,3)
        if acrescimo%2==0:
            valor_final = int(valor) * 1.1
        else:
            valor_final = int(valor) * (random.randint(10, 100))

        valor_final = round(valor_final, 0)

    # valor_formatado
    valor_formatado = f"R$ {valor_final}.00"

    # verificar qual vai ser a cor
    if valor_final>0:
        cor = "background-color: {{ 'rgba(100, 0, 0, 0.5)'}}"
    else:
        cor = "background-color: {{ 'rgba(200, 0, 0, 0.5)'}}"

    # pegar usuario que apostou
    usuario_que_apostou = nome_usuario

    if local and valor and tipo and descricao:
        lista_apostas.append(Aposta(len(lista_apostas)+1, local, valor, tipo, descricao, resultado, valor_final, valor_formatado, cor, usuario_que_apostou))
        salvar_apostas_json()

    saldo = float(session['saldo']) - float(valor) + float(valor_final)
    atualizar_saldo(saldo)
    return redirect(url_for('pagina_aposta'))

@app.route("/apostar-contra/<nome_usuario>", methods=["POST"])
def apostar_contra(nome_usuario):
    contra_aposta = request.form.get("contra_aposta") #pega o id da aposta feita
    valor = request.form.get("valor-contra")
    descricao = request.form.get("descricao-contra")
    usuario_que_apostou = nome_usuario

    if contra_aposta and valor and descricao:
        l_a = ler_apostas()
        for aposta in l_a:
            if aposta.id == contra_aposta:
                if valor>=aposta.valor_final:
                    lista_apostascontras.append(ApostaContra(len(lista_apostascontras)+1, contra_aposta, valor, descricao, usuario_que_apostou))
                    salvar_apostascontras_json()
                else:
                    print("O valor informado é menor que o mínimo")
    return redirect(url_for('pagina_aposta'))

@app.route("/comentar/<nome_usuario>", methods=["POST"])
def comentar(nome_usuario):
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    feedback = request.form.get("feedback")
    denuncia = request.form.get("denuncia")
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}" 
    usuario_que_comentou = nome_usuario

    if titulo and descricao:
        lista_comentarios.append(Comentario(len(lista_comentarios)+1, titulo, descricao, feedback, denuncia, data, usuario_que_comentou))
        salvar_comentarios_json()
    return redirect(url_for('pagina_comentario'))

@app.route("/limpar")
def limpar():
    lista_comentarios.clear()
    salvar_comentarios_json()
    return redirect(url_for('pagina_comentario'))

@app.route("/configurar", methods=["POST"])
def configurar():
    session["cookies"] = request.form.get("cookies")
    session["tema_interface"] = request.form.get("interface_clara")

    if session["cookies"] == "None":
        app.permanent = False
    elif session["cookies"] =="on":
        app.permanent = True

    return redirect(url_for('home'))

@app.route("/atualizar_perfil", methods=["POST"])
def atualizar_perfil():
    nome_completo = request.form.get("nome")
    cpf = request.form.get("cpf")
    email = request.form.get("email")
    senha = request.form.get("senha")
    telefone = request.form.get("telefone")
    saldo = session['saldo']
    foto = upload_imagem()

    if nome_completo and cpf and email and senha and telefone:
        if usuario := [usuario for usuario in usuarios if usuario.id == session.get('usuario_id')]:
            if foto is None:
                foto = usuario[0].foto
            usuario_atualizado = Usuario(usuario[0].id, nome_completo, cpf, email, senha, telefone, saldo, foto)
            usuarios[usuarios.index(usuario[0])] = usuario_atualizado
            session['nome_usuario'] = usuario_atualizado.nome_completo
            salvar_usuarios_json()
            return render_template("index.html", usuario=usuario_atualizado, resultado="atualizado")
    return redirect(url_for("home"))

def upload_imagem():
    arquivo = request.files.get("foto")
    
    if arquivo:
        nome_seguro = secure_filename(arquivo.filename)
        caminho = os.path.join("static/uploads", nome_seguro)
        arquivo.save(caminho)
        return caminho.replace('\\', '/')
    return None

@app.route("/resgatar", methods=['POST'])
def resgatar():
    valor = request.form.get("valor")
    senha = request.form.get("senha")
    usuario = session['nome_usuario']
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}" 

    if valor and senha:
        for u in usuarios:
            if u.nome_completo==usuario and u.senha==senha:
                saldo = float(session['saldo']) - float(valor)
                atualizar_saldo(saldo) 
                valor_para_usuario = 0.7 * float(valor)
                lista_resgates.append(Resgate(len(lista_resgates)+1, valor, valor_para_usuario, usuario, data))
                salvar_resgate_json()
                return redirect(url_for('home'))
            
    return redirect(url_for('pagina_resgate'))

@app.route("/identificar-forma-de-pagamento", methods=['POST'])
def identificar_forma_de_pagamento():
    forma_de_pagamento = request.form.get("forma-de-pagamento")
    if forma_de_pagamento=="pix":
        return redirect(url_for('pagina_pix'))
    elif forma_de_pagamento=="cartao-de-credito":
        return redirect(url_for('pagina_cartao_de_credito'))
    elif forma_de_pagamento=="cartao-de-debito":
        return redirect(url_for('pagina_cartao_de_debito'))
    elif forma_de_pagamento=="enviar-comprovante":
        return redirect(url_for('pagina_comprovante'))
    else:
        return "Opção Inválida"

@app.route("/pagar-com-cartao-credito", methods=['POST'])
def pagar_com_cartao_credito():
    valor = request.form.get("valor")
    numero_do_cartao = request.form.get("numero-do-cartao")
    nome_do_cartao = request.form.get("nome-do-cartao")
    validade = request.form.get("validade")
    cvv = request.form.get("cvv")
    usuario = session['nome_usuario']
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}" 

    if valor and numero_do_cartao and nome_do_cartao and validade and cvv:
        lista_pagamentos.append(Pagamento(len(lista_pagamentos)+1, valor, "Cartão de crédito", usuario, data))
        salvar_pagamento_json()
    else:
        return redirect(url_for('pagina_cartao_de_credito'))
    a = float(session['saldo']) + float(valor)
    atualizar_saldo(a)
    return redirect(url_for('home'))

@app.route("/pagar-com-cartao-debito", methods=['POST'])
def pagar_com_cartao_debito():
    valor = request.form.get("valor")
    numero_do_cartao = request.form.get("numero-do-cartao")
    nome_do_cartao = request.form.get("nome-do-cartao")
    validade = request.form.get("validade")
    cvv = request.form.get("cvv")
    usuario = session['nome_usuario']
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}" 

    if valor and numero_do_cartao and nome_do_cartao and validade and cvv:
        lista_pagamentos.append(Pagamento(len(lista_pagamentos)+1, valor, "Cartão de débito", usuario, data))
        salvar_pagamento_json()
    else:
        return redirect(url_for('pagina_cartao_de_debito'))
    a = float(session['saldo']) + float(valor)
    atualizar_saldo(a)
    return redirect(url_for('home'))

codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=80))

@app.route("/pagar-com-pix", methods=['POST'])
def pagar_com_pix():
    valor = request.form.get("valor")
    usuario = session['nome_usuario']
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}" 

    if valor:
        lista_pagamentos.append(Pagamento(len(lista_pagamentos)+1, valor, "PIX", usuario, data))
        salvar_pagamento_json()
    else:
        return redirect(url_for('pagina_pix'))
    a = float(session['saldo']) + float(valor)
    atualizar_saldo(a)
    return redirect(url_for('home'))

@app.route("/gerar_qr", methods=["POST"])
def gerar_qr():
    valor = request.json.get("valor")

    if not valor:
        return {"erro": "sem valor"}, 400

    codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    url = f"http://127.0.0.1:5000/pix/{codigo}"

    img = qrcode.make(url)
    path = f"static/img/{codigo}.png"
    img.save(path)

    return {"img": path}

@app.route("/pagar-com-comprovante", methods=["POST"])
def pagar_com_comprovante():
    valor = request.form.get("valor")
    usuario = session['nome_usuario']
    data = f"{datetime.now().strftime("[ %H:%M - %d/%m/%Y ]")}"

    if valor:
        lista_pagamentos.append(Pagamento(len(lista_pagamentos)+1, valor, "Comprovante", usuario, data))
        salvar_pagamento_json()
    else:
        return redirect(url_for('pagina_comprovante'))
    a = float(session['saldo']) + float(valor)
    atualizar_saldo(a)
    return redirect(url_for('home'))

@app.route("/atualizar_saldo", methods=["POST"])
def atualizar_saldo(saldo):
    novo_saldo = saldo
    usuario_id = session.get("usuario_id")

    if not novo_saldo or not usuario_id:
        return redirect(url_for("home"))

    try:
        novo_saldo = float(novo_saldo)
    except ValueError:
        return redirect(url_for("home"))

    # encontra usuário
    usuario_encontrado = next(
        (u for u in usuarios if u.id == usuario_id),
        None
    )

    if not usuario_encontrado:
        return redirect(url_for("home"))

    # cria usuário atualizado só mudando saldo
    usuario_atualizado = Usuario(
        usuario_encontrado.id,
        usuario_encontrado.nome_completo,
        usuario_encontrado.cpf,
        usuario_encontrado.email,
        usuario_encontrado.senha,
        usuario_encontrado.telefone,
        str(novo_saldo),   
        usuario_encontrado.foto
    )

    # substitui na lista
    index = usuarios.index(usuario_encontrado)
    usuarios[index] = usuario_atualizado

    # atualiza session também
    session["saldo"] = str(novo_saldo)

    salvar_usuarios_json()

    return redirect(url_for("home"))

@app.route("/entrar-admin/<string:pgn>", methods=['POST'])
def entrar_admin(pgn):
    senha = request.form.get("senha")
    
    l_uv = ler_usuariosvip()
    for usuariovip in l_uv:
        if usuariovip.email == session['usuario']:
            senha_vip = usuariovip.senha_vip

    if pgn=='aposta':
        if senha=="admin" or senha==senha_vip:
            return redirect(url_for('pagina_lista_apostas'))
        else:
            return redirect(url_for('pagina_confirmar_admin_apostas'))
    if pgn=='comentario':
        if senha=="admin" or senha==senha_vip:
            return redirect(url_for('pagina_lista_comentarios'))
        else:
            return redirect(url_for('pagina_confirmar_admin_comentarios'))

@app.route("/pagar-conta-vip", methods=['POST'])
def pagar_conta_vip():
    email = request.form.get("email")
    senha = request.form.get("senha")
    senha_vip = request.form.get("senha_vip")
    confirmar_senha_vip = request.form.get("confirmar_senha_vip")

    if email==session['usuario'] and senha==session['usuario_senha'] and senha_vip==confirmar_senha_vip:
        session['senha_vip'] = senha_vip

        lista_usuariosvip.append(UsuarioVip(len(lista_usuariosvip)+1, email, senha, senha_vip))
        salvar_usuariosvip_json()

        saldo = float(session['saldo']) - 30.0
        atualizar_saldo(saldo)

        return redirect(url_for("pagina_configuracoes"))
    else:
        return redirect(url_for("pagina_pagar_vip"))

@app.route("/saldo-negativo")
def saldo_negativo():
    if float(session['saldo'])<=0:
        return True
    else:
        return False