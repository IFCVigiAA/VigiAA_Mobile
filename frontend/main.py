import flet as ft
import traceback

# Imports das views
from views.home_view import create_main_view
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.forgot_password_view import create_forgot_password_view
from views.change_password_view import create_change_password_view
from views.forms.focus_form_view import create_focus_form_view

def main(page: ft.Page):
    # --- CONFIGURAÇÕES GERAIS ---
    page.title = "Dengue Focus"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.assets_dir = "assets"
    
    # --- O PORTEIRO ÚNICO ---
    # FilePicker Global (Nunca será duplicado)
    global_file_picker = ft.FilePicker()
    page.overlay.append(global_file_picker)
    
    def route_change(e):
        page.views.clear()
        route = page.route
        print(f"--- Rota Atual: {route} ---")

        try:
            # --- ROTA HOME ---
            if route == "/":
                token = page.client_storage.get("token")
                
                if not token:
                    print("Sem token. Indo para /login...")
                    page.go("/login") 
                    return
                else:
                    print("Token válido. Carregando Home...")
                    page.views.append(create_main_view(page, aba_inicial=0))

            # --- ROTA LOGIN ---
            elif route == "/login":
                page.views.append(create_login_view(page))

            # --- ROTA REGISTRO ---
            elif route == "/register":
                page.views.append(create_register_view(page))
            
            # --- ROTA ESQUECI SENHA ---
            elif route == "/forgot-password":
                page.views.append(create_forgot_password_view(page))

            # --- ROTA MUDAR SENHA ---
            elif route == "/change-password":
                page.views.append(create_change_password_view(page))

            # --- ROTA NOVO (Aba do meio) ---
            elif route == "/novo":
                if not page.client_storage.contains_key("token"):
                    page.go("/login")
                else:
                    page.views.append(create_main_view(page, aba_inicial=1))

            # --- ROTA FORMULÁRIO DE FOCO ---
            elif route == "/form-foco":
                # CORREÇÃO: Não carregamos mais a create_main_view(page) aqui.
                # Isso evita o conflito de navegação que fazia voltar pra Home.
                page.views.append(create_focus_form_view(page, global_file_picker))

        except Exception as ex:
            print("❌ ERRO NO MAIN ❌")
            print(traceback.format_exc())
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro crítico: {ex}"), bgcolor="red")
            page.snack_bar.open = True

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
    
    page.go(page.route)

ft.app(target=main)