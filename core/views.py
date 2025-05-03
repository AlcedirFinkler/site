from django.views.generic import FormView, CreateView, DetailView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.db import transaction

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from .serializers import TenantSerializer
from django.utils.timezone import now

from .models import PlanoAssinatura, Tenant, TenantAPIKey
from .forms import ContatoForm, CadastroUsuarioForm, CadastroTenantForm

from .utils import send_tenant_notification

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.urls import path
from rest_framework_api_key.models import APIKey

class IndexView(FormView):
    template_name = 'index.html'
    form_class = ContatoForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['planos'] = PlanoAssinatura.objects.filter(ativo=True)
        return context

    def form_valid(self, form, *args, **kwargs):
        form.send_mail()
        messages.success(self.request, 'E-mail enviado com sucesso')
        return super(IndexView, self).form_valid(form, *args, **kwargs)
    
    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro ao enviar o e-mail')
        return super(IndexView, self).form_invalid(form, *args, **kwargs)

class CadastroUsuarioView(CreateView):
    template_name = 'cadastro_usuario.html'
    form_class = CadastroUsuarioForm
    success_url = reverse_lazy('cadastro_tenant')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, 'Cadastro realizado com sucesso! Agora configure seu tenant.')
        return response

class CadastroTenantView(LoginRequiredMixin, CreateView):
    template_name = 'cadastro_tenant.html'
    form_class = CadastroTenantForm
    success_url = reverse_lazy('tenant_sucesso')
    login_url = 'cadastro_usuario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['planos'] = PlanoAssinatura.objects.filter(ativo=True)
        return context

    def form_valid(self, form):
        with transaction.atomic():
            tenant = form.save(commit=False)
            tenant.usuario = self.request.user
            
            # Pega o CPF/CNPJ do formulário e salva no modelo
            tenant.cpf_cnpj = form.cleaned_data.get('cpf_cnpj')
            
            tenant.save()
            
            # Em uma implementação completa, aqui seria chamado o serviço 
            # para criação do tenant na infraestrutura
            
            # Envia notificação por email
            send_tenant_notification(tenant)
            
            messages.success(self.request, 'Tenant criado com sucesso!')
            return super().form_valid(form)

class TenantSucessoView(LoginRequiredMixin, TemplateView):
    template_name = 'tenant_sucesso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['tenant'] = Tenant.objects.get(usuario=self.request.user)
        except Tenant.DoesNotExist:
            pass
        return context

class PlanosView(TemplateView):
    template_name = 'planos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['planos'] = PlanoAssinatura.objects.filter(ativo=True)
        return context
    
class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [HasAPIKey]
    
    def get_queryset(self):
        slug = self.request.query_params.get('slug', None)
        if slug:
            return Tenant.objects.filter(slug=slug, ativo=True)
        return Tenant.objects.none()

@api_view(['GET'])
@permission_classes([HasAPIKey])
def tenant_info(request):
    slug = request.query_params.get('slug', None)
    if not slug:
        return Response({"error": "Parâmetro 'slug' é obrigatório"}, status=400)
    
    try:
        tenant = Tenant.objects.get(slug=slug)
        serializer = TenantSerializer(tenant)
        
        # Adiciona informações sobre recursos disponíveis baseados no plano
        response_data = serializer.data
        response_data['recursos'] = {}
        
        if tenant.plano.nivel == 'nivel1':
            response_data['recursos']['usuarios_max'] = 5
            response_data['recursos']['ativos_max'] = 50
            response_data['recursos']['api_access'] = False
            response_data['recursos']['dashboards'] = False
        elif tenant.plano.nivel == 'nivel2':
            response_data['recursos']['usuarios_max'] = 20
            response_data['recursos']['ativos_max'] = 500
            response_data['recursos']['api_access'] = True
            response_data['recursos']['dashboards'] = True
        elif tenant.plano.nivel == 'nivel3':
            response_data['recursos']['usuarios_max'] = 0  # ilimitado
            response_data['recursos']['ativos_max'] = 0  # ilimitado
            response_data['recursos']['api_access'] = True
            response_data['recursos']['dashboards'] = True
            response_data['recursos']['predictive_maintenance'] = True
            response_data['recursos']['machine_learning'] = True
            
        # Adiciona o status de acesso com base no pagamento e status ativo
        if not tenant.ativo:
            response_data['access_status'] = 'blocked'
        elif tenant.status_pagamento == 'atraso':
            response_data['access_status'] = 'grace_period'
        elif tenant.status_pagamento == 'expirado':
            response_data['access_status'] = 'expired'
        else:
            response_data['access_status'] = 'active'
            
        return Response(response_data)
    except Tenant.DoesNotExist:
        return Response({"error": "Tenant não encontrado"}, status=404)
    
@api_view(['GET'])
@permission_classes([HasAPIKey])
def verify_api_key(request):
    """
    Endpoint simples para verificar se a API Key está funcionando
    """
    return Response({
        "status": "success",
        "message": "API Key válida",
        "timestamp": timezone.now().isoformat()
    })

@staff_member_required
def display_api_key(request, tenant_id, api_key):
    """
    Exibe a chave API gerada para um tenant. 
    Esta view só é acessível uma vez, imediatamente após a geração da chave.
    """
    # Adicione depuração para ver o que está sendo recebido
    print(f"Recebendo request para tenant_id={tenant_id}, api_key={api_key}")
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Segurança: Verifica se a chave pertence ao tenant
    try:
        # Tenta decodificar a chave para confirmar que é válida
        api_key_obj = APIKey.objects.get_from_key(api_key)
        expected_prefix = f"tenant.{tenant.slug}"
        
        print(f"Chave API encontrada: {api_key_obj.name}")
        print(f"Prefixo esperado: {expected_prefix}")
        
        if not api_key_obj.name.startswith(expected_prefix):
            raise Http404("Chave inválida para este tenant")
    except Exception as e:
        print(f"Erro ao validar chave API: {str(e)}")
        raise Http404("Chave inválida")
    
    # Obtém ou cria metadados da API Key
    meta, created = TenantAPIKey.objects.get_or_create(
        tenant=tenant,
        defaults={
            'last_used': None,
            'last_ip': None,
            'usage_count': 0
        }
    )
    
    # Constrói URL base para o exemplo de API
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    api_url = f"{protocol}://{host}"
    
    context = {
        'tenant': tenant,
        'api_key': api_key,
        'key_generated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        'api_url': api_url,
        # Adicionar variáveis de contexto para o admin
        'site_header': 'Weconn Administration',
        'site_title': 'Weconn Admin',
    }
    
    # Verifique se o template existe
    try:
        from django.template.loader import get_template
        template = get_template('admin/display_api_key.html')
        print(f"Template encontrado: {template}")
    except Exception as e:
        print(f"Erro ao carregar template: {str(e)}")
        # Fallback para um template básico
        return render(request, 'admin/base.html', {
            'title': 'Chave API Gerada',
            'content': f'Sua chave API foi gerada: {api_key}',
            **context
        })
    
    # Renderiza o template normalmente
    return render(request, 'admin/display_api_key.html', context)
