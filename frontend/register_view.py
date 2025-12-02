import flet as ft
import requests
import time
import config

def create_register_view(page: ft.Page):
    
    # Campos de Nome e Sobrenome
    first_name_field = ft.TextField(label="Nome", width=300)
    last_name_field = ft.TextField(label="Sobrenome", width=300)
    
    username_field = ft.TextField(label="Usuário", width=300)
    email_field = ft.TextField(label="Email", width=300, keyboard_type=ft.KeyboardType.EMAIL)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    password2_field = ft.TextField(label="Confirmar Senha", password=True, can_reveal_password=True, width=300)
    
    error_text = ft.Text(color="red")
    
    def register_clicked(e):
        e.control.disabled = True
        e.control.text = "Criando..."
        page.update()

        try:
            response = requests.post(
                f"{config.API_URL}/register/",
                json={
                    "username": username_field.value,
                    "email": email_field.value,
                    "password": password_field.value,
                    "password2": password2_field.value,
                    "first_name": first_name_field.value,
                    "last_name": last_name_field.value
                },
                timeout=15
            )
            
            if response.status_code == 201:
                error_text.value = "Conta criada! Faça o login."
                error_text.color = "green"
                page.update()
                time.sleep(1.5)
                page.go("/login")
            
            else:
                error_data = response.json()
                error_text.value = error_data.get("error", "Erro desconhecido.")
                error_text.color = "red"
                e.control.disabled = False
                e.control.text = "Registrar"
                page.update()

        except requests.exceptions.ConnectionError:
            error_text.value = "Erro de conexão com o servidor."
            error_text.color = "red"
            e.control.disabled = False
            e.control.text = "Registrar"
            page.update()
        except Exception as ex:
            error_text.value = f"Erro inesperado: {ex}"
            error_text.color = "red"
            e.control.disabled = False
            e.control.text = "Registrar"
            page.update()

    return ft.View(
        route="/register",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Criar Conta", size=32, weight=ft.FontWeight.BOLD),
                        first_name_field,
                        last_name_field,
                        username_field,
                        email_field,
                        password_field,
                        password2_field,
                        ft.ElevatedButton("Registrar", on_click=register_clicked),
                        error_text,
                        ft.TextButton(
                            "Já tem uma conta? Faça o Login",
                            on_click=lambda _: page.go("/login")
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )