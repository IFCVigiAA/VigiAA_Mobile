from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Mantenha apenas o include do seu app 'api'
    path('', include('api.urls')), 
]