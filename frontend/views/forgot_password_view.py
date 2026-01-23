import flet as ft
import requests
import config

def create_forgot_password_view(page: ft.Page):
    API_URL = config.API_URL
    HEADERS = {"ngrok-skip-browser-warning": "true"}
    
    email_field = ft.TextField(
        label="Digite seu email cadastrado", 
        width=300, 
        bgcolor="white", 
        color="black",
        border_radius=10
    )
    msg_text = ft.Text(size=14, text_align=ft.TextAlign.CENTER)

    def go_back(e):
        page.go("/login")

    def send_reset_click(e):
        if not email_field.value:
            msg_text.value = "Por favor, digite o email."
            msg_text.color = "red"
            msg_text.update()
            return

        msg_text.value = "Conectando ao servidor..."
        msg_text.color = "blue"
        msg_text.update()

        try:
            # CORREÇÃO AQUI: Trocamos _ por - e adicionamos 'request'
            # De acordo com o seu log: api/password-reset-request/
            response = requests.post(
                f"{API_URL}/api/password-reset-request/", 
                data={"email": email_field.value},
                headers=HEADERS
            )
            
            if response.status_code in [200, 204]:
                msg_text.value = "Verifique seu e-mail! Enviamos um link."
                msg_text.color = "green"
            else:
                msg_text.value = f"Erro: {response.text}"
                msg_text.color = "red"
                
            msg_text.update()
            
        except Exception as ex:
            msg_text.value = f"Erro de conexão: {ex}"
            msg_text.color = "red"
            msg_text.update()

    # --- HEADER MANUAL ---
    header = ft.Container(
        height=60,
        bgcolor="#39BFEF",
        padding=ft.padding.symmetric(horizontal=10),
        content=ft.Row(
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back, icon_color="white"),
                ft.Text("Recuperar Senha", color="white", size=20, weight="bold")
            ]
        )
    )

    return ft.View(
        route="/forgot-password",
        bgcolor="white",
        padding=0,
        controls=[
            ft.Column(
                controls=[
                    header,
                    ft.Container(
                        padding=20,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=20),
                                ft.Icon(ft.Icons.LOCK_RESET, size=80, color="#39BFEF"),
                                ft.Container(height=20),
                                ft.Text("Esqueceu sua senha?", size=20, weight="bold", color="black"),
                                ft.Text("Digite seu email para receber o link.", color="grey"),
                                ft.Container(height=30),
                                email_field,
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "Enviar Link", 
                                    on_click=send_reset_click, 
                                    bgcolor="#39BFEF", 
                                    color="white", 
                                    width=200,
                                    height=45
                                ),
                                ft.Container(height=10),
                                msg_text
                            ]
                        )
                    )
                ]
            )
        ]
    )