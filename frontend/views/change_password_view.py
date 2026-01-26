import flet as ft
import requests
import config

def create_change_password_view(page: ft.Page):
    print("--- Abrindo Tela de Alterar Senha ---")
    
    API_URL = config.API_URL
    
    # --- ESTILOS ---
    header_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=["#39BFEF", "#4ADE80"] 
    )
    
    input_style = {
        "border": ft.InputBorder.UNDERLINE,
        "border_color": "#E0E0E0",
        "focused_border_color": "#39BFEF",
        "label_style": ft.TextStyle(color="grey", size=14),
        "text_style": ft.TextStyle(color="black", size=16),
        "bgcolor": "transparent",
        "content_padding": ft.padding.only(bottom=5, top=15),
        "password": True,
        "can_reveal_password": True
    }

    # --- CAMPOS ---
    old_pass = ft.TextField(label="Senha Atual", **input_style)
    new_pass = ft.TextField(label="Nova Senha", **input_style)
    confirm_pass = ft.TextField(label="Confirmar Nova Senha", **input_style)
    
    status_text = ft.Text(size=14, text_align=ft.TextAlign.CENTER)

    # --- FUNÇÕES ---
    def go_back(e):
        # CORREÇÃO: Verificação manual da pilha de telas
        if len(page.views) > 1:
            page.views.pop() # Remove a tela atual
            top_view = page.views[-1] # Pega a tela anterior
            page.go(top_view.route) # Navega para ela
        else:
            page.go("/perfil") # Se não tiver histórico, força ir para a Home
        page.update()

    def change_click(e):
        token = page.client_storage.get("token")
        if not token: 
            page.go("/login")
            return
            
        if not old_pass.value or not new_pass.value or not confirm_pass.value:
            status_text.value = "Preencha todos os campos."
            status_text.color = "red"
            status_text.update()
            return

        if new_pass.value != confirm_pass.value:
            status_text.value = "As novas senhas não coincidem."
            status_text.color = "red"
            status_text.update()
            return

        status_text.value = "Salvando..."
        status_text.color = "blue"
        status_text.update()

        try:
            headers = {"Authorization": f"Bearer {token}", "ngrok-skip-browser-warning": "true"}
            
            response = requests.put(
                f"{API_URL}/api/change-password/", 
                data={"old_password": old_pass.value, "new_password": new_pass.value},
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                status_text.value = "Senha alterada com sucesso!"
                status_text.color = "green"
                old_pass.value = ""; new_pass.value = ""; confirm_pass.value = ""
                old_pass.update(); new_pass.update(); confirm_pass.update()
            elif response.status_code == 400:
                status_text.value = "Senha incorreta ou inválida."
                status_text.color = "red"
            elif response.status_code == 401:
                page.go("/login")
            else:
                status_text.value = f"Erro {response.status_code}"
                status_text.color = "red"
        except Exception as ex:
            status_text.value = f"Erro de conexão: {ex}"
            status_text.color = "red"
        
        status_text.update()

    # --- HEADER ---
    header = ft.Container(
        height=80,
        gradient=header_gradient,
        padding=ft.padding.symmetric(horizontal=15),
        alignment=ft.alignment.center_left,
        content=ft.Row(
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="white", on_click=go_back),
                ft.Text("Alterar senha", color="white", size=20, weight="bold")
            ]
        )
    )

    # --- BOTÃO ---
    btn_save = ft.ElevatedButton(
        "Salvar Nova Senha",
        on_click=change_click,
        bgcolor="black",
        color="white",
        width=float("inf"),
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # --- BODY ---
    body_content = ft.Column(
        controls=[
            ft.Text("Defina sua nova credencial", color="grey", size=14),
            ft.Container(height=30),
            old_pass,
            ft.Container(height=20),
            new_pass,
            ft.Container(height=20),
            confirm_pass,
            ft.Container(height=40),
            btn_save,
            ft.Container(height=20),
            status_text
        ]
    )

    body = ft.Container(
        padding=30,
        bgcolor="white",
        expand=True,
        content=ft.ListView(
            controls=[body_content],
            padding=0
        )
    )

    # --- VIEW FINAL ---
    return ft.View(
        route="/change-password",
        bgcolor="white",
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                spacing=0,
                controls=[header, body]
            )
        ]
    )