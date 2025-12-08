from django.urls import path
# ADICIONADO: UserDeleteView na importação
from .views import MyTokenObtainPairView, UserRegistrationView, UserDeleteView

from .views import google_callback_token
from .views import google_callback_token, check_login_status
from .views import google_callback_token, check_login_status, start_login

urlpatterns = [
    # Login
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Registro
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    
    # Exclusão de Conta
    path('delete-account/', UserDeleteView.as_view(), name='user_delete'),

    path('google-callback/', google_callback_token, name='google_callback'),

    path('check-login/', check_login_status, name='check_login'),

    path('start-login/', start_login, name='start_login'),
]