import flet as ft
# Imports das views
from views.home_view import create_main_view
from views.login_view import create_login_view
from views.register_view import create_register_view
from views.change_password_view import create_change_password_view
from views.forms.focus_form_view import create_focus_form_view

def main(page: ft.Page):
    # --- CONFIGURAÇÃO VITAL ---
    page.title = "Dengue Focus"
    page.theme_mode = ft.ThemeMode.LIGHT
    # AQUI: Dizemos ao Flet onde procurar imagens (na pasta 'assets' dentro de frontend)
    page.assets_dir = "assets" 
    
    def route_change(e):
        # Limpa as telas anteriores para evitar sobreposições e erros
        page.views.clear()

        route = page.route

        # --- ROTA RAIZ (HOME PADRÃO - Aba 0) ---
        if route == "/":
            if not page.client_storage.contains_key("token"):
                page.views.append(create_login_view(page))
            else:
                page.views.append(create_main_view(page, aba_inicial=0))

        # --- ROTA NOVA (HOME - Aba 1/Novo) ---
        # Usada quando voltamos do formulário
        elif route == "/novo":
            if not page.client_storage.contains_key("token"):
                page.views.append(create_login_view(page))
            else:
                page.views.append(create_main_view(page, aba_inicial=1))

        # --- ROTAS DE AUTENTICAÇÃO ---
        elif route == "/login":
            page.views.append(create_login_view(page))
        elif route == "/register":
            page.views.append(create_register_view(page))
        elif route == "/change-password":
            # Cria a home por baixo para dar contexto
            page.views.append(create_main_view(page))
            page.views.append(create_change_password_view(page))

        # --- ROTA: FORMULÁRIO DE FOCO ---
        elif route == "/form-foco":
            # Cria a Home por baixo
            page.views.append(create_main_view(page))
            # Põe o formulário por cima
            page.views.append(create_focus_form_view(page))

        page.update()

    # --- CORREÇÃO DO INDEX ERROR ---
    def view_pop(e):
        # Só tentamos voltar se houver mais de uma tela na pilha
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            # Se for a última tela, não faz nada ou força a ida para home
            # Isso evita o crash quando não tem para onde voltar
            print("Não há tela anterior para voltar.")
            # Opcional: se estiver perdido, força a home
            if page.route != "/": page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Inicia a navegação
    page.go(page.route)

ft.app(target=main)