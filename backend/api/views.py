from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.models import update_last_login
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings # Para pegar variáveis do settings se precisar

# DRF e JWT
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from .serializers import PasswordResetRequestSerializer, SetNewPasswordSerializer

# Requests para falar com o Google manualmente
import requests 
import urllib.parse
import os

# Seus Serializers
from .serializers import MyTokenObtainPairSerializer 

# ==============================================================================
# CONFIGURAÇÕES DO GOOGLE (PREENCHA AQUI OU PEGUE DO SETTINGS/ENV)
# ==============================================================================

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "https://froglike-cataleya-quirkily.ngrok-free.dev/api/google-callback/"

# ==============================================================================
# LÓGICA MANUAL DE LOGIN (O QUE O PROFESSOR PEDIU)
# ==============================================================================

def get_tokens_for_user(user):
    """Gera o JWT manualmente para um usuário"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def start_login(request):
    """
    1. Inicia o processo, salva o ID do celular no Cookie.
    2. Redireciona o usuário para a página de permissão do Google.
    """
    login_id = request.GET.get('login_id')

    # Montamos a URL do Google manualmente (sem allauth)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    # Cria a string: https://accounts.google.com...?client_id=...
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    # HTML que joga o usuário para o Google
    html = f"""
    <html>
        <body>
            <h3>Redirecionando para o Google...</h3>
            <script>
                window.location.href = '{google_auth_url}';
            </script>
        </body>
    </html>
    """
    
    response = HttpResponse(html)
    
    # Salva o ID do celular no cookie seguro
    if login_id:
        response.set_cookie(
            key='mobile_login_id', 
            value=login_id, 
            max_age=300, 
            samesite='None', 
            secure=True,
            httponly=True
        )
        print(f"DEBUG: Cookie 'mobile_login_id' gravado com: {login_id}")
    
    return response

@csrf_exempt
def google_callback_manual(request):
    """
    3. O Google devolve o usuário para cá com um 'code'.
    4. Nós trocamos o 'code' por dados do usuário.
    5. Salvamos na tabela auth_user e geramos o JWT.
    """
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error or not code:
        return HttpResponse("<h1>Erro no login com Google. Tente novamente.</h1>")

    # --- PASSO A: Trocar o CODE pelo ACCESS TOKEN ---
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    res = requests.post(token_url, data=data)
    token_json = res.json()
    access_token = token_json.get('access_token')

    if not access_token:
        return HttpResponse(f"<h1>Erro ao obter token do Google: {res.text}</h1>")

    # --- PASSO B: Pegar os dados do usuário (Email/Nome) ---
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    user_info_res = requests.get(user_info_url, params={'access_token': access_token, 'alt': 'json'})
    user_info = user_info_res.json()

    email = user_info.get('email')
    first_name = user_info.get('given_name', '')
    last_name = user_info.get('family_name', '')

    if not email:
        return HttpResponse("<h1>Google não forneceu o email.</h1>")

# --- PASSO C: A MÁGICA DO PROFESSOR (Só usa auth_user) ---
    try:
        # Tenta achar o usuário pelo email na tabela padrão
        user = User.objects.get(email=email)
        print(f"Usuário encontrado: {user.username}")
        
        if not user.is_active:
            print("Usuário estava desativado. Reativando conta...")
            user.is_active = True
            user.save()

    except User.DoesNotExist:
        print("Criando novo usuário...")
        user = User.objects.create_user(
            username=email, 
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_unusable_password() 
        user.save()

    update_last_login(None, user)

    # --- PASSO D: Gerar Token JWT e Salvar no Cache ---
    jwt_access_token = get_tokens_for_user(user)
    
    # Recupera o ID do celular do cookie
    login_id = request.COOKIES.get('mobile_login_id')

    response = render(request, 'google_success.html') # <--- Carrega o arquivo bonitinho

    if login_id:
        print(f"DEBUG: Cookie encontrado! ID: {login_id}")
        # Guarda o token no cache para o celular buscar
        cache.set(f"login_token_{login_id}", jwt_access_token, timeout=300)
        # Limpa o cookie para não ficar lixo no navegador
        response.delete_cookie('mobile_login_id')
    else:
        print("AVISO: Cookie sumiu, mas o usuário foi criado/logado.")

    return response

def check_login_status(request):
    # Essa função continua IGUAL, pois o Flet não sabe o que mudou no backend
    login_id = request.GET.get('login_id')
    
    if not login_id:
        return JsonResponse({'status': 'waiting'}, status=400)

    token = cache.get(f"login_token_{login_id}")
    
    if token:
        cache.delete(f"login_token_{login_id}")
        return JsonResponse({'status': 'success', 'access_token': token})
    else:
        return JsonResponse({'status': 'waiting'})


# ==============================================================================
# VIEWS PADRÃO (REGISTRO, LOGIN SENHA, ETC) - MANTIDAS
# ==============================================================================

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        email = request.data.get('email', '')
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
        

# --- FLUXO DE RECUPERAÇÃO DE SENHA ---

class RequestPasswordResetEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = PasswordResetTokenGenerator().make_token(user)
                
                # --- AQUI ESTÁ A MÁGICA DO LINK ---
                # Pegamos o domínio atual (ex: ngrok) dinamicamente ou fixo
                # Para simplificar, vamos pegar o que veio na requisição ou defina manualmente
                # Vamos assumir que você vai configurar o DOMINIO no settings ou usar o host atual
                current_site = request.META.get('HTTP_HOST') # Pega o ngrok atual
                
                # Monta o link clicável
                abs_url = f"https://{current_site}/api/password-reset-web/{uidb64}/{token}/"
                
                email_body = f"""
                Olá,
                
                Clique no link abaixo para redefinir sua senha do VigiAA:
                {abs_url}
                
                Se não foi você, ignore.
                """
                
                send_mail('Redefinir Senha - VigiAA', email_body, 'noreply@vigiaa.com', [email], fail_silently=False)
            
            return Response({'message': 'Email enviado.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordTokenCheckAPI(APIView):
    permission_classes = [AllowAny]
    
    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Senha redefinida com sucesso!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetWebConfirm(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'reset_password.html'

    def get(self, request, uidb64, token):
        return Response({'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        # 1. Conferência de Backend (Segurança)
        if password != confirm_password:
            return Response({
                'error': 'As senhas não conferem.',
                'uidb64': uidb64,
                'token': token
            })

        # 2. Processa a troca
        serializer = SetNewPasswordSerializer(data={
            'uidb64': uidb64, 
            'token': token, 
            'password': password
        })

        if serializer.is_valid():
            return Response({'success': True})
        else:
            error_msg = list(serializer.errors.values())[0][0]
            return Response({'error': error_msg, 'uidb64': uidb64, 'token': token})