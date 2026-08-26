from django.urls import path
from .import views
from .views import (
    ChangePasswordView,
    DengueCaseCreateView,
    DengueFocusCreateView,
    EstatisticasView,
    MyTokenObtainPairView,
    PasswordResetWebConfirm,
    PasswordTokenCheckAPI,
    RequestPasswordResetEmail,
    UserDeleteView,
    UserProfileView,
    UserRegistrationView,
    check_login_status,
    estatisticas_view,
    google_callback_manual,
    start_login,
)
from .views import PasswordResetWebConfirm

urlpatterns = [
    # --- Autenticação JWT ---
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('delete-account/', UserDeleteView.as_view(), name='user_delete'),

    # --- Login Google (Manual) ---
    path('start-login/', views.start_login, name='start_login'),
    path('google-callback/', views.google_callback_manual, name='google_callback_manual'),
    path('check-login/', views.check_login_status, name='check_login_status'),
    
    # --- Recuperação de Senha ---
    path('password-reset-request/', RequestPasswordResetEmail.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-web/<uidb64>/<token>/', PasswordResetWebConfirm.as_view(), name='password-reset-web'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),

    path('report-focus/', DengueFocusCreateView.as_view(), name='report-focus'),
    path('report-case/', DengueCaseCreateView.as_view(), name='report-case'),
    path('report-positive-case/', views.PositiveDengueCaseCreateView.as_view(), name='report-positive-case'),

    path('estatisticas/', estatisticas_view, name='estatisticas'),
]