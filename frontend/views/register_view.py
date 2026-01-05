import flet as ft
import requests
import time
import config

def create_register_view(page: ft.Page):
    
    # --- 1. Estilização dos Campos ---
    def input_style(hint, password=False, reveal=False, keyboard=ft.KeyboardType.TEXT):
        return ft.TextField(
            hint_text=hint,
            password=password,
            can_reveal_password=reveal,
            keyboard_type=keyboard,
            bgcolor="white",
            border_color="#d9d9d9",
            border_radius=10,
            text_style=ft.TextStyle(color="black", size=14),
            hint_style=ft.TextStyle(color="grey"),
            content_padding=15,
            height=50,
            cursor_color="black",
            width=320
        )

    # --- 2. Criação dos Campos ---
    first_name_field = input_style("Nome")
    last_name_field = input_style("Sobrenome")
    username_field = input_style("Usuário")
    email_field = input_style("Email", keyboard=ft.KeyboardType.EMAIL)
    password_field = input_style("Senha", password=True, reveal=True)
    password2_field = input_style("Confirmar Senha", password=True, reveal=True)
    
    error_text = ft.Text(color="red", size=12, text_align="center")
    
    # --- 3. Lógica do Botão ---
    def register_clicked(e):
        if not username_field.value or not password_field.value:
            error_text.value = "Preencha todos os campos obrigatórios."
            error_text.update()
            return

        e.control.disabled = True
        e.control.text = "Criando..."
        e.control.update()

        try:
            response = requests.post(
                f"{config.API_URL}/api/register/",
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
                error_text.value = "Conta criada! Redirecionando..."
                error_text.color = "green"
                error_text.update()
                page.update()
                time.sleep(1.5)
                page.go("/login")
            
            else:
                try:
                    error_data = response.json()
                    msg = error_data.get("error") or str(error_data)
                    error_text.value = msg
                except:
                    error_text.value = f"Erro {response.status_code}: {response.text}"
                
                error_text.color = "red"
                e.control.disabled = False
                e.control.text = "Cadastrar"
                page.update()

        except requests.exceptions.ConnectionError:
            error_text.value = "Erro de conexão com o servidor."
            e.control.disabled = False
            e.control.text = "Cadastrar"
            page.update()
        except Exception as ex:
            error_text.value = f"Erro inesperado: {ex}"
            e.control.disabled = False
            e.control.text = "Cadastrar"
            page.update()

    # --- 4. Layout Visual (Design Ajustado) ---

    header_section = ft.Container(
        width=float("inf"),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#3AC0ED", "#72FC90"]
        ),
        border_radius=ft.border_radius.only(bottom_left=50, bottom_right=50),
        padding=ft.padding.only(top=40, bottom=30, left=20, right=20),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                # Logo MAIOR
                ft.Image(
                    src="logo-sem-fundo.png",
                    width=250,
                    fit=ft.ImageFit.CONTAIN
                ),
                
                # Texto VigiAA com MARGEM NEGATIVA para subir
                ft.Container(
                    content=ft.Text("VigiAA", size=26, weight="bold", color="#1a1a1a"),
                    # O "top=-20" puxa o texto para cima, colando na imagem
                    margin=ft.margin.only(top=-20) 
                ),
                
                ft.Container(height=5),
                ft.Text("Crie sua conta", size=16, weight="w500", color="#1a1a1a"),
            ]
        )
    )

    form_section = ft.Container(
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                first_name_field,
                last_name_field,
                username_field,
                email_field,
                password_field,
                password2_field,
                
                ft.Container(height=10),
                
                ft.ElevatedButton(
                    text="Cadastrar",
                    color="white",
                    bgcolor="black",
                    width=320,
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=0
                    ),
                    on_click=register_clicked
                ),
                
                error_text,
                
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Já possui conta?", size=13, color="#777777"),
                        ft.TextButton(
                            "Faça Login", 
                            style=ft.ButtonStyle(color="#0056b3", padding=0), 
                            on_click=lambda _: page.go("/login")
                        )
                    ]
                )
            ]
        )
    )

    return ft.View(
        "/register",
        bgcolor="white",
        padding=0,
        controls=[
            ft.Column(
                controls=[header_section, form_section],
                spacing=0,
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )