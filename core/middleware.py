# Crie um arquivo middleware.py na pasta core

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import EmailConfig
from django.utils import timezone
from rest_framework_api_key.models import APIKey
from .models import TenantAPIKey, Tenant

class DynamicEmailConfigMiddleware(MiddlewareMixin):
    """
    Middleware para atualizar as configurações de email dinamicamente.
    """
    
    def process_request(self, request):
        # Só atualiza as configurações se estiver no admin
        if request.path.startswith('/admin/'):
            try:
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
                # Caso ocorra algum erro, não faz nada
                pass

class APIKeyUsageMiddleware(MiddlewareMixin):
    """
    Middleware para rastrear o uso de API Keys
    """
    
    def process_response(self, request, response):
        # Verifica se a requisição usou uma API Key
        api_key_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if api_key_header.startswith('Api-Key '):
            key = api_key_header.replace('Api-Key ', '')
            
            try:
                # Tenta encontrar a chave na base
                api_key = APIKey.objects.get_from_key(key)
                
                # Se a chave está ligada a um tenant
                if api_key.name.startswith('tenant.'):
                    tenant_slug = api_key.name.split('tenant.')[1]
                    
                    try:
                        tenant = Tenant.objects.get(slug=tenant_slug)
                        
                        # Obtém ou cria o registro de metadados
                        meta, created = TenantAPIKey.objects.get_or_create(
                            tenant=tenant, 
                            defaults={
                                'last_used': timezone.now(),
                                'last_ip': self.get_client_ip(request),
                                'usage_count': 1
                            }
                        )
                        
                        # Se não foi criado agora, atualiza os campos
                        if not created:
                            meta.last_used = timezone.now()
                            meta.last_ip = self.get_client_ip(request)
                            meta.usage_count += 1
                            meta.save()
                    
                    except Tenant.DoesNotExist:
                        pass
            
            except:
                # Se a chave não for válida, apenas ignora
                pass
                
        return response
        
    def get_client_ip(self, request):
        """
        Obtém o IP do cliente, considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip