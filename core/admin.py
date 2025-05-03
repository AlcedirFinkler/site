from django.contrib import admin
from django.utils.timezone import now
from datetime import timedelta
from .models import PlanoAssinatura, Tenant, EmailConfig, TenantAPIKey 
from django.urls import path
from django.contrib.admin import AdminSite
from django.urls import path, include
from .views import display_api_key

@admin.register(PlanoAssinatura)
class PlanoAssinaturaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'preco', 'ativo', 'modificado')
    list_filter = ('nivel', 'ativo')
    search_fields = ('nome', 'descricao')

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'email', 'empresa', 'cpf_cnpj', 'plano', 'status_pagamento', 'data_vencimento', 'ativo', 'has_api_key')
    list_filter = ('plano', 'status_pagamento', 'ativo')
    search_fields = ('nome', 'slug', 'email', 'empresa', 'cpf_cnpj')
    readonly_fields = ('nome', 'api_key_info')  # Nome será igual ao slug, então é somente leitura
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'email', 'empresa', 'telefone', 'cpf_cnpj', 'plano')
        }),
        ('Status', {
            'fields': ('status_pagamento', 'data_vencimento', 'ativo')
        }),
        ('API', {
            'fields': ('api_key_info',),
            'description': 'Informações sobre a chave API para integração com o SaaS.'
        }),
        ('Usuário', {
            'fields': ('usuario',)
        }),
    )
    actions = ['marcar_pagamento_realizado', 'marcar_pagamento_pendente', 'marcar_pagamento_expirado', 'generate_api_key']
    
    def api_key_info(self, obj):
        """
        Exibe informações sobre a chave API do tenant
        """
        from rest_framework_api_key.models import APIKey
        
        keys = APIKey.objects.filter(name__startswith=f"tenant.{obj.slug}")
        if keys.exists():
            return f"Chave API ativa: Sim (criada em {keys.first().created.strftime('%d/%m/%Y %H:%M')})"
        return "Chave API ativa: Não (use a ação 'Gerar Chave API' para criar uma)"
    api_key_info.short_description = "Informações da Chave API"
    
    def has_api_key(self, obj):
        """
        Exibe no list_display se o tenant possui uma chave API
        """
        from rest_framework_api_key.models import APIKey
        
        return APIKey.objects.filter(name__startswith=f"tenant.{obj.slug}").exists()
    has_api_key.short_description = "API Key"
    has_api_key.boolean = True
    
    def marcar_pagamento_realizado(self, request, queryset):
        # Define o vencimento para 30 dias a partir de hoje
        data_vencimento = now() + timedelta(days=30)
        
        # Atualiza todos os registros selecionados
        queryset.update(
            status_pagamento='em_dia',
            data_vencimento=data_vencimento,
            ativo=True
        )
        
        self.message_user(request, f'{queryset.count()} tenants foram marcados como pagos, com vencimento em {data_vencimento.strftime("%d/%m/%Y")}.')
    marcar_pagamento_realizado.short_description = "Marcar como pago (próximo vencimento em 30 dias)"
    
    def marcar_pagamento_pendente(self, request, queryset):
        # Atualiza todos os registros selecionados
        queryset.update(
            status_pagamento='atraso',
            ativo=True  # Mantém ativo durante o período de carência
        )
        
        self.message_user(request, f'{queryset.count()} tenants foram marcados como pendentes de pagamento.')
    marcar_pagamento_pendente.short_description = "Marcar como pendente de pagamento"
    
    def marcar_pagamento_expirado(self, request, queryset):
        # Atualiza todos os registros selecionados
        queryset.update(
            status_pagamento='expirado',
            ativo=False  # Desativa o tenant
        )
        
        self.message_user(request, f'{queryset.count()} tenants foram marcados como expirados e desativados.')
    marcar_pagamento_expirado.short_description = "Marcar como expirado e desativar"
    
    def generate_api_key(self, request, queryset):
        """
        Gera uma chave API para cada tenant selecionado
        """
        from rest_framework_api_key.models import APIKey
        from django.utils.html import format_html
        from django.shortcuts import redirect
        
        if not queryset:
            self.message_user(request, "Nenhum tenant selecionado.", level="ERROR")
            return
            
        # Se mais de um tenant foi selecionado
        if queryset.count() > 1:
            results = []
            
            for tenant in queryset:
                # Prefixo para a chave
                key_name = f"tenant.{tenant.slug}"
                
                # Revoga chaves existentes
                existing_keys = APIKey.objects.filter(name__startswith=key_name)
                if existing_keys.exists():
                    existing_keys.delete()
                    
                # Cria nova chave
                api_key, key = APIKey.objects.create_key(name=key_name)
                
                # Adiciona ao resultado
                results.append((tenant.nome, key))
            
            # Construa uma mensagem HTML com as chaves geradas
            message = format_html(
                "<p>Chaves API geradas com sucesso:</p><ul>{}</ul><p><strong>Importante:</strong> Guarde estas chaves em um local seguro. Elas não serão exibidas novamente.</p>",
                format_html("".join(
                    [format_html("<li><strong>{}:</strong> {}</li>", tenant_name, key) for tenant_name, key in results]
                ))
            )
            
            self.message_user(request, message)
            return
            
        # Se apenas um tenant foi selecionado, redirecionamos para uma página específica
        tenant = queryset.first()
        key_name = f"tenant.{tenant.slug}"
        
        # Revoga chaves existentes
        existing_keys = APIKey.objects.filter(name__startswith=key_name)
        if existing_keys.exists():
            existing_keys.delete()
            
        # Cria nova chave
        api_key, key = APIKey.objects.create_key(name=key_name)
        
        # Redireciona para a página de detalhes da chave - MODIFICADO AQUI
        return redirect('display_api_key', tenant_id=tenant.id, api_key=key)

@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ('email_host', 'email_host_user', 'ativar_notificacoes', 'email_notificacao', 'ativo')
    fieldsets = (
        ('Status', {
            'fields': ('ativo', 'ativar_notificacoes', 'email_notificacao')
        }),
        ('Configurações SMTP', {
            'fields': ('email_backend', 'email_host', 'email_port', 'email_use_tls', 'email_host_user', 'email_host_password', 'default_from_email')
        }),
    )

    def has_add_permission(self, request):
        # Verificar se já existe uma configuração
        if EmailConfig.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(TenantAPIKey)
class TenantAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'last_used', 'usage_count', 'ativo')
    list_filter = ('ativo', 'last_used')
    search_fields = ('tenant__nome', 'tenant__slug')
    readonly_fields = ('tenant', 'last_used', 'last_ip', 'usage_count')
    
    def has_add_permission(self, request):
        # Não permitir adicionar manualmente, apenas via ação do TenantAdmin
        return False
