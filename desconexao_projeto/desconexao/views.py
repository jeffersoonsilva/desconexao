# views.py - VERSÃO SIMPLIFICADA SEM FORMS
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import Usuario, Atividade, Inscricao, Produto, Resgate
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta


def index(request):
    """View da página inicial"""
    atividades = Atividade.objects.filter(ativa=True)[:5]
    context = {
        'atividades': atividades
    }
    return render(request, 'index.html', context)


@require_http_methods(["GET", "POST"])
def cadastro_view(request):
    """View para cadastro de usuários"""
    if request.method == 'POST':
        # Pegar dados do formulário
        nome = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        # Validações
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'cadastro.html')
        
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'cadastro.html')
        
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return render(request, 'cadastro.html')
        
        # Criar usuário
        try:
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=nome
            )
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
            return render(request, 'cadastro.html')
    
    return render(request, 'cadastro.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """View para login de usuários"""
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        try:
            # Buscar usuário pelo email
            usuario = Usuario.objects.get(email=email)
            # Autenticar usando username
            user = authenticate(request, username=usuario.username, password=senha)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Senha incorreta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Email não encontrado.')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """View para logout"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('index')


@login_required
def dashboard(request):
    """Dashboard do usuário logado"""
    usuario = request.user
    inscricoes = Inscricao.objects.filter(usuario=usuario).order_by('-data_inscricao')
    atividades_disponiveis = Atividade.objects.filter(
        ativa=True,
        vagas_disponiveis__gt=0
    ).exclude(
        inscricoes__usuario=usuario,
        inscricoes__status='confirmada'
    )
    
    context = {
        'usuario': usuario,
        'inscricoes': inscricoes,
        'atividades': atividades_disponiveis,
        'pontos': usuario.pontos
    }
    return render(request, 'dashboard.html', context)


@login_required
def listar_atividades(request):
    """Lista todas as atividades disponíveis"""
    tipo = request.GET.get('tipo')
    atividades = Atividade.objects.filter(ativa=True, vagas_disponiveis__gt=0)
    
    if tipo:
        atividades = atividades.filter(tipo=tipo)
    
    context = {
        'atividades': atividades,
        'tipos': Atividade.TIPOS_ATIVIDADE
    }
    return render(request, 'atividades.html', context)


@login_required
@require_http_methods(["POST"])
def inscrever_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    usuario = request.user

    # Verifica se já está inscrito
    inscricao_existente = Inscricao.objects.filter(
        usuario=usuario,
        atividade=atividade,
        status='confirmada'
    ).exists()

    if inscricao_existente:
        messages.warning(request, 'Você já está inscrito nesta atividade.')
        return redirect('atividades')

    # Checa vagas
    if atividade.vagas_disponiveis <= 0:
        messages.error(request, 'Não há vagas disponíveis.')
        return redirect('atividades')

    try:
        with transaction.atomic():
            
            # Cria inscrição salvando os pontos ganhos
            inscricao = Inscricao.objects.create(
                usuario=usuario,
                atividade=atividade,
                pontos_ganhos=10  # <- IMPORTANTE
            )

            # Atualiza vagas
            atividade.vagas_disponiveis -= 1
            atividade.save()

            # Soma pontos ao usuário
            usuario.pontos += 10
            usuario.save()

        messages.success(request, f'Inscrição realizada em {atividade.titulo}! +10 pontos!')
    
    except Exception as e:
        messages.error(request, f'Erro ao inscrever: {e}')

    return redirect('dashboard')




@login_required
@require_http_methods(["POST"])
def cancelar_inscricao(request, inscricao_id):
    """Cancela uma inscrição do usuário e remove os pontos ganhos"""
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, usuario=request.user)
    
    if inscricao.status != 'confirmada':
        messages.warning(request, 'Esta inscrição não pode ser cancelada.')
        return redirect('dashboard')
    
    try:
        with transaction.atomic():

            # Pegar pontos que ele ganhou ao inscrever
            pontos_ganhos = inscricao.pontos_ganhos or 0

            # Remover os pontos do usuário
            if pontos_ganhos > 0:
                usuario = request.user
                usuario.pontos -= pontos_ganhos
                usuario.save()

            # Cancelar a inscrição
            inscricao.status = 'cancelada'
            inscricao.pontos_ganhos = 0
            inscricao.save()

            # Devolver a vaga
            atividade = inscricao.atividade
            atividade.vagas_disponiveis += 1
            atividade.save()

        messages.success(request, f'Inscrição cancelada e {pontos_ganhos} pontos removidos.')
    except Exception as e:
        messages.error(request, f'Erro ao cancelar inscrição: {str(e)}')
    
    return redirect('dashboard')



@login_required
def loja(request):
    """Lista produtos disponíveis para resgate"""
    produtos = Produto.objects.filter(ativo=True, quantidade_disponivel__gt=0)
    usuario = request.user
    
    context = {
        'produtos': produtos,
        'pontos_usuario': usuario.pontos
    }
    return render(request, 'loja.html', context)


@login_required
@require_http_methods(["POST"])
def resgatar_produto(request, produto_id):
    """Resgata um produto usando pontos"""
    produto = get_object_or_404(Produto, id=produto_id)
    usuario = request.user
    
    # Verifica se tem pontos suficientes
    if usuario.pontos < produto.pontos_necessarios:
        messages.error(request, 'Pontos insuficientes.')
        return redirect('loja')
    
    # Verifica disponibilidade
    if produto.quantidade_disponivel <= 0:
        messages.error(request, 'Produto indisponível.')
        return redirect('loja')
    
    # Realiza o resgate
    try:
        with transaction.atomic():
            usuario.pontos -= produto.pontos_necessarios
            usuario.save()
            
            produto.quantidade_disponivel -= 1
            produto.save()
            
            Resgate.objects.create(
                usuario=usuario,
                produto=produto,
                pontos_utilizados=produto.pontos_necessarios
            )
        
        messages.success(request, f'Produto {produto.nome} resgatado com sucesso! Pontos restantes: {usuario.pontos}')
    except Exception as e:
        messages.error(request, f'Erro ao resgatar produto: {str(e)}')
    
    return redirect('loja')


@login_required
def meus_resgates(request):
    """Lista resgates do usuário"""
    resgates = Resgate.objects.filter(usuario=request.user).order_by('-data_resgate')
    
    context = {
        'resgates': resgates
    }
    return render(request, 'resgates.html', context)

@login_required
def criar_atividades(request):
    """Cria automaticamente atividades padrão se ainda não existirem"""
    atividades_lista = [
        ("Aula de Violão", "musica"),
        ("Aula de Bateria", "musica"),
        ("Aula de Piano", "musica"),
        ("Aula de Dança", "dança"),
        ("Artes", "arte"),
        ("Futebol", "esporte"),
        ("Basquete", "esporte"),
        ("Handebol", "esporte"),
    ]

    criadas = 0

    for titulo, tipo in atividades_lista:
        if not Atividade.objects.filter(titulo=titulo).exists():
            Atividade.objects.create(
                titulo=titulo,
                descricao=f"{titulo} para iniciantes.",
                tipo=tipo,
                data_hora=timezone.now() + timedelta(days=3),
                local="Sala Principal",
                vagas_totais=20,
                vagas_disponiveis=20,
                pontos_participacao=10,
                ativa=True
            )
            criadas += 1

    return HttpResponse(f"{criadas} atividades criadas com sucesso!")


