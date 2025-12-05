import flet as ft
import requests
import time
import certifi
import urllib3
import charset_normalizer
import config  # Importa as configurações globais (Ícones, URL)
import urllib.parse
from home_view import create_main_view  # Importa a sua tela Home com abas
import uuid
import threading

# Atalhos vindos do config.py
ICONS = config.ICONS
API_URL = config.API_URL

# ===============================================
# TELA DE LOGIN (COM GOOGLE + TOKEN MANUAL + POLLING)
# ===============================================
def create_login_view(page: ft.Page):
    
    # Campos de Login Tradicional
    username_field = ft.TextField(label="Usuário", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    
    # Textos de status
    status_text = ft.Text(value="Pronto para iniciar.", color="grey", size=12)
    error_text = ft.Text(color="red")
    
    # Botão de verificação manual (aparece se demorar)
    check_now_button = ft.ElevatedButton("Já fiz o login (Verificar)", visible=False)

    # --- Função Auxiliar: Salva o Token e Entra ---
    def finalize_login(token):
        if not token: return
        page.client_storage.set("token", token)
        status_text.value = "SUCESSO! Entrando..."
        status_text.color = "green"
        page.update()
        time.sleep(1)
        page.go("/")

    # --- Lógica de Verificação no Servidor (Polling) ---
    def check_status(login_id):
        try:
            status_text.value = f"Consultando servidor... ({login_id[:4]})"
            page.update()
            
            # Remove barra extra se tiver para montar a URL certa
            clean_api_url = API_URL.rstrip('/')
            check_url = f"{clean_api_url}/check-login/?login_id={login_id}"
            
            print(f"Consultando: {check_url}")
            res = requests.get(check_url, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if data.get('status') == 'success':
                    token = data.get('access_token')
                    finalize_login(token)
                    return True # Sucesso, para o loop
                else:
                    status_text.value = "Ainda aguardando login..."
            else:
                status_text.value = f"Servidor respondeu: {res.status_code}"
                
        except Exception as ex:
            status_text.value = f"Erro de conexão..."
            print(ex)
        
        page.update()
        return False

    # --- Ação do Botão Google (Inicia o Processo) ---
    def google_login_clicked(e):
        # 1. Gera ID único para essa tentativa
        login_id = str(uuid.uuid4())
        
        # 2. Monta o link do Google com esse ID (state)
        # Pega a base do Ngrok tirando o /api do final
        base_url = API_URL.split("/api")[0] 
        google_url = f"{base_url}/accounts/google/login/?state={login_id}"
        
        # 3. Abre o navegador
        page.launch_url(google_url)
        
        # 4. Atualiza a tela
        e.control.disabled = True
        e.control.text = "Aguardando login..."
        status_text.value = "Navegador aberto. Faça login e volte aqui."
        status_text.color = "blue"
        
        # Habilita botão manual caso o automático falhe
        check_now_button.visible = True
        check_now_button.on_click = lambda _: check_status(login_id)
        page.update()

        # 5. Inicia a verificação em segundo plano (Thread)
        def poll_loop():
            attempts = 0
            # Tenta por 60 vezes (2 segundos cada = 2 minutos)
            while attempts < 60: 
                time.sleep(2)
                # Se achou o token, para tudo e entra
                if check_status(login_id): 
                    return
                attempts += 1
            
            # Se acabou o tempo
            e.control.disabled = False
            e.control.text = "Entrar com Google"
            status_text.value = "Tempo esgotado. Tente novamente."
            page.update()

        threading.Thread(target=poll_loop, daemon=True).start()

    # --- Ação do Login Tradicional ---
    def login_clicked(e):
        try:
            status_text.value = "Verificando senha..."
            page.update()
            res = requests.post(
                f"{API_URL}/token/", 
                data={"username": username_field.value, "password": password_field.value}
            )
            if res.status_code == 200:
                finalize_login(res.json().get("access"))
            else:
                status_text.value = "Usuário ou senha incorretos."
                status_text.color = "red"
                page.update()
        except Exception as ex:
            status_text.value = f"Erro: {ex}"
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
                        
                        username_field, 
                        password_field,
                        ft.ElevatedButton("Entrar", on_click=login_clicked, width=300),
                        
                        ft.Container(height=10),
                        ft.Text("ou"),
                        ft.Container(height=10),
                        
                        # Botão Google Inteligente
                        ft.ElevatedButton(
                            text="Entrar com Google",
                            icon=ICONS.G_MOBILEDATA,
                            width=300,
                            color="black",
                            bgcolor="white",
                            on_click=google_login_clicked
                        ),
                        
                        ft.Container(height=10),
                        status_text,      # Mostra o progresso
                        check_now_button, # Botão de emergência
                        error_text,
                        
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
# ROTEAMENTO E REGISTRO
# ===============================================
def create_register_view(page: ft.Page):
    # (Mantive simplificado para caber, mas sua lógica original funciona aqui)
    return ft.View(route="/register", controls=[ft.Text("Tela de Registro")]) 

def route_change(e: ft.RouteChangeEvent, page: ft.Page):
    page.views.clear()
    token = page.client_storage.get("token")

    if page.route == "/login":
        page.views.append(create_login_view(page))
    elif page.route == "/register":
        from register_view import create_register_view # Importa só quando precisa
        page.views.append(create_register_view(page))
    elif page.route == "/" or page.route == "":
        if token:
            page.views.append(create_main_view(page)) 
        else:
            page.go("/login")
    else:
        page.go("/login")
    
    page.update()

def main(page: ft.Page):
    page.title = "VigiAA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.on_route_change = lambda e: route_change(e, page)
    page.go(page.route)

# SEM O DEEP LINK (Para evitar o erro de versão)
ft.app(target=main, assets_dir="assets")