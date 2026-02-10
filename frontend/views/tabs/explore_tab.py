import flet as ft

def get_explore_tab(page):
    # Texto longo sobre o projeto
    long_text = """O VigiAA é uma iniciativa focada na prevenção e combate ao mosquito Aedes aegypti. 
Nossa missão é utilizar a tecnologia para mapear focos, conscientizar a população e agilizar a ação dos agentes de endemias. 
Com a sua ajuda, podemos reduzir drasticamente os casos de Dengue, Zika e Chikungunya na nossa região. 
Participe ativamente reportando focos e seguindo as orientações de prevenção."""

    # Controle de texto com limite de linhas
    txt_description = ft.Text(
        long_text,
        size=14,
        color="grey",
        max_lines=3, # Começa resumido
        overflow=ft.TextOverflow.ELLIPSIS,
        text_align=ft.TextAlign.JUSTIFY
    )

    # Botão que expande o texto
    btn_read_more = ft.TextButton("Ler mais", style=ft.ButtonStyle(color="#39BFEF"))

    def toggle_read_more(e):
        if txt_description.max_lines == 3:
            txt_description.max_lines = None
            btn_read_more.text = "Ler menos"
        else:
            txt_description.max_lines = 3
            btn_read_more.text = "Ler mais"
        
        # Atualiza a página para redesenhar o texto
        if page: page.update()

    btn_read_more.on_click = toggle_read_more

    # Função para criar os botões da lista (Sintomas, Prevenção, Campanhas)
    def create_info_item(image_name, text, route_name):
        return ft.Container(
            padding=ft.padding.symmetric(vertical=10),
            on_click=lambda _: page.go(route_name),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            # Imagem redonda
                            ft.Container(
                                width=50, height=50,
                                border_radius=25,
                                content=ft.Image(src=f"/images/{image_name}", fit=ft.ImageFit.COVER),
                                clip_behavior=ft.ClipBehavior.HARD_EDGE
                            ),
                            # Texto
                            ft.Text(text, weight="bold", size=15, color="black")
                        ]
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=16, color="grey")
                ]
            )
        )

    # Retorna o conteúdo da Tab (Coluna)
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text("Sobre o Projeto", size=22, weight="bold", color="#39BFEF"),
            ft.Divider(height=20, color="transparent"),
            
            # Imagem de Capa (Opcional, se tiver)
            ft.Container(
                border_radius=15,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Image(src="/images/capa_explore.png", fit=ft.ImageFit.COVER, height=180, width=float("inf"),
                                 error_content=ft.Container(bgcolor="#EEEEEE", height=180)) 
            ),
            ft.Divider(height=10, color="transparent"),

            # Descrição e Ler Mais
            txt_description,
            ft.Row([btn_read_more], alignment=ft.MainAxisAlignment.END),
            
            ft.Divider(height=20, color="#EEEEEE"),
            
            # Lista de Botões
            ft.Text("Saiba mais", size=18, weight="bold", color="black"),
            ft.Divider(height=10, color="transparent"),
            
            create_info_item("termometro.png", "Sintomas", "/sintomas"),
            create_info_item("mosquito_proibido.png", "Conheça as formas de prevenção", "/prevencao"),
            # O NOVO BOTÃO AQUI EMBAIXO 👇
            create_info_item("agentes.jpeg", "Campanhas", "/campanhas"),
            
            ft.Divider(height=50, color="transparent"),
        ]
    )