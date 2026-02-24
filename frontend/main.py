import flet as ft
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.forgot_password_view import create_forgot_password_view
from views.change_password_view import create_change_password_view
from views.home_view import create_main_view
from views.forms.focus_form_view import create_focus_form_view
from views.forms.case_form_view import create_case_form_view
from views.forms.positive_case_form_view import create_positive_case_form_view

def main(page: ft.Page):
    page.title = "VigiAA Mobile"
    page.bgcolor = "white"
    page.padding = 0 
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.OPEN_UPWARDS,
            ios=ft.PageTransitionTheme.CUPERTINO,
        )
    )

    # TRAVA DE SEGURANÇA: Só muda de tela se realmente for uma tela diferente
    def change_tab(index):
        rotas = ["/", "/novo", "/explorar", "/perfil"]
        if 0 <= index < len(rotas):
            if page.route != rotas[index]: 
                page.go(rotas[index])

    # 1. CRIAMOS A BARRA UMA ÚNICA VEZ GLOBALMENTE! (Mata o clique fantasma)
    nav_bar = ft.NavigationBar(
        height=60, 
        bgcolor="#39BFEF",
        indicator_color="#2898C2", 
        surface_tint_color="#39BFEF",
        shadow_color="black",
        elevation=10,
        selected_index=0,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Novo"),
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label="Explorar"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Perfil"),
        ],
        on_change=lambda e: change_tab(e.control.selected_index)
    )

    # 2. Fixamos a barra na página para sempre
    page.navigation_bar = nav_bar

    def route_change(e):
        rotas_base = ["/", "/novo", "/explorar", "/perfil", "/login", "/register"]
        
        if page.route in rotas_base:
            page.views.clear()
            
        # 3. Lógica inteligente: Esconde a barra dentro dos formulários para dar espaço!
        telas_sem_barra = ["/login", "/register", "/forgot-password", "/change-password", "/form-foco", "/form-caso", "/form-caso-positivo"]
        if page.route in telas_sem_barra:
            nav_bar.visible = False
        else:
            nav_bar.visible = True
        
        if page.route == "/login":
            page.views.append(create_login_view(page))
        elif page.route == "/register":
            page.views.append(create_register_view(page))
        elif page.route == "/forgot-password":
            page.views.append(create_forgot_password_view(page))
            
        # 4. Nas telas base, a gente só "pinta" o ícone atualizado
        elif page.route == "/":
            nav_bar.selected_index = 0 
            page.views.append(create_main_view(page, aba_inicial=0))
            
        elif page.route == "/novo":
            nav_bar.selected_index = 1
            page.views.append(create_main_view(page, aba_inicial=1))
            
        elif page.route == "/explorar":
            nav_bar.selected_index = 2
            page.views.append(create_main_view(page, aba_inicial=2))
            
        elif page.route == "/perfil":
            nav_bar.selected_index = 3
            page.views.append(create_main_view(page, aba_inicial=3))

        # Formulários
        elif page.route == "/form-foco":
            page.views.append(create_focus_form_view(page))
        elif page.route == "/form-caso":
            page.views.append(create_case_form_view(page))
        elif page.route == "/form-caso-positivo":
            page.views.append(create_positive_case_form_view(page))
            
        elif page.route == "/change-password":
            page.views.append(create_change_password_view(page))
            
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            if page.route != "/":
                page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    token = page.client_storage.get("token")
    if token:
        page.go("/")
    else:
        page.go("/login")

ft.app(target=main)