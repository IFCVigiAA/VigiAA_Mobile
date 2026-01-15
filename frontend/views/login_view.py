import flet as ft
import requests
import config

def create_login_view(page: ft.Page):
    API_URL = config.API_URL
    
    # --- CORREÇÃO 1: CABEÇALHO PARA O NGROK NÃO BLOQUEAR ---
    HEADERS = {"ngrok-skip-browser-warning": "true"}

    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(color="red", size=14)

    def login_click(e):
        if not email_field.value or not password_field.value:
            error_text.value = "Preencha todos os campos"
            error_text.update()
            return

        error_text.value = "Conectando..."
        error_text.update()

        try:
            # Adicionamos headers=HEADERS aqui para passar pelo Ngrok
            response = requests.post(
                f"{API_URL}/api/token/", 
                data={
                    "username": email_field.value, 
                    "password": password_field.value
                },
                headers=HEADERS # <--- O PULO DO GATO
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access")
                
                if token:
                    page.client_storage.set("token", token)
                    page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                    print("Token salvo. Redirecionando para Home...")
                    page.go("/")
                else:
                    error_text.value = "Erro: Token vazio."
                    error_text.update()
            
            elif response.status_code == 401:
                error_text.value = "Email ou senha incorretos."
                error_text.update()
            else:
                error_text.value = f"Erro no servidor: {response.status_code}"
                error_text.update()
        
        except Exception as ex:
            error_text.value = f"Erro de conexão: {ex}"
            error_text.update()

    def go_register(e):
        page.go("/register")
    
    def login_google(e):
        # Adiciona o parametro na URL pro navegador também tentar pular o aviso
        page.launch_url(f"{API_URL}/api/start-login/?ngrok-skip-browser-warning=true")

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        # --- CORREÇÃO 2: A BARRA "/" E O TRATAMENTO DE ERRO ---
                        ft.Image(
                            src="/logo-sem-fundo.png", # <--- OBRIGATÓRIO TER A BARRA
                            width=100, 
                            height=100,
                            # Se a imagem falhar, mostra um ícone e NÃO TRAVA O APP (Tela Branca)
                            error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=50, color="grey")
                        ), 
                        ft.Text("Bem-vindo ao VigiAA", size=24, weight="bold", color="#39BFEF"),
                        ft.Container(height=20),
                        email_field,
                        password_field,
                        error_text,
                        ft.ElevatedButton("ENTRAR", on_click=login_click, bgcolor="#39BFEF", color="white", width=300),
                        ft.Container(height=10),
                        ft.OutlinedButton("Entrar com Google", icon=ft.Icons.g_mobiledata, on_click=login_google, width=300),
                        ft.Container(height=20),
                        ft.TextButton("Não tem conta? Cadastre-se", on_click=go_register)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=20,
                bgcolor="white"
            )
        ],
        bgcolor="white",
        padding=0
    )