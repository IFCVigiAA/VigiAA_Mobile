import flet as ft
import requests
import config

def get_profile_tab(page: ft.Page):
    API_URL = config.API_URL
    fields_refs = {}

    def logout(e):
        page.client_storage.remove("token")
        page.go("/login")

    # --- LÓGICA DE EXCLUIR CONTA ---
    def delete_account_action(e):
        page.close(confirm_dialog)
        token = page.client_storage.get("token")
        
        if not token: return

        try:
            response = requests.delete(
                f"{API_URL}/api/delete-account/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Conta desativada."))
                page.snack_bar.open = True
                page.update()
                logout(None)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Erro ao desativar conta."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                
        except Exception as ex:
            print(f"Erro: {ex}")

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir Conta"),
        content=ft.Text("Tem certeza? Isso desativará sua conta permanentemente."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
            ft.TextButton("Sim, Excluir", on_click=delete_account_action, style=ft.ButtonStyle(color="red")),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_delete_dialog(e):
        page.open(confirm_dialog)

    # --- FÁBRICA DE LINHAS (Visual Clean) ---
    def create_clean_row(label, api_key, is_email=False):
        text_field = ft.TextField(
            value="Carregando...",
            read_only=True,
            border=ft.InputBorder.NONE,
            text_size=16,
            color="grey",
            text_align=ft.TextAlign.LEFT,
            expand=True,
            disabled=is_email,
            content_padding=ft.padding.only(left=20) 
        )

        fields_refs[api_key] = text_field

        if is_email:
            return ft.Column([
                ft.Container(
                    padding=ft.padding.symmetric(vertical=10),
                    content=ft.Row(
                        controls=[
                            ft.Container(ft.Text(label, weight="bold", size=16, color="black"), width=100),
                            text_field,
                            ft.Container(width=30)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                ),
                ft.Divider(height=1, thickness=0.5, color="#EEEEEE")
            ])

        btn_edit = ft.IconButton(icon=ft.Icons.EDIT, icon_color="grey", icon_size=20, tooltip="Editar")
        btn_save = ft.IconButton(icon=ft.Icons.CHECK, icon_color="green", icon_size=20, tooltip="Salvar", visible=False)
        btn_cancel = ft.IconButton(icon=ft.Icons.CLOSE, icon_color="red", icon_size=20, tooltip="Cancelar", visible=False)

        original_value = [""]

        def on_edit(e):
            original_value[0] = text_field.value
            text_field.read_only = False
            text_field.color = "black"
            text_field.content_padding = ft.padding.all(10) 
            text_field.border = ft.InputBorder.UNDERLINE 
            text_field.focus()
            
            btn_edit.visible = False
            btn_save.visible = True
            btn_cancel.visible = True
            page.update()

        def on_cancel(e):
            text_field.value = original_value[0]
            text_field.read_only = True
            text_field.color = "grey"
            text_field.text_align = ft.TextAlign.LEFT
            text_field.content_padding = ft.padding.only(left=20)
            text_field.border = ft.InputBorder.NONE
            
            btn_edit.visible = True
            btn_save.visible = False
            btn_cancel.visible = False
            page.update()

        def on_save(e):
            token = page.client_storage.get("token")
            payload = {api_key: text_field.value}

            try:
                response = requests.patch(
                    f"{API_URL}/api/profile/",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text(f"{label} salvo!"), bgcolor="green")
                    text_field.read_only = True
                    text_field.color = "grey"
                    text_field.text_align = ft.TextAlign.LEFT
                    text_field.content_padding = ft.padding.only(left=20)
                    text_field.border = ft.InputBorder.NONE
                    btn_edit.visible = True
                    btn_save.visible = False
                    btn_cancel.visible = False
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Erro ao salvar."), bgcolor="red")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        btn_edit.on_click = on_edit
        btn_cancel.on_click = on_cancel
        btn_save.on_click = on_save

        return ft.Column([
            ft.Container(
                padding=ft.padding.symmetric(vertical=5),
                content=ft.Row(
                    controls=[
                        ft.Container(ft.Text(label, weight="bold", size=16, color="black"), width=100),
                        text_field,
                        ft.Row([btn_edit, btn_save, btn_cancel], spacing=0)
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            ),
            ft.Divider(height=1, thickness=0.5, color="#EEEEEE")
        ])

    # --- BOTÕES DE AÇÃO ---

    # 1. Redefinir Senha
    def go_to_reset_password(e):
        page.go("/change-password")

    btn_reset_password = ft.Container(
        padding=ft.padding.symmetric(vertical=15),
        content=ft.Row(
            controls=[
                ft.Text("Redefinir senha", weight="bold", size=16, color="black"),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color="grey")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        on_click=go_to_reset_password,
        ink=True 
    )

    # 2. Sair da Conta (Logout) - AGORA NO ESTILO LISTA
    btn_logout = ft.Container(
        padding=ft.padding.symmetric(vertical=15),
        content=ft.Row(
            controls=[
                ft.Text("Sair da conta", weight="bold", size=16, color="black"),
                ft.Icon(ft.Icons.LOGOUT, color="grey", size=20) # Ícone de porta/saída
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        on_click=logout,
        ink=True 
    )

    # 3. Excluir Conta (Vermelho)
    btn_delete_account = ft.Container(
        padding=ft.padding.symmetric(vertical=15),
        content=ft.Row(
            controls=[
                ft.Text("Excluir conta", weight="bold", size=16, color="red"),
                ft.Icon(ft.Icons.DELETE_FOREVER, color="red") 
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        on_click=open_delete_dialog,
        ink=True 
    )

    switch_display = ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.Row(
            controls=[
                ft.Text("Modo de exibição", weight="bold", size=16),
                ft.Switch(active_color="#39BFEF")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    def load_user_data():
        token = page.client_storage.get("token")
        if not token: return
        try:
            response = requests.get(f"{API_URL}/api/profile/", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                data = response.json()
                if 'username' in fields_refs: fields_refs['username'].value = data.get('username', '')
                if 'email' in fields_refs: fields_refs['email'].value = data.get('email', '')
                if 'first_name' in fields_refs: fields_refs['first_name'].value = data.get('first_name', '')
                if 'last_name' in fields_refs: fields_refs['last_name'].value = data.get('last_name', '')
                page.update()
        except Exception as ex:
            print(f"Erro: {ex}")

    # --- MONTAGEM DA TELA ---
    row_first_name = create_clean_row("Nome", "first_name")
    row_last_name = create_clean_row("Sobrenome", "last_name")
    row_username = create_clean_row("Usuário", "username")
    row_email = create_clean_row("Email", "email", is_email=True)

    content = ft.Container(
        bgcolor="white",
        padding=20,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Icon(ft.Icons.PERSON, size=60, color="black"), 
                        radius=60, 
                        bgcolor="#E0E0E0"
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=30)
                ),
                
                switch_display,
                ft.Divider(height=1, thickness=0.5, color="#EEEEEE"),
                
                row_first_name,
                row_last_name,
                row_username,
                row_email,
                
                # --- Seção de Ações ---
                btn_reset_password,
                ft.Divider(height=1, thickness=0.5, color="#EEEEEE"),
                
                # Sair da Conta (Agora aqui em cima)
                btn_logout,
                ft.Divider(height=1, thickness=0.5, color="#EEEEEE"),
                
                # Excluir Conta (Por último)
                btn_delete_account,
                
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        expand=True
    )

    load_user_data()
    return content