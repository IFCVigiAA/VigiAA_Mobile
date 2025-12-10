import flet as ft
import config 

def logout(page: ft.Page):
    page.client_storage.remove("token")
    page.go("/login")

def create_main_view(page: ft.Page):
    ICONS = config.ICONS
    map_url = "http://192.168.70.63:5173/mapa_leaflet/map_src/index.html"
    
    view_map = ft.Container(
        content=ft.WebView(
            url=map_url, 
            expand=True,
            on_page_started=lambda _: print("Carregando mapa..."),
            on_web_resource_error=lambda e: print(f"Erro no mapa: {e.description}")
        ),
        expand=True,
        padding=0
    )

    # Aba 1: Ajustes
    view_settings = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.icons.SETTINGS, size=50, color="grey"),
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

    # Função para trocar de aba
    def change_tab(e):
        # O índice da aba clicada define qual container aparece
        index = e.control.selected_index
        body_component.content = my_tabs[index]
        body_component.update()

    # Componente que segura o conteúdo atual (começa com o mapa)
    body_component = ft.Container(content=view_map, expand=True)

    return ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("Mapa Web VigiAA"), bgcolor="blue", color="white"),
            
            # Corpo Principal (Muda dinamicamente)
            body_component,

            # Barra de Navegação no Rodapé
            ft.NavigationBar(
                selected_index=0,
                on_change=change_tab,
                destinations=[
                    ft.NavigationDestination(icon=ft.icons.MAP, label="Mapa"),
                    ft.NavigationDestination(icon=ft.icons.SETTINGS, label="Ajustes"),
                    ft.NavigationDestination(icon=ICONS.PERSON, label="Perfil"),
                ]
            )
        ],
        padding=0
    )