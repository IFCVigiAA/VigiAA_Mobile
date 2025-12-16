import flet as ft
import requests
import config 

def logout(page: ft.Page):
    page.client_storage.remove("token")
    page.go("/login")

def create_main_view(page: ft.Page):
    API_URL = config.API_URL
    
    # --- 1. COMPONENTE: HEADER (TOPO PERSONALIZADO) ---
    def get_custom_header():
        return ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#3AC0ED", "#72FC90"]
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # ESQUERDA: Logo
                    ft.Image(
                        src="logo-sem-fundo.png", 
                        height=35,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    
                    # CENTRO: Título
                    ft.Text(
                        "VigiAA", 
                        size=22, 
                        weight="bold", 
                        color="#1a1a1a",
                        font_family="Roboto"
                    ),
                    
                    # DIREITA: Sino
                    ft.Stack(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.NOTIFICATIONS_OUTLINED, 
                                icon_color="black",
                                icon_size=28,
                                on_click=lambda _: print("Notificações")
                            ),
                            ft.Container(
                                content=ft.Text("2", size=10, color="white", weight="bold"),
                                alignment=ft.alignment.center,
                                bgcolor="#FF5252",
                                width=16, height=16,
                                border_radius=8,
                                right=5, top=5
                            )
                        ],
                        width=40, height=40
                    )
                ]
            )
        )

    # --- Lógica de Deletar Conta ---
    def delete_account(e):
        page.close(confirm_dialog)
        token = page.client_storage.get("token")
        if not token: return

        try:
            response = requests.delete(
                f"{API_URL}/delete-account/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Conta desativada com sucesso."))
                page.snack_bar.open = True
                page.update()
                logout(page)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Erro ao desativar conta."))
                page.snack_bar.open = True
                page.update()
                
        except Exception as ex:
            print(f"Erro de conexão: {ex}")

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir Conta"),
        content=ft.Text("Tem certeza? Sua conta será desativada."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
            ft.TextButton("Sim, Deletar", on_click=delete_account, style=ft.ButtonStyle(color="red")),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_delete_dialog(e):
        page.open(confirm_dialog)

    # --- CONTEÚDO DAS ABAS ---

    # 1. HOME
    view_home = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.HOME, size=80, color="#39BFEF"),
                ft.Text("Início", size=24, weight="bold"),
                ft.Text("Bem-vindo ao VigiAA", color="grey"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center, expand=True
    )

    # 2. NOVO
    view_add = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ADD_A_PHOTO, size=80, color="#39BFEF"),
                ft.Text("Nova Ocorrência", size=24, weight="bold"),
                ft.ElevatedButton("Reportar Foco", bgcolor="#39BFEF", color="white")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center, expand=True
    )

    # 3. EXPLORAR
    view_explore = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.EXPLORE, size=80, color="#39BFEF"),
                ft.Text("Explorar", size=24, weight="bold"),
                ft.Text("Mapa e estatísticas aqui", color="grey"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center, expand=True
    )

    # 4. PERFIL
    view_profile = ft.Container(
        content=ft.Column(
            [
                ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON, size=40), radius=50, bgcolor="#39BFEF"),
                ft.Text("Minha Conta", size=22, weight="bold"),
                ft.Divider(),
                ft.ElevatedButton(
                    "Sair (Logout)",
                    icon=ft.Icons.LOGOUT,
                    color="white",
                    bgcolor="black",
                    width=200,
                    on_click=lambda _: logout(page) 
                ),
                ft.TextButton(
                    "Deletar minha conta",
                    icon=ft.Icons.DELETE_FOREVER,
                    style=ft.ButtonStyle(color="red"),
                    on_click=open_delete_dialog
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        ),
        alignment=ft.alignment.center, expand=True
    )

    my_tabs = [view_home, view_add, view_explore, view_profile]

    def change_tab(e):
        index = e.control.selected_index
        body_component.content = my_tabs[index]
        body_component.update()

    body_component = ft.Container(content=view_home, expand=True)

    return ft.View(
        route="/",
        controls=[
            get_custom_header(),
            body_component,
            
            # --- BARRA DE NAVEGAÇÃO CORRIGIDA ---
            ft.NavigationBar(
                bgcolor="#39BFEF", 
                indicator_color=ft.Colors.TRANSPARENT, # Remove a bolinha de fundo
                selected_index=0,
                on_change=change_tab,
                destinations=[
                    # 1. Home
                    ft.NavigationBarDestination(
                        icon=ft.Icons.HOME_OUTLINED, 
                        selected_icon=ft.Icons.HOME, # Fica cheio quando selecionado
                        label="Home"
                    ),
                    # 2. Novo
                    ft.NavigationBarDestination(
                        icon=ft.Icons.ADD_BOX_OUTLINED, 
                        selected_icon=ft.Icons.ADD_BOX,
                        label="Novo"
                    ),
                    # 3. Explorar
                    ft.NavigationBarDestination(
                        icon=ft.Icons.EXPLORE_OUTLINED, 
                        selected_icon=ft.Icons.EXPLORE,
                        label="Explorar"
                    ),
                    # 4. Perfil
                    ft.NavigationBarDestination(
                        icon=ft.Icons.PERSON_OUTLINE, 
                        selected_icon=ft.Icons.PERSON,
                        label="Perfil"
                    ),
                ]
            )
        ],
        padding=0,
        bgcolor="white"
    )