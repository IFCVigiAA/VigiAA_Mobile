import flet as ft
import requests
import config

def create_login_view(page: ft.Page):
    API_URL = config.API_URL
    
    HEADERS = {"ngrok-skip-browser-warning": "true"}

    # --- ELEMENTOS VISUAIS ---
    error_text = ft.Text(color="red", size=14, weight="bold", text_align=ft.TextAlign.CENTER)

    # Campos de Texto
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

    # --- LÓGICA DE LOGIN ---
    def login_click(e):
        if not email_field.value or not password_field.value:
            error_text.value = "Preencha todos os campos"
            error_text.update()
            return

        error_text.value = "Conectando..."
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
                
                if token:
                    page.client_storage.set("token", token)
                    page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                    print("Token salvo. Redirecionando...")
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
        page.launch_url(f"{API_URL}/api/start-login/?ngrok-skip-browser-warning=true")

    # --- LAYOUT FINAL ---
    return ft.View(
        route="/login",
        padding=0,
        bgcolor="white",
        controls=[
            ft.Column(
                spacing=0,
                controls=[
                    # --- PARTE SUPERIOR COLORIDA ---
                    ft.Container(
                        width=float("inf"),
                        # Aumentei o padding do topo e baixo para caber a logo grande
                        padding=ft.padding.only(left=30, right=30, top=50, bottom=30),
                        border_radius=ft.border_radius.only(bottom_left=50, bottom_right=50),
                        gradient=ft.LinearGradient(
                            colors=["#4DD0E1", "#69F0AE"], 
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                        ),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                # --- ALTERAÇÃO 1: LOGO BASTANTE AUMENTADA ---
                                ft.Image(
                                    src="/logo-sem-fundo.png", 
                                    width=160, # Aumentado de 90 para 160
                                    height=160, 
                                    error_content=ft.Icon(ft.Icons.BUG_REPORT, size=80, color="#1B5E20")
                                ),
                                
                                ft.Text("VigiAA", size=28, weight="bold", color="black"),
                                ft.Text("Entre na sua conta", size=16, weight="bold", color="black"),
                                
                                ft.Container(height=5),
                                
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
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10)
                                        )
                                    )
                                ),
                            ]
                        )
                    ),

                    # --- PARTE INFERIOR BRANCA (ITENS MAIS PRÓXIMOS) ---
                    ft.Container(
                        padding=20,
                        bgcolor="white",
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5, # --- ALTERAÇÃO 2: Espaçamento geral reduzido de 10 para 5
                            controls=[
                                ft.Container(height=5), # Reduzido de 10 para 5
                                
                                ft.TextButton(
                                    "Esqueci minha senha", 
                                    style=ft.ButtonStyle(color="#1976D2"),
                                    on_click=lambda e: page.go("/forgot-password") # <--- O PULO DO GATO ESTÁ AQUI
                                ),
                                
                                ft.Text("ou", color="grey", size=12),
                                
                                # --- ALTERAÇÃO 3: BOTÃO GOOGLE COM "G" COLORIDO ---
                                ft.Container(
                                    width=float("inf"),
                                    height=50,
                                    # Botão personalizado para incluir imagem e texto
                                    content=ft.ElevatedButton(
                                        on_click=login_google,
                                        bgcolor="#F5F5F5",
                                        color="black",
                                        elevation=0,
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=ft.padding.symmetric(horizontal=10) # Ajuste fino
                                        ),
                                        # Conteúdo personalizado: Imagem G + Texto
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                # Usa um link oficial do G do Google (SVG para alta qualidade)
                                                ft.Image(
                                                    src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg",
                                                    width=24,
                                                    height=24,
                                                    # Se falhar (sem net), mostra um ícone de fallback
                                                    error_content=ft.Icon(ft.Icons.G_TRANSLATE, color="grey")
                                                ),
                                                ft.Text("Continue com Google")
                                            ]
                                        )
                                    )
                                ),
                                
                                ft.Container(height=10), # Reduzido de 20 para 10
                                
                                ft.Text(
                                    "Ao clicar em Continuar com Google, você aceita nossos\nTermos de Serviço e Política de Privacidade", 
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