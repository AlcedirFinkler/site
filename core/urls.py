# urls.py from core

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views
from core.views import display_api_key

router = DefaultRouter()
router.register('tenants', views.TenantViewSet, basename='tenant')

from .views import (
    IndexView, 
    CadastroUsuarioView, 
    CadastroTenantView, 
    TenantSucessoView,
    PlanosView,
    verify_api_key
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('planos/', PlanosView.as_view(), name='planos'),
    path('cadastro/', CadastroUsuarioView.as_view(), name='cadastro_usuario'),
    path('tenant/', CadastroTenantView.as_view(), name='cadastro_tenant'),
    path('tenant/sucesso/', TenantSucessoView.as_view(), name='tenant_sucesso'),
    path('api/', include(router.urls)),
    path('api/tenant-info/', views.tenant_info, name='tenant-info'),
    path('api/verify-key/', views.verify_api_key, name='verify-api-key'),
]