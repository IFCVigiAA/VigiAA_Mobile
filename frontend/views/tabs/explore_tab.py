import flet as ft

def get_explore_tab(page):
    # --- Texto e Lógica do "Ler Mais" ---
    long_text = """A dengue é uma arbovirose causada por vírus transmitidos principalmente pelo mosquito Aedes aegypti.
Os principais sintomas são febre alta, erupções cutâneas e dores musculares e articulares. Em casos graves, pode haver hemorragia profusa e choque, podendo ser fatal. O tratamento inclui ingestão de líquidos e analgésicos."""

    txt_description = ft.Text(
        long_text,
        size=15,
        color="#37474F", # Cor mais escura para leitura
        max_lines=3,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    # Botão estilo "link"
    btn_read_more = ft.TextButton(
        "ler mais...",
        style=ft.ButtonStyle(
            color="#0077B6", # Azul link
            padding=0, # Sem padding para parecer texto corrido
            overlay_color="transparent" # Sem efeito de clique cinza
        )
    )

    def toggle_read_more(e):
        if txt_description.max_lines == 3:
            txt_description.max_lines = None
            btn_read_more.text = "ler menos"
        else:
            txt_description.max_lines = 3
            btn_read_more.text = "ler mais..."
        if page: page.update()

    btn_read_more.on_click = toggle_read_more

    # --- Função dos Botões da Lista ---
    def create_info_item(image_name, text, route_name):
        return ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(vertical=15),
                    on_click=lambda _: page.go(route_name),
                    ink=True,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=20,
                                controls=[
                                    # Imagem redonda
                                    ft.Container(
                                        width=60, height=60,
                                        border_radius=30,
                                        content=ft.Image(src=f"/images/{image_name}", fit=ft.ImageFit.COVER),
                                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                        shadow=ft.BoxShadow(blur_radius=5, color="#1A000000")
                                    ),
                                    # Texto
                                    ft.Text(text, weight="w600", size=16, color="black")
                                ]
                            ),
                            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=18, color="grey")
                        ]
                    )
                ),
                ft.Divider(height=1, color="#EEEEEE") # Divisor dentro do item
            ]
        )

    # --- MONTAGEM DA TELA (Alinhada e Centralizada) ---
    
    # 1. Banner do Topo
    banner = ft.Container(
        border_radius=15,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        # Use uma imagem de banner real aqui. Se não tiver, use um placeholder.
        content=ft.Image(
            src="/images/banner1.jpeg", # Nome sugestivo para o banner da imagem
            fit=ft.ImageFit.COVER, 
            height=180, 
            width=float("inf"),
            error_content=ft.Container(bgcolor="#CFD8DC", alignment=ft.alignment.center, content=ft.Text("Banner", color="white"))
        ),
        shadow=ft.BoxShadow(blur_radius=10, color="#1A000000")
    )

    # 2. Caixa de Texto Azul
    blue_info_box = ft.Container(
        bgcolor="#E0F7FA", # Cor azul claro da imagem
        border_radius=15,
        padding=20,
        content=ft.Column(
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                txt_description,
                # Container para alinhar o botão "ler mais" à esquerda
                ft.Container(
                    alignment=ft.alignment.center_left,
                    content=btn_read_more
                )
            ]
        )
    )

    # 3. Conteúdo Principal (Coluna)
    main_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=25, # Espaço entre os blocos principais
        controls=[
            banner,
            blue_info_box,
            # Lista de Itens
            ft.Column(
                spacing=0,
                controls=[
                    create_info_item("termometro.jpg", "Sintomas", "/sintomas"),
                    create_info_item("mosquito_proibido.png", "Conheça as formas de prevenção", "/prevencao"),
                    create_info_item("agentes.jpeg", "Campanhas", "/campanhas"),
                ]
            ),
            ft.Container(height=30) # Espaço final
        ]
    )

    # 4. Container Mestre (Centraliza e dá Padding na tela toda)
    return ft.Container(
        expand=True,
        padding=20, # Padding geral da tela
        alignment=ft.alignment.top_center, # Centraliza tudo horizontalmente
        content=main_column
    )