# models do site de comercialização 

from django.db import models
from stdimage.models import StdImageField
from django.contrib.auth.models import User

class Base(models.Model):
    criados = models.DateField('Criação', auto_now_add=True)
    modificado = models.DateField('Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True
    
class PlanoAssinatura(Base):
    NIVEL_CHOICES = (
        ('nivel1', 'Nível 1 - Básico'),
        ('nivel2', 'Nível 2 - Intermediário'),
        ('nivel3', 'Nível 3 - Avançado'),
    )
    
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', max_length=200)
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=8)
    nivel = models.CharField('Nível', max_length=10, choices=NIVEL_CHOICES)
    recursos = models.TextField('Recursos', max_length=500)

    class Meta:
        verbose_name = 'Plano de Assinatura'
        verbose_name_plural = 'Planos de Assinatura'

    def __str__(self):
        return self.nome

class Tenant(Base):
    STATUS_CHOICES = (
        ('em_dia', 'Em dia'),
        ('atraso', 'Em atraso'),
        ('expirado', 'Expirado'),
    )
    
    nome = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    email = models.EmailField('E-mail')
    empresa = models.CharField('Empresa', max_length=100)
    telefone = models.CharField('Telefone', max_length=20)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20)  # Novo campo
    plano = models.ForeignKey('core.PlanoAssinatura', verbose_name='Plano', on_delete=models.CASCADE)
    status_pagamento = models.CharField('Status de Pagamento', max_length=10, choices=STATUS_CHOICES, default='em_dia')
    data_vencimento = models.DateField('Data de Vencimento', null=True, blank=True)
    usuario = models.OneToOneField(User, verbose_name='Usuário', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def __str__(self):
        return self.nome
    
class EmailConfig(Base):
    email_backend = models.CharField('EMAIL_BACKEND', max_length=255, default='django.core.mail.backends.smtp.EmailBackend')
    email_host = models.CharField('EMAIL_HOST', max_length=255, null=True, blank=True)
    email_port = models.IntegerField('EMAIL_PORT', default=587)
    email_use_tls = models.BooleanField('EMAIL_USE_TLS', default=True)
    email_host_user = models.CharField('EMAIL_HOST_USER', max_length=255, null=True, blank=True)
    email_host_password = models.CharField('EMAIL_HOST_PASSWORD', max_length=255, null=True, blank=True)
    default_from_email = models.EmailField('DEFAULT_FROM_EMAIL', max_length=255, null=True, blank=True)
    ativar_notificacoes = models.BooleanField('Ativar notificações', default=False)
    email_notificacao = models.EmailField('Email para notificações', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Configuração de Email'
        verbose_name_plural = 'Configurações de Email'

    def __str__(self):
        return f"Configuração de Email: {self.email_host}" if self.email_host else "Configuração de Email"
    
class TenantAPIKey(Base):
    """
    Modelo para armazenar metadados sobre as chaves API dos tenants.
    As chaves em si são gerenciadas pelo rest_framework_api_key.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="api_key_meta")
    last_used = models.DateTimeField("Último uso", null=True, blank=True)
    last_ip = models.GenericIPAddressField("Último IP", null=True, blank=True)
    usage_count = models.PositiveIntegerField("Contagem de uso", default=0)
    
    class Meta:
        verbose_name = "Metadados de API Key"
        verbose_name_plural = "Metadados de API Keys"
        
    def __str__(self):
        return f"API Key para {self.tenant.nome}"