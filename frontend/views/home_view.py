import flet as ft
from views.tabs.home_tab import get_home_tab
from views.tabs.new_tab import get_new_tab
from views.tabs.explore_tab import get_explore_tab
from views.tabs.profile_tab import get_profile_tab 

def create_main_view(page: ft.Page, aba_inicial=0):
    
    modulos = [
        get_home_tab(page),      # 0
        get_new_tab(page),       # 1
        get_explore_tab(page),   # 2
        get_profile_tab(page)    # 3
    ]

    if aba_inicial >= len(modulos):
        aba_inicial = 0

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
                ft.Container(
                    content=ft.Image(
                        src="/images/logo-sem-fundo.png", 
                        width=40, height=40, 
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color="white")
                    ),
                    alignment=ft.alignment.center
                ),
                ft.Text("VigiAA", size=22, weight="bold", color="black"),
                ft.IconButton(ft.Icons.NOTIFICATIONS_NONE, icon_color="black")
            ]
        ),
        shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
    )

    return ft.View(
        route="/", 
        padding=0,
        bgcolor="#F5F5F5",
        controls=[
            ft.Column(
                spacing=0,
                expand=True,
                controls=[
                    header,
                    ft.Container(
                        content=modulos[aba_inicial],
                        expand=True
                    )
                ]
            )
        ],
        # A MÁGICA QUE FALTAVA: Conectando a tela com a barra do main!
        navigation_bar=page.navigation_bar
    )