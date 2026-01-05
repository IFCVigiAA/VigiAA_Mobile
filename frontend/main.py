import flet as ft

# --- MUDANÇA AQUI: Importando de dentro da pasta 'views' ---
from views.login_view import create_login_view
from views.home_view import create_main_view
from views.register_view import create_register_view
from views.change_password_view import create_change_password_view
# -----------------------------------------------------------

def main(page: ft.Page):
    page.title = "VigiAA"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Gerenciador de Rotas
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        # Pega o token para saber se já está logado
        token = page.client_storage.get("token")

        # Rota de Login
        if page.route == "/login":
            page.views.append(create_login_view(page))
        
        # Rota de Registro
        elif page.route == "/register":
            page.views.append(create_register_view(page))

        # Rota da Home (Protegida)
        elif page.route == "/" or page.route == "":
            if token:
                # Se tem token, carrega a Home (que puxa as abas internamente)
                page.views.append(create_main_view(page)) 
            else:
                page.go("/login")
        
        elif page.route == "/change-password":
            page.views.append(create_change_password_view(page))
        
        # Rota padrão para erros
        else:
            page.go("/login")
        
        page.update()

    page.on_route_change = route_change
    
    # Inicia a navegação
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")