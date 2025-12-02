"""
Arquivo de URLs principal. Este é o 'Conector' que liga a URL /api/ ao seu app.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas da sua API (Login normal, Registro, etc)
    path('api/', include('api.urls')),
    
    # --- ROTAS DO GOOGLE LOGIN (NOVO) ---
    # Isso diz ao Django: "Tudo que começar com 'accounts/', 
    # mande para o pacote allauth cuidar."
    path('accounts/', include('allauth.urls')),
]