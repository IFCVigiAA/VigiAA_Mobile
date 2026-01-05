import flet as ft

def get_home_tab(page: ft.Page = None):

    # Lista para guardar as referências dos botões
    year_buttons_refs = []

    # --- Lógica de Troca de Ano ---
    def toggle_year(e):
        clicked_year = e.control.data
        print(f"Ano selecionado: {clicked_year}") 
        
        for btn in year_buttons_refs:
            if btn.data == clicked_year:
                btn.bgcolor = "black"
                btn.content.color = "white"
                btn.shadow = None
            else:
                btn.bgcolor = "white"
                btn.content.color = "black"
                btn.shadow = ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.1, "black"))
            
            btn.update()

    # --- Fábrica de Botões ---
    def create_year_button(year, is_selected=False):
        btn = ft.Container(
            content=ft.Text(year, color="white" if is_selected else "black", weight="bold"),
            bgcolor="black" if is_selected else "white",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=20,
            data=year,
            on_click=toggle_year,
            
            # --- CORREÇÃO AQUI: ft.Animation direto ---
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT), 
            
            shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.1, "black")) if not is_selected else None
        )
        year_buttons_refs.append(btn)
        return btn

    # Linha dos Anos
    year_filter = ft.Row(
        controls=[
            create_year_button("2025", is_selected=True),
            create_year_button("2024"),
            create_year_button("2023"),
        ],
        spacing=10
    )

    # --- Cards de Estatística ---
    def stat_card(title, value, subtext):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, weight="bold", color="black"),
                    ft.Text(value, size=32, weight="bold", color="black"),
                    ft.Text(subtext, size=12, color="grey"),
                ],
                spacing=5
            ),
            bgcolor="white",
            padding=20,
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black"))
        )

    stats_row = ft.Row(
        controls=[
            stat_card("Casos confirmados", "457", "+20 casos no último mês"),
            stat_card("Suspeitas de dengue", "2,405", "+300 casos no último mês"),
        ],
        spacing=15
    )

    # --- Cards de Gráfico ---
    def chart_card(title, img_src):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=16, weight="bold", color="black"),
                    ft.Container(height=10),
                    
                    ft.Container(
                        content=ft.Image(
                            src=img_src,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        height=200, 
                        alignment=ft.alignment.center,
                        bgcolor="white",
                        border_radius=10
                    )
                ]
            ),
            bgcolor="white",
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
            margin=ft.margin.only(bottom=10)
        )

    # Montagem Final
    content = ft.Container(
        content=ft.Column(
            controls=[
                year_filter,
                ft.Container(height=10),
                stats_row,
                ft.Container(height=10),
                chart_card("Casos confirmados por mês", "grafico1.png"),
                chart_card("Proporção de focos por tipo de atividade", "grafico2.png"),
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15
        ),
        padding=20,
        alignment=ft.alignment.top_center,
        expand=True
    )

    return content