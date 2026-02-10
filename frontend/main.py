import flet as ft
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.forgot_password_view import create_forgot_password_view
from views.change_password_view import create_change_password_view
from views.home_view import create_main_view
from views.forms.focus_form_view import create_focus_form_view

def main(page: ft.Page):
    page.title = "VigiAA Mobile"
    page.bgcolor = "white"
    page.padding = 0 
    page.scroll = ft.ScrollMode.ADAPTIVE

    def route_change(e):
        page.views.clear()
        
        # Roteamento baseado na URL
        if page.route == "/login":
            page.views.append(create_login_view(page))
        
        elif page.route == "/register":
            page.views.append(create_register_view(page))
            
        elif page.route == "/forgot-password":
            page.views.append(create_forgot_password_view(page))
            
        elif page.route == "/change-password":
            page.views.append(create_change_password_view(page))
            
        # --- ABAS PRINCIPAIS (0 a 3) ---
        elif page.route == "/":
            page.views.append(create_main_view(page, aba_inicial=0)) # 0: Home
            
        elif page.route == "/novo":
            page.views.append(create_main_view(page, aba_inicial=1)) # 1: Novo
            
        elif page.route == "/explorar":
            page.views.append(create_main_view(page, aba_inicial=2)) # 2: Explorar
            
        elif page.route == "/perfil":
            page.views.append(create_main_view(page, aba_inicial=3)) # 3: Perfil

        # Formulários (Tela Cheia)
        elif page.route == "/form-foco":
            page.views.append(create_focus_form_view(page))
            
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # --- BARRA DE NAVEGAÇÃO (4 ITENS) ---
    page.navigation_bar = ft.NavigationBar(
        height=60, 
        bgcolor="white",
        indicator_color="#E0F7FA",
        icon_color=ft.Colors.GREY_500, # Ícones não selecionados mais claros
        surface_tint_color="white",
        shadow_color="black",
        elevation=10,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        
        destinations=[
            # 0. Home
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
            # 1. Novo
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Novo"),
            # 2. Explorar
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label="Explorar"),
            # 3. Perfil
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Perfil"),
        ],
        on_change=lambda e: change_tab(e.control.selected_index)
    )

    # Lógica de troca (Sincronizada com a lista acima)
    def change_tab(index):
        if index == 0: page.go("/")
        elif index == 1: page.go("/novo")
        elif index == 2: page.go("/explorar")
        elif index == 3: page.go("/perfil")

    # Verifica login inicial
    token = page.client_storage.get("token")
    if token:
        page.go("/")
    else:
        page.go("/login")

ft.app(target=main)