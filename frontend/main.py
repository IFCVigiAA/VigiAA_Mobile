import flet as ft
# Imports das views
from views.home_view import create_main_view
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.forms.focus_form_view import create_focus_form_view

def main(page: ft.Page):
    # --- CONFIGURAÇÕES ---
    page.title = "Dengue Focus"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.assets_dir = "assets"
    
    def route_change(e):
        # Limpa as telas da memória
        page.views.clear()
        
        # Pega a rota atual
        route = page.route
        print(f"--- Rota Atual: {route} ---") # Debug no terminal

        # --- ROTA RAIZ (HOME) ---
        if route == "/":
            # Verifica se TEM TOKEN
            token = page.client_storage.get("token")
            print(f"Token encontrado? {bool(token)}")

            if not token:
                # SE NÃO TEM TOKEN, REDIRECIONA PARA /login DE VERDADE
                # Isso evita o bug de estar na rota "/" mostrando login
                print("Sem token. Indo para /login...")
                page.go("/login") 
                return # Para a execução aqui para não carregar mais nada
            else:
                # SE TEM TOKEN, MOSTRA A HOME
                print("Token válido. Carregando Home...")
                page.views.append(create_main_view(page, aba_inicial=0))

        # --- ROTA LOGIN (Agora existe separada) ---
        elif route == "/login":
            page.views.append(create_login_view(page))

        # --- ROTA REGISTRO ---
        elif route == "/register":
            page.views.append(create_register_view(page))

        # --- ROTA NOVO ---
        elif route == "/novo":
            if not page.client_storage.contains_key("token"):
                page.go("/login")
            else:
                page.views.append(create_main_view(page, aba_inicial=1))

        # --- ROTA FORMULÁRIO ---
        elif route == "/form-foco":
            page.views.append(create_main_view(page))
            page.views.append(create_focus_form_view(page))

        # ATUALIZA A TELA
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Inicia a navegação
    page.go(page.route)

ft.app(target=main)