import flet as ft
# Imports das 4 abas oficiais
from views.tabs.home_tab import get_home_tab
from views.tabs.new_tab import get_new_tab
from views.tabs.explore_tab import get_explore_tab
from views.tabs.profile_tab import get_profile_tab 

def create_main_view(page: ft.Page, aba_inicial=0):
    
    # Lista de Módulos (Conteúdo das abas)
    # A ORDEM DEVE SER IDÊNTICA À DO MAIN.PY
    # 0: Home, 1: Novo, 2: Explorar, 3: Perfil
    modulos = [
        get_home_tab(page),      # Índice 0
        get_new_tab(page),       # Índice 1
        get_explore_tab(page),   # Índice 2
        get_profile_tab(page)    # Índice 3
    ]

    # Proteção: Se o código pedir uma aba que não existe (ex: 4), joga para Home (0)
    if aba_inicial >= len(modulos):
        print(f"AVISO: Aba {aba_inicial} inválida. Redirecionando para Home.")
        aba_inicial = 0

    # Header
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

    # View Principal
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
                        content=modulos[aba_inicial], # Carrega a aba correta (0 a 3)
                        expand=True
                    )
                ]
            )
        ]
    )