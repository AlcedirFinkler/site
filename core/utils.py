# Crie um arquivo utils.py na pasta core

from django.core.mail import send_mail
from django.conf import settings
from .models import EmailConfig

def send_tenant_notification(tenant):
    """
    Envia uma notificação por email quando um novo tenant é criado
    """
    try:
        # Verifica se existe configuração de email e se as notificações estão ativas
        email_config = EmailConfig.objects.filter(ativo=True, ativar_notificacoes=True).first()
        
        if not email_config or not email_config.email_notificacao:
            return False
            
        # Prepara o conteúdo do email
        subject = f'Nova solicitação de tenant: {tenant.nome}'
        message = f"""
Nova solicitação de tenant recebida:

Nome da instância: {tenant.nome}
Subdomínio: {tenant.slug}.weconn.com.br
Empresa: {tenant.empresa}
Email: {tenant.email}
Telefone: {tenant.telefone}
CPF/CNPJ: {tenant.cpf_cnpj}
Plano escolhido: {tenant.plano.nome}

Esta solicitação está pendente de análise e provisionamento.
        """
        
        # Envia o email
        send_mail(
            subject=subject,
            message=message,
            from_email=email_config.default_from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_config.email_notificacao],
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")
        return False