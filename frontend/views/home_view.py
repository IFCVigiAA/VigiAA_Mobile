import flet as ft
# Imports das abas
from views.tabs.home_tab import get_home_tab
from views.tabs.new_tab import get_new_tab
from views.tabs.explore_tab import get_explore_tab
from views.tabs.profile_tab import get_profile_tab

def create_main_view(page: ft.Page, aba_inicial=0):
    
    # 1. Carrega as abas
    view_home = get_home_tab(page)
    view_add = get_new_tab(page) # Essa é a tela com os cards de seleção
    view_explore = get_explore_tab()
    view_profile = get_profile_tab(page)

    modulos = [view_home, view_add, view_explore, view_profile]

    # 2. Corpo da página
    body = ft.Container(
        content=modulos[aba_inicial],
        expand=True
    )

    # 3. Função de troca de aba
    def change_tab(e):
        index = e.control.selected_index
        
        # --- CORREÇÃO AQUI: Removemos o desvio direto para o formulário ---
        # Agora ele carrega a aba correspondente (a view_add) normalmente
        
        body.content = modulos[index]
        body.update()

    # 4. Barra de Navegação
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE, label="Novo"),
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explorar"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Perfil"),
        ],
        selected_index=aba_inicial,
        on_change=change_tab,
        bgcolor="#39BFEF", # Azul Ciano
    )

    # 5. Cabeçalho Personalizado (VigiAA)
    header = ft.Container(
        height=60,
        padding=ft.padding.symmetric(horizontal=15),
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=["#39BFEF", "#69F0AE"] 
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Logo com barra / para funcionar no Android
                ft.Container(
                    content=ft.Image(
                        src="/logo-sem-fundo.png", 
                        width=40, 
                        height=40, 
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color="white")
                    ),
                    alignment=ft.alignment.center
                ),
                
                ft.Text("VigiAA", size=22, weight="bold", color="black"),
                
                ft.IconButton(ft.Icons.NOTIFICATIONS_NONE, icon_color="black")
            ]
        )
    )

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                controls=[
                    header,
                    body,
                    nav_bar
                ],
                spacing=0,
                expand=True
            )
        ],
        padding=0,
        bgcolor="#F5F5F5"
    )