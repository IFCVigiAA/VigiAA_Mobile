import flet as ft
import config 

def logout(page: ft.Page):
    page.client_storage.remove("token")
    page.go("/login")

def create_main_view(page: ft.Page):
    ICONS = config.ICONS
    
    # --- Aba 1: Início ---
    view_home = ft.Container(
        content=ft.Column(
            [
                ft.Text("Bem-vindo!", size=24),
                ft.Text("Você está conectado ao sistema."),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=20
    )

    # --- Aba 2: Ajustes ---
    view_settings = ft.Container(
        content=ft.Column(
            [
                ft.Text("Ajustes", size=24),
                ft.Switch(label="Modo Noturno", value=False),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=20
    )

    # --- Aba 3: Perfil ---
    view_profile = ft.Container(
        content=ft.Column(
            [
                ft.Text("Perfil", size=24),
                ft.CircleAvatar(content=ft.Icon(ICONS.PERSON), radius=40),
                ft.ElevatedButton(
                    "Sair (Logout)",
                    icon=ICONS.LOGOUT,
                    on_click=lambda _: logout(page) 
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=20
    )

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("VigiAA"), center_title=True),
            ft.Tabs(
                selected_index=0,
                expand=1,
                tabs=[
                    ft.Tab(text="Início", icon=ICONS.HOME, content=view_home),
                    ft.Tab(text="Ajustes", icon=ICONS.SETTINGS, content=view_settings),
                    ft.Tab(text="Perfil", icon=ICONS.PERSON, content=view_profile),
                ],
            ),
        ]
    )