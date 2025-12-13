from django.urls import path
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Área logada
    path('dashboard/', views.dashboard, name='dashboard'),
    path('atividades/', views.listar_atividades, name='atividades'),
    path('atividades/<int:atividade_id>/inscrever/', views.inscrever_atividade, name='inscrever_atividade'),
    path('inscricoes/<int:inscricao_id>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),
    
    # Loja e resgates
    path('loja/', views.loja, name='loja'),
    path('produtos/<int:produto_id>/resgatar/', views.resgatar_produto, name='resgatar_produto'),
    path('meus-resgates/', views.meus_resgates, name='meus_resgates'),

    path('criar-atividades/', views.criar_atividades, name='criar_atividades'),

    path('loja/<int:produto_id>/resgatar/', views.resgatar_produto, name='resgatar_produto'),
    path('meus-resgates/', views.meus_resgates, name='meus_resgates'),

]