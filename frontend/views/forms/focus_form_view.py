import flet as ft
import requests
import config

def create_focus_form_view(page: ft.Page, file_picker: ft.FilePicker):
    API_URL = config.API_URL
    selected_files = [] 
    
    # --- FUNÇÕES DE NAVEGAÇÃO E DIÁLOGO ---
    def back_click(e):
        page.go("/novo")

    def close_success_dialog(e):
        # FECHAMENTO CLÁSSICO (Garante que fecha visualmente)
        success_dialog.open = False
        page.update()
        back_click(None)

    success_dialog = ft.AlertDialog(
        modal=True, 
        title=ft.Text("Sucesso!"), 
        content=ft.Text("O foco de dengue foi cadastrado corretamente."),
        actions=[ft.TextButton("OK", on_click=close_success_dialog)], 
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- LÓGICA DE IMAGENS ---
    images_list_container = ft.Column(spacing=15)

    def on_file_result(e):
        if e.files:
            selected_files.extend(e.files)
            update_images_display()
    
    # Conecta o FilePicker Global a esta tela
    file_picker.on_result = on_file_result

    def remove_image(file_obj):
        if file_obj in selected_files:
            selected_files.remove(file_obj)
            update_images_display()

    def update_images_display():
        images_list_container.controls.clear()
        
        for file in selected_files:
            img_row = ft.Row(
                controls=[
                    ft.Image(src=file.path, width=60, height=60, fit=ft.ImageFit.COVER, border_radius=8),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text(file.name, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text("Imagem", color="grey", size=12) 
                        ],
                        expand=True
                    ),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="black54", on_click=lambda e, f=file: remove_image(f))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            images_list_container.controls.append(img_row)
        
        add_btn_row = ft.Row(
            controls=[
                ft.Container(
                    width=60, height=60, bgcolor="#E0E0E0", border_radius=8, alignment=ft.alignment.center,
                    content=ft.Icon(ft.Icons.ADD, size=30, color="black54"),
                    on_click=lambda _: file_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                ),
                ft.Text("Adicionar imagem", color="grey", size=16)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
        images_list_container.controls.append(add_btn_row)
        page.update()

    # --- DADOS E API ---
    neighborhoods_db = {
        "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"],
        "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
    }

    def search_cep(e):
        cep = tf_cep.value.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            try:
                res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
                if "erro" not in res: fill_address_fields(res)
            except: pass
    
    def fill_address_fields(data):
        dd_municipio.value = data.get("localidade")
        if dd_municipio.value in neighborhoods_db:
            opts = neighborhoods_db[dd_municipio.value]
            if data.get("bairro") and data.get("bairro") not in opts: opts.append(data.get("bairro"))
            dd_bairro.options = [ft.dropdown.Option(b) for b in sorted(opts)]
            dd_bairro.disabled = False
        dd_bairro.value = data.get("bairro")
        tf_rua.value = data.get("logradouro")
        tf_cep.value = data.get("cep")
        page.update()

    def on_city_change(e):
        city = dd_municipio.value
        if city in neighborhoods_db:
            dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[city]]
            dd_bairro.disabled = False
        else:
            dd_bairro.disabled = True
        dd_bairro.update()

    # --- CAMPOS ---
    input_style = {"border": "none", "text_size": 14, "content_padding": 10}
    tf_cep = ft.TextField(hint_text="Digite o CEP", on_change=search_cep, keyboard_type=ft.KeyboardType.NUMBER, **input_style)
    dd_municipio = ft.Dropdown(hint_text="Selecione a cidade", options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")], on_change=on_city_change, **input_style, icon=ft.Icons.KEYBOARD_ARROW_DOWN)
    dd_bairro = ft.Dropdown(hint_text="Selecione o bairro", disabled=True, **input_style, icon=ft.Icons.KEYBOARD_ARROW_DOWN)
    tf_rua = ft.TextField(hint_text="Digite o nome da rua", **input_style, suffix_icon=ft.Icons.SEARCH)
    tf_numero = ft.TextField(hint_text="Digite o número", **input_style)
    tf_descricao = ft.TextField(hint_text="Descreva a situação do local.\nObs: não se identifique de nenhuma forma", multiline=True, min_lines=3, **input_style)

    btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    def submit_form(e):
        token = page.client_storage.get("token")
        if not token: page.go("/login"); return

        if not all([dd_municipio.value, dd_bairro.value, tf_rua.value, tf_numero.value]):
            page.snack_bar = ft.SnackBar(ft.Text("Preencha os campos obrigatórios!"), bgcolor="red"); page.snack_bar.open = True; page.update(); return

        btn_submit.text = "Enviando..."; btn_submit.disabled = True; page.update()

        try:
            data = {"cep": tf_cep.value, "city": dd_municipio.value, "neighborhood": dd_bairro.value, "street": tf_rua.value, "number": tf_numero.value, "description": tf_descricao.value, "latitude": "-27.000", "longitude": "-48.000"}
            files = [('uploaded_images', (f.name, open(f.path, 'rb'), 'image/jpeg')) for f in selected_files]
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{API_URL}/api/report-focus/", data=data, files=files, headers=headers)
            for _, (n, f, t) in files: f.close()

            if res.status_code == 201:
                # A MÁGICA ACONTECE AQUI: Método Clássico
                page.dialog = success_dialog
                success_dialog.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {res.text}"), bgcolor="red"); page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red"); page.snack_bar.open = True
        
        btn_submit.text = "CADASTRAR"; btn_submit.disabled = False
        # Importante: Atualizamos a página de novo para destravar o botão, 
        # mas como o dialog já está aberto no page.dialog, ele permanece lá.
        page.update()

    btn_submit.on_click = submit_form
    update_images_display() 

    # --- LAYOUT (DESIGN ORIGINAL) ---
    header = ft.Container(
        padding=ft.padding.only(top=40, left=10, right=20, bottom=15),
        bgcolor="white",
        content=ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20),
            ft.Text("Focos de mosquitos", size=18, weight="bold", color="black"),
            ft.Container(width=40)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    def create_row(label, field, required=False):
        spans = [ft.TextSpan(label, style=ft.TextStyle(color="black", weight="bold", size=12))]
        if required: spans.append(ft.TextSpan("*", style=ft.TextStyle(color="red", weight="bold")))
        
        return ft.Column([
            ft.Container(
                padding=ft.padding.symmetric(vertical=5, horizontal=20),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(width=100, content=ft.Text(spans=spans)),
                        ft.Container(content=field, expand=True)
                    ]
                )
            ),
            ft.Divider(height=1, thickness=1, color="#F5F5F5")
        ], spacing=0)

    form_body = ft.Container(
        bgcolor="white",
        expand=True,
        content=ft.ListView(
            padding=ft.padding.only(bottom=30),
            controls=[
                ft.Container(padding=20, content=ft.ElevatedButton("Capturar localização pelo GPS", icon=ft.Icons.LOCATION_ON, bgcolor="#39BFEF", color="white", width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))),
                create_row("CEP", tf_cep),
                create_row("MUNICÍPIO", dd_municipio, required=True),
                create_row("BAIRRO", dd_bairro, required=True),
                create_row("RUA", tf_rua, required=True),
                create_row("NÚMERO", tf_numero, required=True),
                create_row("DESCRIÇÃO", tf_descricao),
                
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("IMAGENS", weight="bold", size=12),
                        ft.Container(height=10),
                        images_list_container,
                    ])
                ),
                ft.Container(padding=20, content=btn_submit),
            ]
        )
    )

    return ft.View(
        route="/form-foco",
        bgcolor="white",
        padding=0,
        controls=[header, ft.Divider(height=1, thickness=1, color="#EEEEEE"), form_body]
    )