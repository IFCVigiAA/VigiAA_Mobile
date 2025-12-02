from django.urls import path
# ADICIONADO: UserDeleteView na importação
from .views import MyTokenObtainPairView, UserRegistrationView, UserDeleteView

from .views import google_callback_token

urlpatterns = [
    # Login
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Registro
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    
    # Exclusão de Conta
    path('delete-account/', UserDeleteView.as_view(), name='user_delete'),

    path('google-callback/', google_callback_token, name='google_callback'),
]