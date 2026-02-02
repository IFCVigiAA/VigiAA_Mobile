import flet as ft

def get_explore_tab(page: ft.Page):
    # --- 1. BARRA DE PESQUISA ---
    search_bar = ft.Container(
        padding=ft.padding.symmetric(horizontal=5),
        content=ft.TextField(
            hint_text="Pesquisar",
            prefix_icon=ft.Icons.SEARCH,
            text_size=14,
            bgcolor="#F5F5F5",
            border_radius=30,
            border_width=0,
            content_padding=10
        )
    )

    # --- 2. BANNER PRINCIPAL ---
    pagination_dots = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5,
        controls=[
            ft.Container(width=6, height=6, border_radius=6, bgcolor="white"),
            ft.Container(width=6, height=6, border_radius=6, bgcolor="grey"),
            ft.Container(width=6, height=6, border_radius=6, bgcolor="grey"),
            ft.Container(width=6, height=6, border_radius=6, bgcolor="grey"),
            ft.Container(width=6, height=6, border_radius=6, bgcolor="grey"),
        ]
    )

    banner_card = ft.Container(
        height=180,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            controls=[
                # Imagem de fundo
                ft.Image(
                    src="assets/focos.jpg",
                    fit=ft.ImageFit.COVER,
                    width=float("inf"),
                    height=180,
                ),
                # Gradiente e Texto
                ft.Container(
                    alignment=ft.alignment.bottom_center,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.Colors.TRANSPARENT, ft.Colors.BLACK87]
                    ),
                    padding=15,
                    content=ft.Column(
                        # --- CORREÇÃO AQUI ---
                        alignment=ft.MainAxisAlignment.END,            # Era main_AxisAlignment
                        horizontal_alignment=ft.CrossAxisAlignment.START, # Era cross_AxisAlignment
                        # ---------------------
                        spacing=5,
                        controls=[
                            ft.Text("Banner estado", color="white", size=12, weight="bold"),
                            ft.Container(content=pagination_dots, alignment=ft.alignment.center)
                        ]
                    )
                )
            ]
        )
    )

    # --- 3. CARD INFORMATIVO AZUL ---
    info_card = ft.Container(
        bgcolor="#E1F5FE",
        border_radius=12,
        padding=20,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Text(
                    spans=[
                        ft.TextSpan("A dengue ", style=ft.TextStyle(weight="bold", color="black", size=14)),
                        ft.TextSpan(
                            "é uma arbovirose causada por vírus transmitidos principalmente pelo mosquito ", 
                            style=ft.TextStyle(color="black", size=14)
                        ),
                        ft.TextSpan(
                            "Aedes aegypti. ", 
                            style=ft.TextStyle(color="black", size=14, italic=True)
                        ),
                        ft.TextSpan(
                            "ler mais...", 
                            style=ft.TextStyle(color="#0288D1", weight="bold", size=14)
                        ),
                    ]
                )
            ]
        )
    )

    # --- 4. LISTA DE NAVEGAÇÃO ---
    def create_nav_item(icon_data, title, route, is_image=False):
        if is_image:
            visual_content = ft.Image(src=icon_data, width=30, height=30, fit=ft.ImageFit.CONTAIN)
        else:
            visual_content = ft.Icon(icon_data, size=24, color="#555555")

        return ft.Container(
            padding=ft.padding.symmetric(vertical=12),
            on_click=lambda _: page.go(route),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=50, height=50,
                        bgcolor="#E0E0E0",
                        border_radius=25,
                        alignment=ft.alignment.center,
                        content=visual_content
                    ),
                    ft.Container(width=10),
                    ft.Text(title, weight="bold", size=15, color="black", expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="grey")
                ]
            )
        )

    item_sintomas = create_nav_item(ft.Icons.THERMOSTAT, "Sintomas", "/sintomas") 
    item_prevencao = create_nav_item(ft.Icons.BLOCK, "Conheça as formas de prevenção", "/prevencao")

    # --- MONTAGEM FINAL ---
    return ft.ListView(
        padding=20,
        spacing=15,
        controls=[
            search_bar,
            ft.Container(height=5),
            banner_card,
            info_card,
            ft.Container(height=5),
            item_sintomas,
            item_prevencao
        ]
    )