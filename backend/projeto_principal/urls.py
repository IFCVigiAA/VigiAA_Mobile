from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from api.views import estatisticas_view 

urlpatterns = [
    # ... suas rotas existentes ...
    path('api/estatisticas/', estatisticas_view, name='estatisticas'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
