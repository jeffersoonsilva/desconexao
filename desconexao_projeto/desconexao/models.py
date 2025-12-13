# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class Usuario(AbstractUser):
    """Model customizado para usuários do sistema"""
    pontos = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


class Atividade(models.Model):
    """Model para atividades oferecidas"""
    TIPOS_ATIVIDADE = [
        ('esporte', 'Esporte'),
        ('musica', 'Música'),
        ('Aula de Dança', 'Dança'),
        ('arte', 'Arte'),
        ('alongamento', 'Alongamento'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_ATIVIDADE)
    data_hora = models.DateTimeField()
    local = models.CharField(max_length=300)
    vagas_totais = models.IntegerField(validators=[MinValueValidator(1)])
    vagas_disponiveis = models.IntegerField(validators=[MinValueValidator(0)])
    pontos_participacao = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    imagem = models.ImageField(upload_to='atividades/', null=True, blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
        ordering = ['data_hora']

    def __str__(self):
        return f"{self.titulo} - {self.data_hora.strftime('%d/%m/%Y')}"


class Inscricao(models.Model):
    """Model para inscrições dos usuários nas atividades"""
    STATUS_CHOICES = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='inscricoes')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='inscricoes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmada')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    pontos_ganhos = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together = ['usuario', 'atividade']
        ordering = ['-data_inscricao']

    def __str__(self):
        return f"{self.usuario.username} - {self.atividade.titulo}"

    def marcar_presenca(self):
        """Marca presença e atribui pontos ao usuário"""
        if self.status == 'confirmada':
            self.status = 'presente'
            self.pontos_ganhos = self.atividade.pontos_participacao
            self.usuario.pontos += self.pontos_ganhos
            self.usuario.save()
            self.save()


class Produto(models.Model):
    """Model para produtos disponíveis para troca por pontos"""
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    pontos_necessarios = models.IntegerField(validators=[MinValueValidator(1)])
    quantidade_disponivel = models.IntegerField(validators=[MinValueValidator(0)])
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['pontos_necessarios']

    def __str__(self):
        return f"{self.nome} ({self.pontos_necessarios} pontos)"


class Resgate(models.Model):
    """Model para registrar resgates de produtos"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resgates')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='resgates')
    pontos_utilizados = models.IntegerField()
    data_resgate = models.DateTimeField(auto_now_add=True)
    entregue = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Resgate'
        verbose_name_plural = 'Resgates'
        ordering = ['-data_resgate']

    def __str__(self):
        return f"{self.usuario.username} - {self.produto.nome}"