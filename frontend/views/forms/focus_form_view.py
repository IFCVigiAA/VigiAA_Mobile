import flet as ft
import requests
import config

def create_focus_form_view(page: ft.Page):
    API_URL = config.API_URL
    selected_files = [] 
    
    # Grid de Imagens
    images_grid = ft.Row(wrap=True, spacing=10)

    # Função para voltar
    def back_click(e):
        page.go("/novo")

    def close_success_dialog(e):
        page.close(success_dialog)
        back_click(None)

    # --- POP-UP DE SUCESSO ---
    success_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Sucesso!"),
        content=ft.Text("O foco de dengue foi cadastrado corretamente."),
        actions=[
            ft.TextButton("OK", on_click=close_success_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # --- BANCO DE DADOS DE BAIRROS ---
    neighborhoods_db = {
        "Camboriú": [
            "Areias", "Braço", "Caetés", "Cedro", "Centro", 
            "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", 
            "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", 
            "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"
        ],
        "Balneário Camboriú": [
            "Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", 
            "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", 
            "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", 
            "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"
        ]
    }

    # --- Gerenciamento de Imagens ---
    def remove_image(file_obj):
        if file_obj in selected_files:
            selected_files.remove(file_obj)
            update_images_display()

    def update_images_display():
        images_grid.controls.clear()
        for file in selected_files:
            img_card = ft.Container(
                width=100, height=100,
                border_radius=10,
                content=ft.Stack([
                    ft.Image(src=file.path, fit=ft.ImageFit.COVER, width=100, height=100, border_radius=10),
                    ft.Container(
                        content=ft.IconButton(ft.Icons.DELETE, icon_color="black", icon_size=18, 
                            on_click=lambda e, f=file: remove_image(f)),
                        bgcolor="white", shape=ft.BoxShape.CIRCLE, right=5, top=5, width=30, height=30
                    )
                ])
            )
            images_grid.controls.append(img_card)
        
        add_btn = ft.Container(
            width=100, height=100,
            bgcolor="#E0E0E0", border_radius=10, alignment=ft.alignment.center,
            content=ft.Icon(ft.Icons.ADD, size=40, color="black54"),
            on_click=lambda _: file_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
        )
        images_grid.controls.append(add_btn)
        page.update()

    file_picker = ft.FilePicker(on_result=lambda e: (selected_files.extend(e.files) if e.files else None, update_images_display()))
    page.overlay.append(file_picker)

    # --- LÓGICA DE API ---
    def search_cep(e):
        cep = tf_cep.value.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            tf_cep.suffix = ft.Container(ft.ProgressRing(width=20, height=20, stroke_width=2), padding=10)
            tf_cep.update()
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                data = response.json()
                if "erro" not in data:
                    fill_address_fields(data)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("CEP não encontrado."), bgcolor="red")
                    page.snack_bar.open = True
            except:
                page.snack_bar = ft.SnackBar(ft.Text("Erro na busca."), bgcolor="red")
                page.snack_bar.open = True
            tf_cep.suffix = None
            page.update()

    def search_address_by_name(e):
        city = dd_municipio.value
        street_part = tf_rua.value

        if not city:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione a cidade primeiro."), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return
        if len(street_part) < 3:
            page.snack_bar = ft.SnackBar(ft.Text("Digite pelo menos 3 letras da rua."), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        btn_search_rua.icon = ft.Icons.HOURGLASS_TOP
        btn_search_rua.update()

        try:
            url = f"https://viacep.com.br/ws/SC/{city}/{street_part}/json/"
            response = requests.get(url)
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                open_address_selector(data)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Nenhuma rua encontrada."), bgcolor="red")
                page.snack_bar.open = True
        except Exception as ex:
            print(ex)
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao buscar ruas."), bgcolor="red")
            page.snack_bar.open = True

        btn_search_rua.icon = ft.Icons.SEARCH
        btn_search_rua.update()

    def fill_address_fields(data):
        api_city = data.get("localidade")
        api_bairro = data.get("bairro")
        api_rua = data.get("logradouro")
        api_cep = data.get("cep")

        dd_municipio.value = api_city
        
        if api_city in neighborhoods_db:
            current_list = neighborhoods_db[api_city].copy()
            if api_bairro and api_bairro not in current_list:
                current_list.append(api_bairro)
                current_list.sort()
            dd_bairro.options = [ft.dropdown.Option(b) for b in current_list]
            dd_bairro.disabled = False
        else:
            dd_bairro.options = [ft.dropdown.Option(api_bairro)] if api_bairro else []
            dd_bairro.disabled = False

        dd_bairro.value = api_bairro
        tf_rua.value = api_rua
        tf_cep.value = api_cep
        tf_numero.focus()
        page.update()

    # --- MODAL ---
    def open_address_selector(address_list):
        list_items = []
        for addr in address_list:
            list_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCATION_ON, color="#39BFEF"),
                    title=ft.Text(addr.get("logradouro", ""), weight="bold"),
                    subtitle=ft.Text(f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}"),
                    on_click=lambda e, a=addr: select_address_from_modal(a)
                )
            )
        address_dialog.content = ft.Column(list_items, height=300, scroll=ft.ScrollMode.AUTO)
        page.open(address_dialog)

    def select_address_from_modal(addr_data):
        page.close(address_dialog)
        fill_address_fields(addr_data)

    address_dialog = ft.AlertDialog(title=ft.Text("Selecione a Rua"), content=ft.Container())

    def on_city_change(e):
        city = dd_municipio.value
        if city in neighborhoods_db:
            dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[city]]
            dd_bairro.disabled = False
            dd_bairro.value = None
        else:
            dd_bairro.options = []
            dd_bairro.disabled = True
        dd_bairro.update()

    # --- CAMPOS ---
    tf_cep = ft.TextField(
        hint_text="00000-000", text_size=14, border="none", content_padding=0, 
        on_change=search_cep, keyboard_type=ft.KeyboardType.NUMBER, max_length=8,
        width=float("inf")
    )

    dd_municipio = ft.Dropdown(
        hint_text="Selecione", text_size=14, border="none", icon=ft.Icons.KEYBOARD_ARROW_DOWN,
        options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")],
        on_change=on_city_change,
        width=float("inf")
    )
    
    dd_bairro = ft.Dropdown(
        hint_text="Selecione o bairro", text_size=14, border="none", icon=ft.Icons.KEYBOARD_ARROW_DOWN,
        disabled=True,
        width=float("inf")
    )
    
    tf_rua = ft.TextField(
        hint_text="Digite o nome da rua...", text_size=14, border="none", content_padding=0,
        on_submit=search_address_by_name,
        width=float("inf")
    )
    
    btn_search_rua = ft.IconButton(
        icon=ft.Icons.SEARCH, icon_color="#39BFEF", tooltip="Pesquisar nome da rua",
        on_click=search_address_by_name
    )

    tf_numero = ft.TextField(hint_text="Número", text_size=14, border="none", content_padding=0, width=float("inf"))
    
    tf_descricao = ft.TextField(
        multiline=True, min_lines=3, text_size=14, border="none",
        # PLACEHOLDER ATUALIZADO
        hint_text="Descreva a situação do local.\nObs: POR FAVOR, NÃO SE IDENTIFIQUE.",
        hint_style=ft.TextStyle(color="grey"),
        width=float("inf")
    )

    # --- LAYOUT VISUAL ---
    def create_row(label, field, required=False, extra_control=None):
        spans = [ft.TextSpan(label, style=ft.TextStyle(color="black", weight="bold", size=13))]
        if required:
            spans.append(ft.TextSpan("*", style=ft.TextStyle(color="red", weight="bold")))
        
        right_content_controls = [ft.Container(content=field, expand=True, alignment=ft.alignment.center_left)]
        if extra_control:
            right_content_controls.append(extra_control)
        
        is_multiline = getattr(field, "multiline", False)

        return ft.Column([
            ft.Container(
                padding=ft.padding.symmetric(vertical=15), 
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START if is_multiline else ft.CrossAxisAlignment.CENTER, 
                    controls=[
                        ft.Container(width=90, content=ft.Text(spans=spans)),
                        ft.Row(controls=right_content_controls, expand=True, spacing=5)
                    ]
                )
            ),
            ft.Divider(height=1, thickness=0.5, color="#EEEEEE")
        ], spacing=0)

    btn_gps = ft.ElevatedButton(
        text="Capturar localização pelo GPS", icon=ft.Icons.LOCATION_ON,
        bgcolor="#39BFEF", color="white", width=float("inf"), height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    btn_submit = ft.ElevatedButton(
        text="CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    def submit_form(e):
        token = page.client_storage.get("token")
        if not token: 
            page.go("/login")
            return

        if not dd_municipio.value or not dd_bairro.value or not tf_rua.value or not tf_numero.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos obrigatórios."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        btn_submit.text = "Enviando..."
        btn_submit.disabled = True
        page.update()

        try:
            data_payload = {
                "cep": tf_cep.value,
                "city": dd_municipio.value,
                "neighborhood": dd_bairro.value,
                "street": tf_rua.value,
                "number": tf_numero.value,
                "description": tf_descricao.value,
                "latitude": "-27.000", "longitude": "-48.000"
            }
            files_payload = []
            opened_files = [] 
            for file_ref in selected_files:
                f = open(file_ref.path, 'rb')
                opened_files.append(f)
                files_payload.append(('uploaded_images', (file_ref.name, f, 'image/jpeg')))

            response = requests.post(f"{API_URL}/api/report-focus/", data=data_payload, files=files_payload, headers={"Authorization": f"Bearer {token}"})

            for f in opened_files: f.close()

            if response.status_code == 201:
                # SUCESSO EXPLÍCITO: Abre o Dialog em vez de Snack Bar
                page.open(success_dialog)
                
                # Limpa tudo
                tf_descricao.value = ""; tf_cep.value = ""; tf_numero.value = ""
                tf_rua.value = ""; dd_bairro.value = None; dd_bairro.disabled = True; dd_municipio.value = None
                selected_files.clear()
                update_images_display()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {response.text}"), bgcolor="red")
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red")
            page.snack_bar.open = True
        
        btn_submit.text = "CADASTRAR"
        btn_submit.disabled = False
        page.update()

    btn_submit.on_click = submit_form
    update_images_display()

    header = ft.Container(
        padding=ft.padding.only(top=40, left=10, right=20, bottom=10),
        bgcolor="white",
        content=ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color="black", on_click=back_click),
            ft.Text("Focos de mosquitos", size=20, weight="bold", color="black"),
            ft.Container(width=40) 
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    form_body = ft.Container(
        padding=20,
        bgcolor="white",
        expand=True,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                btn_gps,
                ft.Container(height=20),
                create_row("CEP", tf_cep),
                create_row("MUNICÍPIO", dd_municipio, required=True),
                create_row("BAIRRO", dd_bairro, required=True),
                create_row("RUA", tf_rua, required=True, extra_control=btn_search_rua),
                create_row("NÚMERO", tf_numero, required=True),
                create_row("DESCRIÇÃO", tf_descricao),

                # IMAGENS AGORA ESTÃO GRUDADAS NA DESCRIÇÃO (Sem espaço extra antes)
                ft.Container(height=10),
                ft.Text("IMAGENS", weight="bold", size=13),
                images_grid, 
                
                ft.Container(height=30),
                btn_submit,
                ft.Container(height=100), 
            ]
        )
    )

    return ft.View(
        route="/form-foco",
        controls=[header, ft.Divider(height=1, color="#EEEEEE"), form_body],
        bgcolor="white",
        padding=0
    )