import flet as ft
from login_view import create_login_view  # <--- Importa a tela que criamos acima
from home_view import create_main_view    # <--- Supondo que você tenha esse arquivo
# from register_view import create_register_view # <--- Descomente se tiver esse arquivo

def main(page: ft.Page):
    page.title = "VigiAA"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Função que gerencia a navegação (Roteador)
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        # Pega o token para saber se já está logado
        token = page.client_storage.get("token")

        # --- ROTA: LOGIN ---
        if page.route == "/login":
            page.views.append(create_login_view(page))
        
        # --- ROTA: REGISTRO ---
        elif page.route == "/register":
            # Se você tiver o arquivo register_view.py:
            # page.views.append(create_register_view(page))
            
            # Se não tiver, usa esse provisório:
            page.views.append(ft.View("/register", [
                ft.AppBar(title=ft.Text("Registro")),
                ft.Text("Tela de Registro aqui"),
                ft.ElevatedButton("Voltar", on_click=lambda _: page.go("/login"))
            ]))

        # --- ROTA: HOME (Raiz) ---
        elif page.route == "/" or page.route == "":
            if token:
                # Se tem token, entra no app
                page.views.append(create_main_view(page)) 
            else:
                # Se não tem token, manda pro login
                page.go("/login")
        
        # --- QUALQUER OUTRA ROTA ---
        else:
            page.go("/login")
        
        page.update()

    # Define a função de mudança de rota
    page.on_route_change = route_change
    
    # Inicia na rota atual
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")