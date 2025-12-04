import flet as ft
import requests
import time
import certifi
import urllib3
import charset_normalizer
import config  # Importa as configurações globais (Ícones, URL)
import urllib.parse
from home_view import create_main_view  # Importa a sua tela Home com abas

# Atalhos vindos do config.py
ICONS = config.ICONS
API_URL = config.API_URL

# ===============================================
# TELA DE LOGIN (COM GOOGLE + TOKEN MANUAL)
# ===============================================
def create_login_view(page: ft.Page):
    
    # Campos de Login Tradicional
    username_field = ft.TextField(label="Usuário", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    
    # --- CAMPO ESPECIAL (DEV MODE) ---
    # Serve para você colar o token que aparece na tela preta/verde do navegador
    google_token_field = ft.TextField(
        label="Token Google (Cole aqui)", 
        width=300, 
        text_size=12,
        hint_text="Copie o token da tela verde e cole aqui",
        icon=ICONS.VPN_KEY,
        bgcolor="grey" # Corrigido: Usando string para evitar erro de versão
    )
    
    error_text = ft.Text(color="red")

    # --- Função que valida o Token e Redireciona ---
    def finalize_login_with_token(token):
        # Validação simples
        if not token or len(token) < 10:
            return
        
        # 1. Salva o token no celular/PC
        page.client_storage.set("token", token)
        
        print(f"Token salvo: {token[:15]}...")
        
        # 2. Feedback visual
        error_text.value = "Login validado! Carregando..."
        error_text.color = "green"
        page.update()
        
        # 3. Aguarda um pouco e manda para a Home
        time.sleep(1)
        page.go("/") 

    # Monitora o campo de colar token
    def on_token_change(e):
        # Se colar um texto grande, tenta logar automaticamente
        if len(e.control.value) > 20: 
             finalize_login_with_token(e.control.value)

    google_token_field.on_change = on_token_change

    # --- Ação do Botão Google ---
# Esta função deve estar alinhada com as outras variáveis dentro de create_login_view
    def google_login_clicked(e):
        # Opção segura: Usar o link exato do Ngrok
        # Cole aqui o link que aparece no seu terminal preto do Ngrok
        google_url = "https://froglike-cataleya-quirkily.ngrok-free.dev/accounts/google/login/"
        
        # Se quiser usar a lógica automática (só se API_URL estiver certa):
        # base_url = API_URL.replace("/api", "")
        # google_url = f"{base_url}/accounts/google/login/"
        
        page.launch_url(google_url)

    # --- Ação do Login Tradicional ---
    def login_clicked(e):
        e.control.disabled = True
        e.control.text = "Verificando..."
        page.update()

        try:
            response = requests.post(
                f"{API_URL}/token/", 
                data={"username": username_field.value, "password": password_field.value},
                timeout=5
            )
            
            if response.status_code == 200:
                # Se login ok, pega o token e usa a mesma função de finalizar
                token = response.json().get("access")
                finalize_login_with_token(token)
            else:
                error_text.value = "Usuário ou senha incorretos."
                error_text.color = "red"
                e.control.disabled = False
                e.control.text = "Entrar"
                page.update()
                
        except Exception as ex:
            error_text.value = "Erro de conexão com o servidor."
            print(ex)
            e.control.disabled = False
            e.control.text = "Entrar"
            page.update()

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("VigiAA", size=30, weight="bold", color="blue"),
                        ft.Text("Login", size=16),
                        ft.Container(height=20),
                        
                        # Área Login Senha
                        username_field, 
                        password_field,
                        ft.ElevatedButton("Entrar", on_click=login_clicked, width=300),
                        
                        ft.Container(height=10),
                        ft.Text("ou"),
                        ft.Container(height=10),
                        
                        # Botão Google
                        ft.ElevatedButton(
                            text="Entrar com Google",
                            icon=ICONS.G_MOBILEDATA,
                            width=300,
                            color="black",
                            bgcolor="white",
                            on_click=google_login_clicked
                        ),
                        
                        ft.Divider(),
                        
                        # Área Dev Mode (Colar Token)
                        ft.Text("DEV MODE: Colar Token do Google:", size=10, color="grey"),
                        google_token_field,
                        
                        ft.Container(height=10),
                        error_text,
                        
                        # Link para Registro
                        ft.TextButton("Criar nova conta", on_click=lambda _: page.go("/register"))
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center, expand=True, padding=20
            )
        ]
    )

# ===============================================
# TELA DE REGISTRO
# ===============================================
def create_register_view(page: ft.Page):
    
    username_field = ft.TextField(label="Usuário", width=300)
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Senha", password=True, width=300)
    password2_field = ft.TextField(label="Confirmar Senha", password=True, width=300)
    first_name_field = ft.TextField(label="Nome", width=300)
    last_name_field = ft.TextField(label="Sobrenome", width=300)
    error_text = ft.Text(color="red")
    
    def register_clicked(e):
        e.control.disabled = True
        e.control.text = "Criando..."
        page.update()

        try:
            response = requests.post(
                f"{API_URL}/register/",
                json={
                    "username": username_field.value,
                    "email": email_field.value,
                    "password": password_field.value,
                    "password2": password2_field.value,
                    "first_name": first_name_field.value,
                    "last_name": last_name_field.value
                },
                timeout=10
            )
            
            if response.status_code == 201:
                error_text.value = "Conta criada! Faça o login."
                error_text.color = "green"
                page.update()
                time.sleep(1.5)
                page.go("/login")
            else:
                error_text.value = f"Erro: {response.text}"
                e.control.disabled = False
                e.control.text = "Registrar"
                page.update()

        except Exception as ex:
            error_text.value = f"Erro: {ex}"
            e.control.disabled = False
            e.control.text = "Registrar"
            page.update()

    return ft.View(
        route="/register",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Criar Conta", size=32, weight="bold"),
                        first_name_field, last_name_field, username_field, email_field, password_field, password2_field,
                        ft.ElevatedButton("Registrar", on_click=register_clicked),
                        error_text,
                        ft.TextButton("Voltar ao Login", on_click=lambda _: page.go("/login"))
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO
                ),
                alignment=ft.alignment.center, expand=True, padding=20
            )
        ]
    )

# ===============================================
# ROTEAMENTO INTELIGENTE (COM DEEP LINK)
# ===============================================
def route_change(e: ft.RouteChangeEvent, page: ft.Page):
    print(f"Rota: {page.route}") 

    # --- LÓGICA MÁGICA (DEEP LINK) ---
    if page.route.startswith("/login-callback"):
        try:
            # Pega o token escondido na URL
            parsed = urllib.parse.urlparse(page.route)
            token = urllib.parse.parse_qs(parsed.query).get('access', [None])[0]
            
            if token:
                page.client_storage.set("token", token)
                print("Token pego automaticamente!")
                page.go("/") # Manda direto para a Home
                return
        except Exception as ex:
            print(f"Erro Deep Link: {ex}")

    # --- LÓGICA PADRÃO ---
    page.views.clear()
    token = page.client_storage.get("token")

    if page.route == "/login":
        page.views.append(create_login_view(page))
    elif page.route == "/register":
        page.views.append(create_register_view(page))
    elif page.route == "/" or page.route == "":
        if token:
            page.views.append(create_main_view(page)) 
        else:
            page.go("/login")
    else:
        page.go("/login")
    
    page.update()

# ===============================================
# INICIALIZAÇÃO DO APP
# ===============================================
def main(page: ft.Page):
    page.title = "VigiAA"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configura o roteador
    page.on_route_change = lambda e: route_change(e, page)
    
    # Configura o botão "Voltar" do Android
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    page.on_view_pop = view_pop

    # Inicia na rota /
    page.go(page.route)

try:
    # Tenta ativar o Deep Link (Se o Flet for novo)
    ft.app(target=main, assets_dir="assets", deep_link_url_scheme="vigiaa")
except TypeError:
    # Se o Flet for velho, roda sem Deep Link (pelo menos o app abre)
    print("ERRO CRITICO: Flet desatualizado no APK!")
    ft.app(target=main, assets_dir="assets")