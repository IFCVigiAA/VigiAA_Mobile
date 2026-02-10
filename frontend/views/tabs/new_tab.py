import flet as ft

def get_new_tab(page: ft.Page):
    
    def go_to_form(route):
        page.go(route)

    # --- Componente: Card de Cadastro ---
    def create_action_card(title, description, img_filename, route):
        # MUDANÇA: Adiciona o prefixo /images/ automaticamente
        img_src = f"/images/{img_filename}"

        return ft.Container(
            bgcolor="white",
            border_radius=15,
            # MUDANÇA: Hexadecimal direto para evitar erro de 'ft.colors'
            shadow=ft.BoxShadow(
                blur_radius=10, 
                color="#1A000000", # Preto com 10% de opacidade
                offset=ft.Offset(0, 4)
            ),
            content=ft.Stack(
                controls=[
                    # Conteúdo do Card
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Image(
                                src=img_src,
                                height=150,
                                width=float("inf"),
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.only(top_left=15, top_right=15),
                                # Fallback caso a imagem não exista
                                error_content=ft.Container(bgcolor="#EEEEEE", height=150, alignment=ft.alignment.center, content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color="grey"))
                            ),
                            ft.Container(
                                padding=ft.padding.only(top=15, left=20, right=20, bottom=20),
                                content=ft.Column(
                                    spacing=5,
                                    controls=[
                                        ft.Text(title, size=16, weight="bold", color="black"),
                                        ft.Text(description, size=13, color="grey", selectable=False),
                                    ]
                                )
                            )
                        ]
                    ),
                    
                    # Botão Flutuante (+)
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ADD, 
                            icon_color="white", 
                            icon_size=30,
                            on_click=lambda _: go_to_form(route)
                        ),
                        bgcolor="#39BFEF",
                        shape=ft.BoxShape.CIRCLE,
                        width=50, height=50,
                        alignment=ft.alignment.center,
                        right=20, top=125,
                        # MUDANÇA: Hexadecimal direto para evitar erro
                        shadow=ft.BoxShadow(blur_radius=5, color="#4D000000") # Preto com 30% opacidade
                    )
                ]
            ),
            margin=ft.margin.only(bottom=20)
        )

    # --- Conteúdo da Aba ---
    content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Cadastro", size=24, weight="bold", color="black"),
                ft.Container(height=10),
                
                # Card 1: Foco de Dengue
                create_action_card(
                    "Cadastrar novo foco de dengue",
                    "Forneça informações necessárias para o cadastro de um local com possíveis focos do mosquito.",
                    "focos.jpg", # A função vai procurar em /images/focos.jpg
                    "/form-foco"
                ),

                # Card 2: Paciente
                create_action_card(
                    "Cadastrar novo paciente",
                    "Forneça informações necessárias para o cadastro de um paciente.",
                    "paciente.jpg", 
                    "/form-paciente"
                ),
                
                ft.Container(height=50)
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        expand=True,
        alignment=ft.alignment.top_left
    )

    return content