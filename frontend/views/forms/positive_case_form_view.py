import flet as ft
import requests
import config

def create_positive_case_form_view(page: ft.Page):
    API_URL = config.API_URL

    tf_nome = ft.TextField(hint_text="Digite seu nome", border="none", text_size=14, content_padding=10)
    tf_cpf = ft.TextField(hint_text="000.000.000-00", border="none", text_size=14, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)
    tf_telefone = ft.TextField(hint_text="(XX) XXXXX-XXXX", border="none", text_size=14, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)
    opcoes_locais = ["Posto de Saúde", "Farmácia", "Hospital", "Laboratório"]
    dd_local_teste = ft.Dropdown(hint_text="Selecione o local", options=[ft.dropdown.Option(l) for l in opcoes_locais], icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)

    btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    def close_success_dialog(e):
        try: page.close(success_dialog)
        except: pass
        page.go("/novo") 

    success_dialog = ft.AlertDialog(modal=True, title=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=30), ft.Text("Sucesso!")]), content=ft.Text("Paciente identificado com sucesso!"), actions=[ft.TextButton("OK", on_click=close_success_dialog)])

    def submit_positive_form(e):
        token = page.client_storage.get("token")
        
        # Recupera o ID do caso de dengue base que salvamos na tela anterior
        dengue_case_id = page.session.get("current_case_id")
        
        if not dengue_case_id:
            page.open(ft.SnackBar(ft.Text("Erro: Caso base não encontrado. Volte e tente novamente."), bgcolor="red"))
            return

        if not all([tf_nome.value, tf_telefone.value, dd_local_teste.value]): 
            page.open(ft.SnackBar(ft.Text("Preencha todos os campos obrigatórios (*)!"), bgcolor="red"))
            return
            
        btn_submit.text = "Enviando..."; btn_submit.disabled = True; page.update()
        
        try:
            data = {
                "dengue_case": dengue_case_id,
                "patient_name": tf_nome.value,
                "cpf": tf_cpf.value,
                "phone": tf_telefone.value,
                "test_location": dd_local_teste.value
            }
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{API_URL}/api/report-positive-case/", json=data, headers=headers)
            
            if res.status_code in [200, 201]: 
                try: page.open(success_dialog)
                except: page.dialog = success_dialog; success_dialog.open = True; page.update()
            else: page.open(ft.SnackBar(ft.Text(f"Erro: {res.text}"), bgcolor="red"))
        except Exception as ex: page.open(ft.SnackBar(ft.Text(f"Erro no app: {ex}"), bgcolor="red"))
        btn_submit.text = "CADASTRAR"; btn_submit.disabled = False; page.update()

    btn_submit.on_click = submit_positive_form

    def back_click(e): page.go("/form-caso")
            
    header = ft.Container(padding=ft.padding.only(top=40, left=10, right=20, bottom=15), bgcolor="white", content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20), ft.Text("Casos de dengue", size=18, weight="bold", color="black"), ft.Container(width=40)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
    
    def create_row(label, field, obrigatorio=True): 
        label_controls = [ft.Text(label, style=ft.TextStyle(color="black", weight="bold", size=12))]
        if obrigatorio: label_controls.append(ft.Text(" *", color="red", weight="bold", size=14))
        return ft.Column([ft.Container(padding=ft.padding.symmetric(vertical=5, horizontal=20), content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(width=100, content=ft.Row(label_controls, spacing=0)), ft.Row([ft.Container(content=field, expand=True)], expand=True)])), ft.Divider(height=1, color="#F5F5F5")], spacing=0)

    form_body = ft.Container(bgcolor="white", expand=True, content=ft.ListView(padding=ft.padding.only(bottom=30, top=20), controls=[
        create_row("Nome", tf_nome, obrigatorio=True), 
        create_row("CPF", tf_cpf, obrigatorio=False), 
        create_row("Telefone", tf_telefone, obrigatorio=True), 
        create_row("Local do teste", dd_local_teste, obrigatorio=True), 
        ft.Container(height=40),
        ft.Container(padding=20, content=btn_submit),
    ]))

    return ft.View(
        route="/form-caso-positivo", 
        bgcolor="white", 
        padding=0, 
        controls=[ft.Column(expand=True, spacing=0, controls=[header, ft.Divider(height=1, color="#EEEEEE"), form_body])]
    )