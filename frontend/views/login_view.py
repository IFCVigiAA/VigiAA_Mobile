import flet as ft
import requests
import config
import threading
import time
import uuid

API_URL = config.API_URL

def create_login_view(page: ft.Page):
    
    # --- 1. Estilos e Campos ---
    def input_style(label, is_password=False, reveal=False):
        return ft.TextField(
            hint_text=label,
            password=is_password,
            can_reveal_password=reveal,
            bgcolor="white",
            width=320,
            border_radius=10,
            border_color="transparent",
            text_style=ft.TextStyle(color="black", size=14),
            hint_style=ft.TextStyle(color="grey"),
            content_padding=15,
            height=50,
            cursor_color="black"
        )

    username_field = input_style("email@domain.com")
    password_field = input_style("senha", is_password=True, reveal=True)
    status_text = ft.Text(value="", color="white", size=12, text_align="center")

    # --- 2. Lógica: Login Normal ---
    def login_clicked(e):
        if not username_field.value or not password_field.value:
            status_text.value = "Preencha todos os campos"
            status_text.color = "#ffcccc"
            status_text.update()
            return

        status_text.value = "Entrando..."
        status_text.color = "white"
        status_text.update()

        try:
            res = requests.post(
                f"{API_URL}/api/token/", 
                data={"username": username_field.value, "password": password_field.value}
            )
            
            if res.status_code == 200:
                page.client_storage.set("token", res.json().get("access"))
                page.go("/")
            else:
                status_text.value = "Usuário ou senha incorretos."
                status_text.color = "#ffcccc"
                status_text.update()
        except Exception as ex:
            status_text.value = "Erro de conexão."
            print(ex)
            status_text.update()

    # --- 3. Lógica: Recuperar Senha (Timer + Feedback) ---
    forgot_email_field = ft.TextField(label="Seu Email Cadastrado", width=300)
    send_link_btn = ft.ElevatedButton("Enviar Link")

    def timer_countdown():
        for i in range(30, 0, -1):
            send_link_btn.text = f"Aguarde {i}s..."
            send_link_btn.disabled = True
            send_link_btn.update()
            time.sleep(1)
        
        send_link_btn.text = "Enviar Código Novamente"
        send_link_btn.disabled = False
        send_link_btn.update()

    def send_reset_email(e):
        if not forgot_email_field.value:
            forgot_email_field.error_text = "Digite seu email"
            forgot_email_field.update()
            return
            
        try:
            requests.post(f"{API_URL}/api/password-reset-request/", json={'email': forgot_email_field.value})
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Sucesso! Verifique seu email."),
                bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()

            t = threading.Thread(target=timer_countdown, daemon=True)
            t.start()

        except Exception as ex:
            print(ex)
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao conectar no servidor."))
            page.snack_bar.open = True
            page.update()

    send_link_btn.on_click = send_reset_email

    forgot_dialog = ft.AlertDialog(
        title=ft.Text("Recuperar Senha"),
        content=ft.Column([
            ft.Text("Digite seu email. Enviaremos um link para criar nova senha."),
            forgot_email_field
        ], height=120, tight=True),
        actions=[
            ft.TextButton("Fechar", on_click=lambda _: page.close(forgot_dialog)),
            send_link_btn
        ]
    )

    def open_forgot_password(e):
        send_link_btn.text = "Enviar Link"
        send_link_btn.disabled = False
        forgot_email_field.value = ""
        forgot_email_field.error_text = None
        page.open(forgot_dialog)

    # --- 4. Lógica: Google ---
    def check_google_status(login_id):
        for _ in range(60):
            time.sleep(2)
            try:
                res = requests.get(
                    f"{API_URL}/api/check-login/?login_id={login_id}",
                    headers={"ngrok-skip-browser-warning": "true"}
                )
                if res.status_code == 200:
                    data = res.json()
                    if data.get('status') == 'success' or data.get('access'): 
                        token = data.get('access_token') or data.get('access')
                        page.client_storage.set("token", token)
                        page.go("/")
                        page.update()
                        return
            except:
                pass

    def start_google_login(e):
        try:
            my_login_id = str(uuid.uuid4())
            target_url = f"{API_URL}/api/start-login/?login_id={my_login_id}"
            page.launch_url(target_url)
            t = threading.Thread(target=check_google_status, args=(my_login_id,), daemon=True)
            t.start()
        except Exception as ex:
            print(f"Erro: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao iniciar Google Login"))
            page.snack_bar.open = True
            page.update()

    # --- 5. Layout ---
    top_section = ft.Container(
        width=float("inf"),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#3AC0ED", "#72FC90"]
        ),
        border_radius=ft.border_radius.only(bottom_left=50, bottom_right=50),
        padding=ft.padding.only(top=50, bottom=40, left=20, right=20),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Image(
                    src="logo-sem-fundo.png",
                    width=120,
                    fit=ft.ImageFit.CONTAIN,
                ),
                
                ft.Text("VigiAA", size=28, weight="bold", color="#1a1a1a"),
                ft.Text("Entre na sua conta", size=15, weight="w500", color="#1a1a1a"),
                ft.Container(height=10),
                username_field,
                password_field,
                status_text,
                ft.ElevatedButton(
                    text="Continue",
                    color="white",
                    bgcolor="black",
                    width=320,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=login_clicked
                ),
            ]
        )
    )

    bottom_section = ft.Container(
        width=float("inf"),
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.TextButton(
                    "Esqueci minha senha", 
                    style=ft.ButtonStyle(color="#0056b3"),
                    on_click=open_forgot_password
                ),
                ft.Row(
                    controls=[
                        ft.Container(height=1, bgcolor="#dddddd", expand=True),
                        ft.Text("ou", color="#777777", size=14), 
                        ft.Container(height=1, bgcolor="#dddddd", expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=320
                ),
                
                ft.Column(
                    spacing=3, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton(
                            text="Continue com Google",
                            icon=ft.Icons.G_MOBILEDATA_SHARP, 
                            color="black",
                            bgcolor="#f0f0f0",
                            width=320,
                            height=50,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), elevation=0),
                            on_click=start_google_login
                        ),
                        ft.Text(
                            spans=[
                                ft.TextSpan("Ao clicar em Continuar com Google, você aceita nossos\n"),
                                ft.TextSpan("Termos de Serviço", ft.TextStyle(weight=ft.FontWeight.BOLD, color="black")),
                                ft.TextSpan(" e ", ft.TextStyle(color="grey")),
                                ft.TextSpan("Política de Privacidade", ft.TextStyle(weight=ft.FontWeight.BOLD, color="black")),
                            ],
                            size=11, 
                            color="grey", 
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ]
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2,
                    controls=[
                        ft.Text("Não possui uma conta?", size=13, color="#777777"),
                        ft.TextButton(
                            "Crie sua conta aqui", 
                            style=ft.ButtonStyle(color="#0056b3", padding=0), 
                            on_click=lambda _: page.go("/register")
                        )
                    ]
                )
            ]
        )
    )

    return ft.View(
        "/login",
        bgcolor="white",
        padding=0,
        controls=[
            ft.Column(
                controls=[top_section, bottom_section],
                spacing=0,
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )