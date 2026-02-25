import flet as ft
from views.tabs.home_tab import get_home_tab
from views.tabs.new_tab import get_new_tab
from views.tabs.explore_tab import get_explore_tab
from views.tabs.profile_tab import get_profile_tab 

def create_main_view(page: ft.Page, aba_inicial=0):
    
    # 1. A SOLUÇÃO DO PERFIL (Lazy Loading)
    # Trocamos para as FUNÇÕES sem os parênteses. 
    # Assim elas não executam todas de uma vez, só guardamos os nomes delas!
    modulos_funcs = [
        get_home_tab,      # 0
        get_new_tab,       # 1
        get_explore_tab,   # 2
        get_profile_tab    # 3
    ]

    if aba_inicial >= len(modulos_funcs):
        aba_inicial = 0

    # Agora sim, a gente executa APENAS a tela que o usuário realmente clicou:
    aba_atual = modulos_funcs[aba_inicial](page)

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

    # 2. A SOLUÇÃO DA TELA PISCANDO (Rotas Dinâmicas)
    rotas = ["/", "/novo", "/explorar", "/perfil"]
    rota_correta = rotas[aba_inicial]

    return ft.View(
        route=rota_correta, # Agora a rota acompanha a aba certinho!
        padding=0,
        bgcolor="#F5F5F5",
        controls=[
            ft.Column(
                spacing=0,
                expand=True,
                controls=[
                    header,
                    ft.Container(
                        content=aba_atual,
                        expand=True
                    )
                ]
            )
        ],
        navigation_bar=page.navigation_bar
    )