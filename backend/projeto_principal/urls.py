from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

#graficokk

from django.urls import path
from api.views import estatisticas_view 

urlpatterns = [
    # ... suas rotas existentes ...
    path('api/estatisticas/', estatisticas_view, name='estatisticas'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Mantenha apenas o include do seu app 'api'
    path('', include('api.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Substitua 'nome_do_seu_app' pelo nome da pasta do seu aplicativo Django:
    path('api/', include('api.urls')),
]