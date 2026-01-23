import flet as ft
import requests
import config
import threading
import time
import uuid

def create_login_view(page: ft.Page):
    API_URL = config.API_URL
    HEADERS = {"ngrok-skip-browser-warning": "true"}

    # --- DEFINIÇÃO DOS CAMPOS (Nomes Corrigidos) ---
    email_field = ft.TextField(
        hint_text="email@domain.com", 
        bgcolor="white", 
        border_radius=10, 
        border_width=0, 
        text_size=14, 
        content_padding=15, 
        color="black", 
        cursor_color="black"
    )

    # AQUI ESTAVA O ERRO: Agora garantimos que o nome é password_field
    password_field = ft.TextField(
        hint_text="senha", 
        password=True, 
        can_reveal_password=True, 
        bgcolor="white", 
        border_radius=10, 
        border_width=0, 
        text_size=14, 
        content_padding=15, 
        color="black", 
        cursor_color="black"
    )
    
    error_text = ft.Text(color="red", size=14, weight="bold", text_align=ft.TextAlign.CENTER)

    # --- LÓGICA DE LOGIN MANUAL ---
    def login_click(e):
        if not email_field.value or not password_field.value:
            error_text.value = "Preencha todos os campos"
            error_text.update()
            return

        error_text.value = "Conectando..."
        error_text.color = "blue"
        error_text.update()

        try:
            response = requests.post(
                f"{API_URL}/api/token/", 
                data={
                    "username": email_field.value, 
                    "password": password_field.value
                }, 
                headers=HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access")
                page.client_storage.set("token", token)
                page.go("/")
            else:
                error_text.value = "Email ou senha incorretos."
                error_text.color = "red"
                error_text.update()
        except Exception as ex:
            error_text.value = f"Erro: {ex}"
            error_text.color = "red"
            error_text.update()

    def go_register(e):
        page.go("/register")
    
    # --- LÓGICA DO GOOGLE (POLLING) ---
    def check_google_status(login_id):
        # Tenta verificar se logou por 60 segundos
        for _ in range(60):
            time.sleep(2) # Espera 2s
            try:
                res = requests.get(f"{API_URL}/api/check-login/?login_id={login_id}", headers=HEADERS)
                if res.status_code == 200:
                    data = res.json()
                    # Verifica se o backend retornou sucesso e o token
                    if data.get('status') == 'success':
                        token = data.get('access_token')
                        
                        # Mágica para atualizar a tela principal
                        page.client_storage.set("token", token)
                        page.go("/")
                        page.update()
                        return
            except:
                pass
        
        # Se passar 1 minuto e não logar
        error_text.value = "Tempo limite do Google esgotado."
        error_text.color = "red"
        error_text.update()

    def login_google(e):
        try:
            # 1. Gera ID único
            my_login_id = str(uuid.uuid4())
            
            # 2. Abre navegador com esse ID
            page.launch_url(f"{API_URL}/api/start-login/?login_id={my_login_id}")
            
            error_text.value = "Aguardando confirmação no navegador..."
            error_text.color = "blue"
            error_text.update()

            # 3. Inicia verificação em segundo plano
            t = threading.Thread(target=check_google_status, args=(my_login_id,), daemon=True)
            t.start()
            
        except Exception as ex:
            error_text.value = f"Erro ao abrir Google: {ex}"
            error_text.update()

    # --- LAYOUT FINAL ---
    return ft.View(
        route="/login", 
        padding=0, 
        bgcolor="white",
        controls=[
            ft.Column(
                spacing=0, 
                controls=[
                    # PARTE SUPERIOR (Degradê)
                    ft.Container(
                        width=float("inf"), 
                        padding=ft.padding.only(left=30, right=30, top=50, bottom=30),
                        border_radius=ft.border_radius.only(bottom_left=50, bottom_right=50),
                        gradient=ft.LinearGradient(
                            colors=["#4DD0E1", "#69F0AE"], 
                            begin=ft.alignment.top_center, 
                            end=ft.alignment.bottom_center
                        ),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            spacing=15, 
                            controls=[
                                ft.Image(
                                    src="/logo-sem-fundo.png", 
                                    width=160, 
                                    height=160, 
                                    error_content=ft.Icon(ft.Icons.BUG_REPORT, size=80, color="#1B5E20")
                                ),
                                ft.Text("VigiAA", size=28, weight="bold", color="black"),
                                ft.Text("Entre na sua conta", size=16, weight="bold", color="black"),
                                
                                ft.Container(height=5),
                                
                                # CAMPOS (Dentro de containers para garantir largura total)
                                ft.Container(content=email_field, width=float("inf")),
                                ft.Container(content=password_field, width=float("inf")),
                                
                                error_text,
                                
                                ft.Container(
                                    width=float("inf"), 
                                    height=50, 
                                    content=ft.ElevatedButton(
                                        "Continue", 
                                        on_click=login_click, 
                                        bgcolor="black", 
                                        color="white", 
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                                    )
                                ),
                            ]
                        )
                    ),
                    
                    # PARTE INFERIOR (Branca)
                    ft.Container(
                        padding=20, 
                        bgcolor="white",
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                            spacing=5, 
                            controls=[
                                ft.Container(height=5),
                                ft.TextButton(
                                    "Esqueci minha senha", 
                                    style=ft.ButtonStyle(color="#1976D2"), 
                                    on_click=lambda e: page.go("/forgot-password")
                                ),
                                ft.Text("ou", color="grey", size=12),
                                
                                # Botão Google
                                ft.Container(
                                    width=float("inf"), 
                                    height=50, 
                                    content=ft.ElevatedButton(
                                        on_click=login_google, 
                                        bgcolor="#F5F5F5", 
                                        color="black", 
                                        elevation=0, 
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10), 
                                            padding=ft.padding.symmetric(horizontal=10)
                                        ), 
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER, 
                                            controls=[
                                                ft.Image(
                                                    src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg", 
                                                    width=24, 
                                                    height=24, 
                                                    error_content=ft.Icon(ft.Icons.G_TRANSLATE, color="grey")
                                                ), 
                                                ft.Text("Continue com Google")
                                            ]
                                        )
                                    )
                                ),
                                
                                ft.Container(height=10),
                                ft.Text(
                                    "Ao clicar em continuar, você aceita nossos\nTermos de Serviço e Política de Privacidade", 
                                    size=10, 
                                    color="grey", 
                                    text_align=ft.TextAlign.CENTER
                                ),
                                
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER, 
                                    controls=[
                                        ft.Text("Não possui uma conta?", color="grey", size=12), 
                                        ft.TextButton(
                                            "Crie sua conta aqui", 
                                            on_click=go_register, 
                                            style=ft.ButtonStyle(color="#1976D2")
                                        )
                                    ]
                                ),
                            ]
                        )
                    )
                ]
            )
        ]
    )