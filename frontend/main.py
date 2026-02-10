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
        
        print(f"Navegando para: {page.route}")

        if page.route == "/login":
            page.views.append(create_login_view(page))
        
        elif page.route == "/register":
            page.views.append(create_register_view(page))
            
        elif page.route == "/forgot-password":
            page.views.append(create_forgot_password_view(page))
            
        elif page.route == "/change-password":
            page.views.append(create_change_password_view(page))
            
        elif page.route == "/":
            page.views.append(create_main_view(page, aba_inicial=0)) # Aba Home
            
        elif page.route == "/explorar":
            page.views.append(create_main_view(page, aba_inicial=1)) # Aba Explorar
            
        elif page.route == "/novo":
            page.views.append(create_main_view(page, aba_inicial=2)) # Aba Novo
            
        elif page.route == "/mapa":
            page.views.append(create_main_view(page, aba_inicial=3)) # Aba Mapa
            
        elif page.route == "/perfil":
            page.views.append(create_main_view(page, aba_inicial=4)) # Aba Perfil

        # Rotas de Formulários
        elif page.route == "/form-foco":
            page.views.append(create_focus_form_view(page))
            
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Configuração da Barra de Navegação (Fina - 60px)
    page.navigation_bar = ft.NavigationBar(
        height=60, 
        bgcolor="white",
        indicator_color="#E0F7FA",
        surface_tint_color="white",
        shadow_color="black",
        elevation=10,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label="Explorar"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Novo"),
            ft.NavigationBarDestination(icon=ft.Icons.MAP_OUTLINED, selected_icon=ft.Icons.MAP, label="Mapa"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Perfil"),
        ],
        on_change=lambda e: change_tab(e.control.selected_index)
    )

    # Função auxiliar para trocar abas
    def change_tab(index):
        if index == 0: page.go("/")
        elif index == 1: page.go("/novo")
        elif index == 2: page.go("/explorar")
        elif index == 3: page.go("/mapa")
        elif index == 4: page.go("/perfil")

    # Verifica login inicial
    token = page.client_storage.get("token")
    if token:
        page.go("/")
    else:
        page.go("/login")

ft.app(target=main)