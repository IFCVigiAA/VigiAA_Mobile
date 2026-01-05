from django.urls import path
from . import views
from .views import (
    MyTokenObtainPairView, 
    UserRegistrationView, 
    UserDeleteView, 
    RequestPasswordResetEmail, 
    PasswordTokenCheckAPI,
    UserProfileView,
    ChangePasswordView
)
from .views import PasswordResetWebConfirm

urlpatterns = [
    # --- Autenticação JWT ---
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/register/', UserRegistrationView.as_view(), name='user_register'),
    path('api/delete-account/', UserDeleteView.as_view(), name='user_delete'),

    # --- Login Google (Manual) ---
    path('api/start-login/', views.start_login, name='start_login'),
    path('api/google-callback/', views.google_callback_manual, name='google_callback_manual'),
    path('api/check-login/', views.check_login_status, name='check_login_status'),
    
    # --- Recuperação de Senha ---
    path('api/password-reset-request/', RequestPasswordResetEmail.as_view(), name='password-reset-request'),
    path('api/password-reset-confirm/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('api/password-reset-web/<uidb64>/<token>/', PasswordResetWebConfirm.as_view(), name='password-reset-web'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
]