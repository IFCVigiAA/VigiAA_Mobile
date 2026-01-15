import flet as ft
import requests
import config

def create_login_view(page: ft.Page):
    API_URL = config.API_URL

    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(color="red", size=14)

    def login_click(e):
        if not email_field.value or not password_field.value:
            error_text.value = "Preencha todos os campos"
            error_text.update()
            return

        error_text.value = ""
        error_text.update()

        try:
            response = requests.post(f"{API_URL}/api/token/", data={
                "username": email_field.value, # Django usa 'username', mas seu app manda o email aqui
                "password": password_field.value
            })

            if response.status_code == 200:
                data = response.json()
                token = data.get("access")
                
                if token:
                    # 1. Salva o token
                    page.client_storage.set("token", token)
                    
                    # 2. Feedback visual
                    page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()

                    # 3. Força a navegação
                    print("Token salvo. Redirecionando para Home...")
                    page.go("/")
                else:
                    error_text.value = "Erro: Token não recebido do servidor."
                    error_text.update()
            else:
                error_text.value = "Email ou senha incorretos."
                error_text.update()
        
        except Exception as ex:
            error_text.value = f"Erro de conexão: {ex}"
            error_text.update()

    def go_register(e):
        page.go("/register")
    
    # URL para login com Google (abre no navegador do celular)
    def login_google(e):
        # Redireciona para o endpoint do Django que inicia o fluxo do Google
        page.launch_url(f"{API_URL}/api/start-login/")

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Image(src="logo-sem-fundo.png", width=100, height=100), # Se tiver logo
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