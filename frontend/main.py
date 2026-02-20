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

    # --- 1. CRIA A BARRA PRIMEIRO (AGORA AZUL) ---
    page.navigation_bar = ft.NavigationBar(
        height=60, 
        bgcolor="#39BFEF", # CORREÇÃO: Azul do projeto
        indicator_color="#2898C2", # Azul um pouco mais escuro para o item selecionado
        surface_tint_color="#39BFEF",
        shadow_color="black",
        elevation=10,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        destinations=[
            # Usando NavigationBarDestination compatível com sua versão
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Novo"),
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label="Explorar"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Perfil"),
        ],
        on_change=lambda e: change_tab(e.control.selected_index)
    )

    def change_tab(index):
        if index == 0: page.go("/")
        elif index == 1: page.go("/novo")
        elif index == 2: page.go("/explorar")
        elif index == 3: page.go("/perfil")

    # --- 2. GERENCIA AS ROTAS ---
    def route_change(e):
        page.views.clear()
        
        if page.route == "/login":
            page.views.append(create_login_view(page))
        
        elif page.route == "/register":
            page.views.append(create_register_view(page))
            
        elif page.route == "/forgot-password":
            page.views.append(create_forgot_password_view(page))
            
        elif page.route == "/change-password":
            page.views.append(create_change_password_view(page))
            
        # Abas
        elif page.route == "/":
            page.navigation_bar.selected_index = 0
            page.views.append(create_main_view(page, aba_inicial=0))
            
        elif page.route == "/novo":
            page.navigation_bar.selected_index = 1
            page.views.append(create_main_view(page, aba_inicial=1))
            
        elif page.route == "/explorar":
            page.navigation_bar.selected_index = 2
            page.views.append(create_main_view(page, aba_inicial=2))
            
        elif page.route == "/perfil":
            page.navigation_bar.selected_index = 3
            page.views.append(create_main_view(page, aba_inicial=3))

        # Formulários
        elif page.route == "/form-foco":
            page.views.append(create_focus_form_view(page))
            
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- 3. INICIA O APP ---
    token = page.client_storage.get("token")
    if token:
        page.go("/")
    else:
        page.go("/login")

ft.app(target=main)