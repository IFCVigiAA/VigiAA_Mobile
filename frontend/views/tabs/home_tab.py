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
                # CORREÇÃO: Uso de hexadecimal direto para evitar erro de ft.colors
                btn.shadow = ft.BoxShadow(blur_radius=2, color="#1A000000")
            
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
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT), 
            shadow=ft.BoxShadow(blur_radius=2, color="#1A000000") if not is_selected else None
        )
        year_buttons_refs.append(btn)
        return btn

    year_filter = ft.Row(
        controls=[
            create_year_button("2025", is_selected=True),
            create_year_button("2024"),
            create_year_button("2023"),
        ],
        spacing=10,
        scroll=ft.ScrollMode.HIDDEN 
    )

    # --- Cards de Estatística ---
    def stat_card(title, value, subtext):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=13, weight="w600", color="black"), 
                    ft.Text(value, size=26, weight="bold", color="black"),
                    ft.Text(subtext, size=11, color="grey"),
                ],
                spacing=2, 
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor="white",
            padding=15, 
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color="#0D000000")
        )

    stats_row = ft.Row(
        controls=[
            stat_card("Casos confirmados", "457", "+20 este mês"), 
            stat_card("Suspeitas de dengue", "2,405", "+300 este mês"),
        ],
        spacing=10 
    )

    # --- Cards de Gráfico (COM CAMINHO ASSETS/IMAGES) ---
    def chart_card(title, img_filename):
        # MUDANÇA AQUI: Adiciona o prefixo correto /images/
        # O Flet mapeia a pasta assets para a raiz /, então assets/images vira /images/
        img_src = f"/images/{img_filename}"
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=16, weight="bold", color="black"),
                    ft.Container(height=10),
                    
                    ft.Container(
                        content=ft.Image(
                            src=img_src,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Container(bgcolor="#F0F0F0", alignment=ft.alignment.center, content=ft.Text("Imagem não encontrada", size=10, color="grey"))
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
            shadow=ft.BoxShadow(blur_radius=10, color="#0D000000"),
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
                # Passamos apenas o nome do arquivo, a função adiciona /images/
                chart_card("Casos confirmados por mês", "grafico1.png"),
                chart_card("Proporção de focos por tipo", "grafico2.png"),
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15
        ),
        padding=15, 
        alignment=ft.alignment.top_center,
        expand=True
    )

    return content