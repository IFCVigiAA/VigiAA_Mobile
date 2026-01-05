import flet as ft
import requests
import config

def create_change_password_view(page: ft.Page):
    API_URL = config.API_URL

    # --- Estilo Minimalista para os Campos ---
    def create_minimal_field(label):
        return ft.TextField(
            label=label,
            password=True,
            can_reveal_password=True,
            
            # Visual Clean (Só a linha de baixo)
            border=ft.InputBorder.UNDERLINE,
            border_color="#E0E0E0",     # Cinza claro quando inativo
            focused_border_color="#39BFEF", # Azul da marca quando foca
            cursor_color="#39BFEF",
            
            # Tipografia
            text_style=ft.TextStyle(size=16, color="black"),
            label_style=ft.TextStyle(size=14, color="grey"),
            
            # Remove cor de fundo
            filled=False,
            content_padding=ft.padding.symmetric(vertical=15)
        )

    # Criando os campos
    tf_old_password = create_minimal_field("Senha Atual")
    tf_new_password = create_minimal_field("Nova Senha")
    tf_confirm_password = create_minimal_field("Confirmar Nova Senha")

    # Botão de Ação
    btn_save = ft.ElevatedButton(
        text="Salvar Nova Senha",
        bgcolor="black", # Preto fica mais elegante/minimalista nesse contexto
        color="white",
        width=float("inf"),
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8), # Cantos levemente arredondados
            elevation=0 # Sem sombra para ficar "Flat"
        )
    )

    def back_to_profile(e):
        page.client_storage.set("selected_tab_index", 3)
        page.go("/")

    def change_password_action(e):
        token = page.client_storage.get("token")
        
        # Validação
        if not tf_old_password.value or not tf_new_password.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        if tf_new_password.value != tf_confirm_password.value:
            page.snack_bar = ft.SnackBar(ft.Text("A nova senha não confere."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        # Feedback
        btn_save.text = "Processando..."
        btn_save.disabled = True
        page.update()

        try:
            response = requests.put(
                f"{API_URL}/api/change-password/",
                json={
                    "old_password": tf_old_password.value,
                    "new_password": tf_new_password.value
                },
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Senha alterada com sucesso!"), bgcolor="green")
                # Limpa campos
                tf_old_password.value = ""
                tf_new_password.value = ""
                tf_confirm_password.value = ""
            else:
                try:
                    erro = list(response.json().values())[0]
                    if isinstance(erro, list): erro = erro[0]
                except:
                    erro = "Erro ao alterar senha."
                page.snack_bar = ft.SnackBar(ft.Text(f"{erro}"), bgcolor="red")

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text("Erro de conexão."), bgcolor="red")
        
        btn_save.text = "Salvar Nova Senha"
        btn_save.disabled = False
        page.snack_bar.open = True
        page.update()

    btn_save.on_click = change_password_action

    # --- Header (Igual ao das outras telas, sem o sino) ---
    header = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#3AC0ED", "#72FC90"]
        ),
        padding=ft.padding.only(left=10, right=20, top=35, bottom=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, 
                    icon_color="#1a1a1a",
                    on_click=back_to_profile
                ),
                ft.Text(
                    "Alterar Senha", 
                    size=20, 
                    weight="bold", 
                    color="#1a1a1a"
                ),
                # Espaço vazio para manter o título no centro (Compensa o botão de voltar)
                ft.Container(width=40) 
            ]
        )
    )

    return ft.View(
        route="/change-password",
        controls=[
            header,
            ft.Container(
                padding=30, # Bastante respiro nas bordas
                bgcolor="white",
                content=ft.Column(
                    controls=[
                        # Título interno discreto
                        ft.Text("Defina sua nova credencial", color="grey", size=14),
                        ft.Container(height=20),
                        
                        tf_old_password,
                        ft.Container(height=10),
                        
                        tf_new_password,
                        ft.Container(height=10),
                        
                        tf_confirm_password,
                        ft.Container(height=40),
                        
                        btn_save
                    ]
                )
            )
        ],
        bgcolor="white",
        padding=0
    )