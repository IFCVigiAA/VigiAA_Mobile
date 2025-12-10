import flet as ft
import config 

def logout(page: ft.Page):
    page.client_storage.remove("token")
    page.go("/login")

def create_main_view(page: ft.Page):
    ICONS = config.ICONS
    # Link do mapa 
    map_url = "http://192.168.70.63:5173/mapa_leaflet/map_src/index.html"
    
    # --- Conteúdo das Abas ---

    # Aba 0: O Mapa
    view_map = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.MAP, size=80, color="blue"),
                ft.Text("Mapa de Monitoramento", size=20, weight="bold"),
                ft.Text("Clique abaixo para abrir o mapa em tela cheia", color="grey"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Abrir Mapa no Navegador",
                    icon=ft.Icons.OPEN_IN_BROWSER,
                    style=ft.ButtonStyle(
                        bgcolor="blue",
                        color="white",
                        padding=20
                    ),
                    on_click=lambda _: page.launch_url(map_url)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # Aba 1: Ajustes
    view_settings = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SETTINGS, size=50, color="grey"),
                ft.Text("Ajustes", size=24),
                ft.Switch(label="Modo Noturno", value=False),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # Aba 2: Perfil
    view_profile = ft.Container(
        content=ft.Column(
            [
                ft.Text("Perfil", size=24),
                ft.CircleAvatar(content=ft.Icon(ICONS.PERSON), radius=40),
                ft.Text("Usuário Logado", weight="bold"),
                ft.Divider(),
                ft.ElevatedButton(
                    "Sair (Logout)",
                    icon=ICONS.LOGOUT,
                    color="white",
                    bgcolor="red",
                    on_click=lambda _: logout(page) 
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    # Lista com as 3 telas
    my_tabs = [view_map, view_settings, view_profile]

    def change_tab(e):
        index = e.control.selected_index
        body_component.content = my_tabs[index]
        body_component.update()

    body_component = ft.Container(content=view_map, expand=True)

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("VigiAA Mobile"), bgcolor="blue", color="white"),
            body_component,
            ft.NavigationBar(
                selected_index=0,
                on_change=change_tab,
                destinations=[
                    # --- AQUI ESTAVA O ERRO, TROCAMOS O NOME ---
                    ft.NavigationBarDestination(icon=ft.Icons.MAP, label="Mapa"),
                    ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
                    ft.NavigationBarDestination(icon=ICONS.PERSON, label="Perfil"),
                ]
            )
        ],
        padding=0
    )