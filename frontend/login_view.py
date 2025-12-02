import flet as ft
import requests
import config 

def create_login_view(page: ft.Page):
    
    username_field = ft.TextField(label="Usuário", width=300, autocorrect=False, enable_suggestions=False)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    
    # CORREÇÃO: Usando string "red" para compatibilidade total
    error_text = ft.Text(color="red")
    
    # --- Lógica do Login com Google (QUE ESTAVA FALTANDO) ---
    def google_login_clicked(e):
        # USAMOS LOCALHOST! Graças ao 'adb reverse', o emulador entende isso.
        google_url = "http://localhost:8000/accounts/google/login/"
        page.launch_url(google_url)

    # --- Lógica do Login Normal ---
    def login_clicked(e):
        e.control.disabled = True
        e.control.text = "Entrando..."
        page.update()

        username = username_field.value
        password = password_field.value

        if not username or not password:
            error_text.value = "Usuário e senha obrigatórios."
            e.control.disabled = False
            e.control.text = "Entrar"
            page.update()
            return

        try:
            response = requests.post(
                f"{config.API_URL}/token/", 
                data={"username": username, "password": password},
                timeout=15
            )
            
            if response.status_code == 200:
                token = response.json().get("access")
                page.client_storage.set("token", token)
                page.go("/") 
            else:
                error_text.value = "Usuário ou senha inválidos."
                e.control.disabled = False
                e.control.text = "Entrar"
                page.update()
                
        except requests.exceptions.ConnectionError:
            error_text.value = f"Erro de conexão. O Django está rodando?"
            e.control.disabled = False
            e.control.text = "Entrar"
            page.update()
        except Exception as ex:
            error_text.value = f"Erro: {ex}"
            e.control.disabled = False
            e.control.text = "Entrar"
            page.update()

    login_button = ft.ElevatedButton("Entrar", on_click=login_clicked, width=300)
    
    # --- Botão do Google ---
    google_button = ft.ElevatedButton(
        text="Entrar com Google",
        icon=config.ICONS.G_MOBILEDATA, # Usa o ícone do config
        width=300,
        color="black",
        bgcolor="white",
        on_click=google_login_clicked # Chama a função que estava faltando
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Login VigiAA", size=32, weight=ft.FontWeight.BOLD),
                        username_field,
                        password_field,
                        
                        ft.Container(height=10),
                        login_button,
                        
                        ft.Text("ou", size=12),
                        
                        google_button, # Adiciona o botão na tela
                        
                        error_text,
                        
                        ft.Container(height=10),
                        ft.TextButton(
                            "Não tem uma conta? Registre-se",
                            on_click=lambda _: page.go("/register")
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ),
                alignment=ft.alignment.center, expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )