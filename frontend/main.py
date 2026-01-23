import flet as ft
import traceback
from views.home_view import create_main_view
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.forgot_password_view import create_forgot_password_view
from views.change_password_view import create_change_password_view # <--- USANDO O ARQUIVO ORIGINAL
from views.forms.focus_form_view import create_focus_form_view

def main(page: ft.Page):
    page.title = "Dengue Focus"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.assets_dir = "assets"
    
    def route_change(e):
        page.views.clear()
        route = page.route
        print(f"--- Rota Atual: {route} ---")

        try:
            if route == "/":
                token = page.client_storage.get("token")
                if not token:
                    page.go("/login") 
                    return
                page.views.append(create_main_view(page, aba_inicial=0))

            elif route == "/login":
                page.views.append(create_login_view(page))

            elif route == "/register":
                page.views.append(create_register_view(page))
            
            elif route == "/forgot-password":
                page.views.append(create_forgot_password_view(page))

            elif route == "/change-password":
                # Chama a visualização original (que agora tem o design novo)
                page.views.append(create_change_password_view(page))

            elif route == "/novo":
                if not page.client_storage.contains_key("token"):
                    page.go("/login")
                else:
                    page.views.append(create_main_view(page, aba_inicial=1))

            elif route == "/form-foco":
                page.views.append(create_focus_form_view(page))

        except Exception as ex:
            print("❌ ERRO NO MAIN ❌")
            print(traceback.format_exc())
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro crítico: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

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