import flet as ft
import requests
import config

def create_change_password_view(page: ft.Page):
    API_URL = config.API_URL
    
    old_pass = ft.TextField(label="Senha Atual", password=True, can_reveal_password=True, width=300, bgcolor="white", color="black", border_radius=10)
    new_pass = ft.TextField(label="Nova Senha", password=True, can_reveal_password=True, width=300, bgcolor="white", color="black", border_radius=10)
    status_text = ft.Text(size=14, text_align=ft.TextAlign.CENTER)

    def go_home(e):
        page.go("/")

    def change_click(e):
        token = page.client_storage.get("token")
        if not token:
            page.go("/login")
            return
            
        if not old_pass.value or not new_pass.value:
            status_text.value = "Preencha os dois campos."
            status_text.color = "red"
            status_text.update()
            return

        status_text.value = "Processando..."
        status_text.color = "blue"
        status_text.update()

        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "ngrok-skip-browser-warning": "true"
            }
            
            # --- MUDANÇA CRUCIAL AQUI ---
            # Trocamos requests.post por requests.put
            # APIs de atualização costumam exigir PUT
            response = requests.put(
                f"{API_URL}/api/change-password/", 
                data={
                    "old_password": old_pass.value, 
                    "new_password": new_pass.value
                },
                headers=headers
            )
            
            # Se der erro 405 de novo com PUT, tente requests.patch (mas PUT é o mais provável)
            
            if response.status_code in [200, 204]:
                status_text.value = "Senha alterada com sucesso!"
                status_text.color = "green"
                old_pass.value = ""
                new_pass.value = ""
                old_pass.update()
                new_pass.update()
            elif response.status_code == 400:
                msg = response.text
                if "old_password" in msg:
                    msg = "Senha atual incorreta."
                elif "new_password" in msg:
                    msg = "Senha nova inválida."
                status_text.value = f"Erro: {msg}"
                status_text.color = "red"
            elif response.status_code == 401:
                page.go("/login")
            else:
                status_text.value = f"Erro {response.status_code}: {response.text}"
                status_text.color = "red"
            
            status_text.update()
            
        except Exception as ex:
            status_text.value = f"Erro de conexão: {ex}"
            status_text.color = "red"
            status_text.update()

    # --- HEADER MANUAL ---
    header = ft.Container(
        height=60,
        bgcolor="#39BFEF",
        padding=ft.padding.symmetric(horizontal=10),
        content=ft.Row(
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_home, icon_color="white"),
                ft.Text("Alterar Senha", color="white", size=20, weight="bold")
            ]
        )
    )

    return ft.View(
        route="/change-password",
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
                                ft.Text("Segurança", size=20, weight="bold", color="black"),
                                ft.Text("Defina sua nova senha de acesso.", color="grey"),
                                ft.Container(height=30),
                                old_pass,
                                ft.Container(height=10),
                                new_pass,
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "Salvar Nova Senha", 
                                    on_click=change_click, 
                                    bgcolor="#4CAF50", 
                                    color="white", 
                                    width=200,
                                    height=45
                                ),
                                ft.Container(height=10),
                                status_text
                            ]
                        )
                    )
                ]
            )
        ]
    )