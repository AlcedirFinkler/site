from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

@receiver(post_migrate)
def update_email_settings(sender, **kwargs):
    """
    Atualiza as configurações de email depois que todas as migrações
    forem executadas, para evitar referências circulares
    """
    # Apenas executa se for a migração da aplicação core
    if sender.name == 'core':
        try:
            from django.conf import settings
            from .models import EmailConfig
            
            email_config = EmailConfig.objects.filter(ativo=True).first()
            
            if email_config:
                settings.EMAIL_BACKEND = email_config.email_backend
                settings.EMAIL_HOST = email_config.email_host
                settings.EMAIL_PORT = email_config.email_port
                settings.EMAIL_USE_TLS = email_config.email_use_tls
                settings.EMAIL_HOST_USER = email_config.email_host_user
                settings.EMAIL_HOST_PASSWORD = email_config.email_host_password
                settings.DEFAULT_FROM_EMAIL = email_config.default_from_email or 'noreply@weconn.com.br'
        except:
            # Se acontecer qualquer erro, continuamos com as configurações padrão
            pass