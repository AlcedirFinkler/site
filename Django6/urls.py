# urls.py from Django

from django.contrib import admin
from django.urls import path, include
from core.views import display_api_key

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Defina a URL personalizada ANTES das URLs do admin
    path('admin/api-key/<int:tenant_id>/<str:api_key>/', display_api_key, name='display_api_key'),
    path('admin/', admin.site.urls),  # URLs do admin
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)