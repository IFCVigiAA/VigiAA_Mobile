from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse

# Importações para o Login Social (Google)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Importamos o nosso serializer
from .serializers import MyTokenObtainPairSerializer 

# api/views.py
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required

@login_required
@login_required
def google_callback_token(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # HTML simples para copiar o token
    return HttpResponse(f"""
        <div style="background-color:black; color:#00ff00; padding:20px; font-family:monospace; word-break:break-all;">
            <h1>LOGIN SUCESSO!</h1>
            <p>Copie o token abaixo:</p>
            <br>
            <p>{access_token}</p>
        </div>
    """)

# Não esqueça de importar HttpResponse: from django.http import HttpResponse


# -----------------------------------
# 1. VIEW DE LOGIN (JWT)
# -----------------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# -----------------------------------
# 2. VIEW DE REGISTRO
# -----------------------------------
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        email = request.data.get('email', '')
        
        # Novos campos
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not username or not password or not password2:
            return Response({'error': 'Usuário e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != password2:
            return Response({'error': 'As senhas não coincidem.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Nome de usuário já existe.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            return Response({'message': 'Usuário criado com sucesso!'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': f'Erro ao criar usuário: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------
# 3. VIEW DE EXCLUSÃO DE CONTA
# -----------------------------------
class UserDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            if not user or not user.is_active:
                 return Response({'error': 'Usuário inválido ou já desativado.'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = False
            user.save()
            return Response({'message': 'Conta desativada com sucesso.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'Erro ao desativar conta: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------
# 4. VIEW DE LOGIN COM GOOGLE (A QUE FALTAVA!)
# -----------------------------------
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # URL de callback configurada no Google Cloud
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
    client_class = OAuth2Client