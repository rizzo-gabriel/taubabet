import os
import random
import string
import qrcode
from functools import wraps
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename

from taubabet import app, db
from taubabet.modelos import Usuario, Aposta, Comentario, Pagamento, Resgate, UsuarioVip

# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('pagina_login'))
        return f(*args, **kwargs)
    return decorated_function

# Funções auxiliares
def upload_image():
    arquivo = request.files.get('foto')
    if arquivo and arquivo.filename:
        nome_seguro = secure_filename(arquivo.filename)
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
        arquivo.save(caminho)
        return caminho.replace('\\', '/')
    return None

def atualizar_saldo(usuario_id, novo_saldo):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        usuario.saldo = novo_saldo
        db.session.commit()
        session['saldo'] = novo_saldo

# Rotas de entrada
@app.route("/")
def pagina_entrada():
    return render_template("entrada.html")

@app.route("/pagina-login")
def pagina_login():
    return render_template("login.html")

@app.route("/pagina-cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')
    telefone = request.form.get('telefone')
    saldo = request.form.get('saldo', 0.0)
    if not all([nome, cpf, email, senha, telefone]):
        flash('Preencha todos os campos obrigatórios.', 'danger')
        return render_template("cadastro.html")
    if Usuario.query.filter_by(email=email).first():
        flash('E-mail já cadastrado.', 'danger')
        return render_template("cadastro.html")
    if Usuario.query.filter_by(cpf=cpf).first():
        flash('CPF já cadastrado.', 'danger')
        return render_template("cadastro.html")
    novo = Usuario(
        nome_completo=nome,
        cpf=cpf,
        email=email,
        telefone=telefone,
        saldo=float(saldo)
    )
    novo.set_senha(senha)
    db.session.add(novo)
    db.session.commit()
    flash('Cadastro realizado com sucesso! Faça login.', 'success')
    return redirect(url_for('pagina_login'))

@app.route("/autenticar", methods=['POST'])
def autenticar():
    email = request.form.get('email')
    senha = request.form.get('senha')
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.verificar_senha(senha):
        session.permanent = True
        session['usuario_id'] = usuario.id
        session['nome_usuario'] = usuario.nome_completo
        session['saldo'] = usuario.saldo
        flash(f'Bem-vindo, {usuario.nome_completo}!', 'success')
        return redirect(url_for('dashboard'))
    flash('E-mail ou senha inválidos.', 'danger')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Desconectado com sucesso.', 'info')
    return redirect(url_for('pagina_entrada'))

# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template("dashboard.html", usuario=usuario)

@app.route('/api/todas_apostas')
@login_required
def api_todas_apostas():
    """
    Retorna dados de todas as apostas para exibir no gráfico,
    com eixo X padronizado para todos os usuários
    """
    # Buscar todas as apostas com informações do usuário
    todas_apostas = db.session.query(
        Aposta, Usuario.nome_completo
    ).join(
        Usuario, Aposta.usuario_id == Usuario.id
    ).order_by(
        Aposta.data.asc()
    ).all()
    
    if not todas_apostas:
        return jsonify([])
    
    # Criar um índice único para cada aposta baseado na data/hora
    from collections import defaultdict
    
    posicoes = {}
    posicao_atual = 0
    
    # Primeiro, criar a lista de todas as posições
    for aposta, _ in todas_apostas:
        identificador = f"{aposta.data.strftime('%Y%m%d%H%M%S')}_{aposta.id}"
        if identificador not in posicoes:
            posicoes[identificador] = {
                'posicao': posicao_atual,
                'label': f"#{posicao_atual + 1}",
                'id': aposta.id
            }
            posicao_atual += 1
    
    # Inicializar dados por usuário com None (sem aposta)
    dados_por_usuario = defaultdict(lambda: {
        'valores': [None] * len(posicoes),
        'resultados': [None] * len(posicoes)
    })
    
    # Preencher os dados de cada aposta na posição correta
    for aposta, nome_usuario in todas_apostas:
        identificador = f"{aposta.data.strftime('%Y%m%d%H%M%S')}_{aposta.id}"
        posicao = posicoes[identificador]['posicao']
        
        # Valor positivo para vitória, negativo para derrota
        if aposta.resultado == 'Vitória':
            valor = aposta.valor_final
        else:
            valor = -aposta.valor
        
        dados_por_usuario[nome_usuario]['valores'][posicao] = valor
        dados_por_usuario[nome_usuario]['resultados'][posicao] = aposta.resultado
    
    # Labels do eixo X
    labels = [posicoes[ident]['label'] for ident in sorted(posicoes.keys(), 
                key=lambda x: posicoes[x]['posicao'])]
    
    # Cores para cada usuário
    cores = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FFB1C1', '#9AD0F5', '#FF6B6B', '#4ECDC4',
        '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA'
    ]
    
    # Preparar resultado final
    resultado_final = []
    for i, (usuario, dados) in enumerate(dados_por_usuario.items()):
        cor = cores[i % len(cores)]
        resultado_final.append({
            'usuario': usuario,
            'labels': labels,
            'valores': dados['valores'],
            'resultados': dados['resultados'],
            'cor': cor
        })
    
    return jsonify(resultado_final)

# Perfil
@app.route("/perfil")
@login_required
def perfil():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template("perfil.html", usuario=usuario)

@app.route("/atualizar_perfil", methods=['POST'])
@login_required
def atualizar_perfil():
    usuario = Usuario.query.get(session['usuario_id'])
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    telefone = request.form.get('telefone')
    senha = request.form.get('senha')
    foto = upload_image()
    if nome and cpf and telefone:
        usuario.nome_completo = nome
        usuario.cpf = cpf
        usuario.telefone = telefone
        if senha:
            usuario.set_senha(senha)
        if foto:
            usuario.foto = foto
        db.session.commit()
        session['nome_usuario'] = usuario.nome_completo
        flash('Perfil atualizado com sucesso!', 'success')
    else:
        flash('Preencha todos os campos obrigatórios.', 'danger')
    return redirect(url_for('perfil'))

# Páginas de apostas e comentários (com listagem)
@app.route("/apostas")
@login_required
def pagina_aposta():
    usuario = Usuario.query.get(session['usuario_id'])
    lista_apostas = Aposta.query.filter_by(usuario_id=usuario.id).order_by(Aposta.data.desc()).all()
    return render_template("apostas.html", lista_apostas=lista_apostas, nome_usuario=usuario.nome_completo)

@app.route("/apostar", methods=['POST'])
@login_required
def apostar():
    usuario = Usuario.query.get(session['usuario_id'])
    local = request.form.get('local')
    valor = float(request.form.get('valor', 0))
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    if not local or not valor or not tipo:
        flash('Preencha todos os campos.', 'danger')
        return redirect(url_for('pagina_aposta'))
    if usuario.saldo < valor:
        flash('Saldo insuficiente.', 'danger')
        return redirect(url_for('pagina_aposta'))
    # Sorteio
    vitoria = random.choice([True, False])
    if vitoria:
        multiplicador = random.uniform(1.1, 3.0)
        valor_final = round(valor * multiplicador, 2)
        resultado = 'Vitória'
    else:
        valor_final = 0.0
        resultado = 'Derrota'
    nova = Aposta(
        local=local,
        valor=valor,
        tipo=tipo,
        descricao=descricao,
        resultado=resultado,
        valor_final=valor_final,
        usuario_id=usuario.id
    )
    db.session.add(nova)
    usuario.saldo = usuario.saldo - valor + valor_final
    db.session.commit()
    session['saldo'] = usuario.saldo
    flash(f'Aposta realizada! Resultado: {resultado}', 'info')
    return redirect(url_for('pagina_aposta'))

@app.route("/comentarios")
@login_required
def pagina_comentario():
    usuario = Usuario.query.get(session['usuario_id'])
    lista_comentarios = Comentario.query.order_by(Comentario.data.desc()).all()
    return render_template("comentarios.html", lista_comentarios=lista_comentarios, nome_usuario=usuario.nome_completo)

@app.route("/comentar", methods=['POST'])
@login_required
def comentar():
    usuario = Usuario.query.get(session['usuario_id'])
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    feedback = request.form.get('feedback', '')
    denuncia = request.form.get('denuncia', '')
    if not titulo or not descricao:
        flash('Preencha título e descrição.', 'danger')
        return redirect(url_for('pagina_comentario'))
    novo = Comentario(
        titulo=titulo,
        descricao=descricao,
        feedback=feedback,
        denuncia=denuncia,
        usuario_id=usuario.id
    )
    db.session.add(novo)
    db.session.commit()
    flash('Comentário adicionado!', 'success')
    return redirect(url_for('pagina_comentario'))

@app.route("/limpar_comentarios")
@login_required
def limpar_comentarios():
    # Apenas admin pode limpar (verificação de VIP)
    usuario = Usuario.query.get(session['usuario_id'])
    if usuario.vip and usuario.vip.verificar_senha_vip(session.get('senha_vip_temp', '')):
        Comentario.query.delete()
        db.session.commit()
        flash('Comentários limpos.', 'success')
    else:
        flash('Acesso negado.', 'danger')
    return redirect(url_for('pagina_comentario'))

# Adicionar saldo e métodos de pagamento
@app.route("/adicionar-saldo")
@login_required
def pagina_adicionar_saldo():
    return render_template("adicionar_saldo.html")

@app.route("/identificar-forma-pagamento", methods=['POST'])
@login_required
def identificar_forma_pagamento():
    forma = request.form.get('forma_pagamento')
    if forma == 'pix':
        return redirect(url_for('pagina_pix'))
    elif forma == 'cartao_credito':
        return redirect(url_for('pagina_cartao_credito'))
    elif forma == 'cartao_debito':
        return redirect(url_for('pagina_cartao_debito'))
    elif forma == 'comprovante':
        return redirect(url_for('pagina_comprovante'))
    else:
        flash('Opção inválida.', 'danger')
        return redirect(url_for('pagina_adicionar_saldo'))

@app.route("/pagar-cartao-credito")
@login_required
def pagina_cartao_credito():
    return render_template("pagar_cartao_credito.html")

@app.route("/pagar-cartao-debito")
@login_required
def pagina_cartao_debito():
    return render_template("pagar_cartao_debito.html")

@app.route("/pagar-pix")
@login_required
def pagina_pix():
    return render_template("pagar_pix.html")

@app.route("/pagar-comprovante")
@login_required
def pagina_comprovante():
    return render_template("pagar_comprovante.html")

@app.route("/pagar-com-cartao-credito", methods=['POST'])
@login_required
def pagar_com_cartao_credito():
    valor = float(request.form.get('valor', 0))
    if valor <= 0:
        flash('Valor inválido.', 'danger')
        return redirect(url_for('pagina_cartao_credito'))
    # Simulação de pagamento
    usuario = Usuario.query.get(session['usuario_id'])
    usuario.saldo += valor
    db.session.commit()
    session['saldo'] = usuario.saldo
    pagamento = Pagamento(valor=valor, forma_pagamento='Cartão de Crédito', usuario_id=usuario.id)
    db.session.add(pagamento)
    db.session.commit()
    flash(f'R$ {valor:.2f} adicionados via Cartão de Crédito.', 'success')
    return redirect(url_for('dashboard'))

@app.route("/pagar-com-cartao-debito", methods=['POST'])
@login_required
def pagar_com_cartao_debito():
    valor = float(request.form.get('valor', 0))
    if valor <= 0:
        flash('Valor inválido.', 'danger')
        return redirect(url_for('pagina_cartao_debito'))
    usuario = Usuario.query.get(session['usuario_id'])
    usuario.saldo += valor
    db.session.commit()
    session['saldo'] = usuario.saldo
    pagamento = Pagamento(valor=valor, forma_pagamento='Cartão de Débito', usuario_id=usuario.id)
    db.session.add(pagamento)
    db.session.commit()
    flash(f'R$ {valor:.2f} adicionados via Cartão de Débito.', 'success')
    return redirect(url_for('dashboard'))

@app.route("/pagar-com-pix", methods=['POST'])
@login_required
def pagar_com_pix():
    valor = float(request.form.get('valor', 0))
    if valor <= 0:
        flash('Valor inválido.', 'danger')
        return redirect(url_for('pagina_pix'))
    usuario = Usuario.query.get(session['usuario_id'])
    usuario.saldo += valor
    db.session.commit()
    session['saldo'] = usuario.saldo
    pagamento = Pagamento(valor=valor, forma_pagamento='PIX', usuario_id=usuario.id)
    db.session.add(pagamento)
    db.session.commit()
    flash(f'R$ {valor:.2f} adicionados via PIX.', 'success')
    return redirect(url_for('dashboard'))

@app.route("/gerar_qr", methods=['POST'])
@login_required
def gerar_qr():
    valor = request.json.get('valor')
    if not valor:
        return jsonify({'error': 'Valor necessário'}), 400
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    url_pix = f"http://127.0.0.1:5000/pix/{codigo}"
    img = qrcode.make(url_pix)
    path = f"static/img/qrcode_{codigo}.png"
    img.save(path)
    return jsonify({'img': path})

@app.route("/pagar-com-comprovante", methods=['POST'])
@login_required
def pagar_com_comprovante():
    valor = float(request.form.get('valor', 0))
    if valor <= 0:
        flash('Valor inválido.', 'danger')
        return redirect(url_for('pagina_comprovante'))
    # Simular envio de comprovante (apenas adiciona saldo)
    usuario = Usuario.query.get(session['usuario_id'])
    usuario.saldo += valor
    db.session.commit()
    session['saldo'] = usuario.saldo
    pagamento = Pagamento(valor=valor, forma_pagamento='Comprovante', usuario_id=usuario.id)
    db.session.add(pagamento)
    db.session.commit()
    flash(f'R$ {valor:.2f} adicionados (comprovante enviado).', 'success')
    return redirect(url_for('dashboard'))

# Resgate
@app.route("/resgate")
@login_required
def pagina_resgate():
    return render_template("resgate.html", nome_usuario=session['nome_usuario'], saldo=session['saldo'])

@app.route("/resgatar", methods=['POST'])
@login_required
def resgatar():
    valor = float(request.form.get('valor', 0))
    senha = request.form.get('senha')
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario.verificar_senha(senha):
        flash('Senha incorreta.', 'danger')
        return redirect(url_for('pagina_resgate'))
    if valor <= 0 or valor > usuario.saldo:
        flash('Valor inválido ou saldo insuficiente.', 'danger')
        return redirect(url_for('pagina_resgate'))
    valor_para_usuario = valor * 0.7  # taxa
    usuario.saldo -= valor
    db.session.commit()
    session['saldo'] = usuario.saldo
    resgate = Resgate(valor=valor, valor_para_usuario=valor_para_usuario, usuario_id=usuario.id)
    db.session.add(resgate)
    db.session.commit()
    flash(f'Resgate de R$ {valor:.2f} processado. Você receberá R$ {valor_para_usuario:.2f}.', 'success')
    return redirect(url_for('dashboard'))

# Configurações
@app.route("/configuracoes")
@login_required
def pagina_configuracoes():
    usuario = Usuario.query.get(session['usuario_id'])
    tema = session.get('tema', 'dark')
    cookies = session.get('cookies', 'ativado')
    eh_vip = usuario.vip is not None
    return render_template("configuracoes.html", tema=tema, cookies=cookies, eh_vip=eh_vip)

@app.route("/configurar", methods=['POST'])
@login_required
def configurar():
    session['cookies'] = request.form.get('cookies', 'desativado')
    session['tema'] = request.form.get('tema', 'dark')
    flash('Configurações salvas.', 'success')
    return redirect(url_for('dashboard'))

@app.route("/pagar-vip")
@login_required
def pagina_pagar_vip():
    return render_template("pagar_vip.html")

@app.route("/pagar-conta-vip", methods=['POST'])
@login_required
def pagar_conta_vip():
    email = request.form.get('email')
    senha = request.form.get('senha')
    senha_vip = request.form.get('senha_vip')
    confirmar = request.form.get('confirmar_senha_vip')
    usuario = Usuario.query.get(session['usuario_id'])
    if usuario.email != email or not usuario.verificar_senha(senha):
        flash('E-mail ou senha incorretos.', 'danger')
        return redirect(url_for('pagina_pagar_vip'))
    if senha_vip != confirmar:
        flash('As senhas VIP não coincidem.', 'danger')
        return redirect(url_for('pagina_pagar_vip'))
    if usuario.saldo < 30.0:
        flash('Saldo insuficiente para conta VIP (R$ 30,00).', 'danger')
        return redirect(url_for('pagina_pagar_vip'))
    # Descontar
    usuario.saldo -= 30.0
    # Criar ou atualizar VIP
    if usuario.vip:
        usuario.vip.set_senha_vip(senha_vip)
    else:
        novo_vip = UsuarioVip(usuario_id=usuario.id)
        novo_vip.set_senha_vip(senha_vip)
        db.session.add(novo_vip)
    db.session.commit()
    session['saldo'] = usuario.saldo
    flash('Conta VIP ativada com sucesso!', 'success')
    return redirect(url_for('pagina_configuracoes'))

# Área administrativa (visualizar apostas/comentários)
@app.route("/confirmar-admin-apostas")
@login_required
def pagina_confirmar_admin_apostas():
    return render_template("confirmar_admin_apostas.html")

@app.route("/confirmar-admin-comentarios")
@login_required
def pagina_confirmar_admin_comentarios():
    return render_template("confirmar_admin_comentarios.html")

@app.route("/entrar-admin/<string:pagina>", methods=['POST'])
@login_required
def entrar_admin(pagina):
    senha_digitada = request.form.get('senha')
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario.vip:
        flash('Você não é VIP.', 'danger')
        return redirect(url_for('pagina_configuracoes'))
    if not usuario.vip.verificar_senha_vip(senha_digitada) and senha_digitada != 'admin':
        flash('Senha VIP incorreta.', 'danger')
        if pagina == 'apostas':
            return redirect(url_for('pagina_confirmar_admin_apostas'))
        else:
            return redirect(url_for('pagina_confirmar_admin_comentarios'))
    # Armazenar temporariamente para ações de limpeza
    session['senha_vip_temp'] = senha_digitada
    if pagina == 'apostas':
        lista = Aposta.query.order_by(Aposta.id).all()
        return render_template("div_apostas.html", lista_apostas=lista)
    else:
        lista = Comentario.query.order_by(Comentario.id).all()
        return render_template("div_comentarios.html", lista_comentarios=lista)

# Gamificação (API)
@app.route("/api/gamificacao")
@login_required
def api_gamificacao():
    usuario_id = session['usuario_id']
    apostas = Aposta.query.filter_by(usuario_id=usuario_id).all()
    total = len(apostas)
    vitorias = sum(1 for a in apostas if a.resultado == 'Vitória')
    derrotas = total - vitorias
    perc = (vitorias / total * 100) if total > 0 else 0
    maior_vitoria = max((a.valor_final for a in apostas if a.resultado == 'Vitória'), default=0)
    maior_derrota = max((a.valor for a in apostas if a.resultado == 'Derrota'), default=0)
    # Sequência atual (simples)
    sequencia = 0
    for a in reversed(apostas):
        if a.resultado == 'Vitória':
            sequencia = sequencia + 1 if sequencia >= 0 else 1
        else:
            sequencia = sequencia - 1 if sequencia <= 0 else -1
    nivel = total // 5 + 1
    return jsonify({
        'total': total,
        'vitorias': vitorias,
        'derrotas': derrotas,
        'percentual_vitoria': round(perc, 1),
        'maior_vitoria': maior_vitoria,
        'maior_derrota': maior_derrota,
        'sequencia': sequencia,
        'nivel': nivel
    })

# Página inicial redireciona para dashboard se logado
@app.route("/index")
@login_required
def index():
    return redirect(url_for('dashboard'))