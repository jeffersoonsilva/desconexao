# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Atividade, Inscricao, Produto, Resgate


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Configuração do admin para Usuários"""
    list_display = ['username', 'email', 'first_name', 'pontos', 'data_cadastro', 'is_active']
    list_filter = ['is_active', 'data_cadastro']
    search_fields = ['username', 'email', 'first_name']
    ordering = ['-data_cadastro']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('pontos', 'data_cadastro')
        }),
    )
    
    readonly_fields = ['data_cadastro']


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    """Configuração do admin para Atividades"""
    list_display = ['titulo', 'tipo', 'data_hora', 'local', 'vagas_disponiveis', 'vagas_totais', 'ativa']
    list_filter = ['tipo', 'ativa', 'data_hora']
    search_fields = ['titulo', 'descricao', 'local']
    ordering = ['-data_hora']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tipo', 'imagem')
        }),
        ('Data e Local', {
            'fields': ('data_hora', 'local')
        }),
        ('Vagas e Pontos', {
            'fields': ('vagas_totais', 'vagas_disponiveis', 'pontos_participacao')
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
    )


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    """Configuração do admin para Inscrições"""
    list_display = ['usuario', 'atividade', 'status', 'data_inscricao', 'pontos_ganhos']
    list_filter = ['status', 'data_inscricao']
    search_fields = ['usuario__username', 'usuario__email', 'atividade__titulo']
    ordering = ['-data_inscricao']
    date_hierarchy = 'data_inscricao'
    
    actions = ['marcar_como_presente', 'marcar_como_ausente']
    
    def marcar_como_presente(self, request, queryset):
        """Ação para marcar inscrições como presente"""
        count = 0
        for inscricao in queryset.filter(status='confirmada'):
            inscricao.marcar_presenca()
            count += 1
        
        self.message_user(request, f'{count} inscrições marcadas como presente.')
    
    marcar_como_presente.short_description = "Marcar como presente (adiciona pontos)"
    
    def marcar_como_ausente(self, request, queryset):
        """Ação para marcar inscrições como ausente"""
        count = queryset.filter(status='confirmada').update(status='ausente')
        self.message_user(request, f'{count} inscrições marcadas como ausente.')
    
    marcar_como_ausente.short_description = "Marcar como ausente"


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Configuração do admin para Produtos"""
    list_display = ['nome', 'pontos_necessarios', 'quantidade_disponivel', 'ativo']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    ordering = ['pontos_necessarios']
    
    fieldsets = (
        ('Informações do Produto', {
            'fields': ('nome', 'descricao', 'imagem')
        }),
        ('Pontos e Estoque', {
            'fields': ('pontos_necessarios', 'quantidade_disponivel')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )


@admin.register(Resgate)
class ResgateAdmin(admin.ModelAdmin):
    """Configuração do admin para Resgates"""
    list_display = ['usuario', 'produto', 'pontos_utilizados', 'data_resgate', 'entregue']
    list_filter = ['entregue', 'data_resgate']
    search_fields = ['usuario__username', 'usuario__email', 'produto__nome']
    ordering = ['-data_resgate']
    date_hierarchy = 'data_resgate'
    
    actions = ['marcar_como_entregue']
    
    def marcar_como_entregue(self, request, queryset):
        """Ação para marcar resgates como entregues"""
        count = queryset.filter(entregue=False).update(entregue=True)
        self.message_user(request, f'{count} resgates marcados como entregues.')
    
    marcar_como_entregue.short_description = "Marcar como entregue"