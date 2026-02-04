import flet as ft
import requests
import config
from urllib.parse import quote
import unicodedata
import threading

def create_focus_form_view(page: ft.Page):
    try:
        API_URL = config.API_URL
        selected_files = []
        gps_address_data = {} 
        
        # --- 1. COMPONENTES DO SISTEMA (FilePicker e GPS) ---
        # Nós vamos criar e adicionar ao overlay com cuidado para não travar
        
        def on_file_result(e):
            if e.files:
                selected_files.extend(e.files)
                update_images_display()
        
        file_picker = ft.FilePicker(on_result=on_file_result)
        
        # Lógica do GPS
        def on_gps_position(e):
            print(f"GPS SUCESSO! Lat: {e.latitude}, Lon: {e.longitude}")
            get_address_from_coords(e.latitude, e.longitude, source="GPS (Preciso)")

        def on_gps_error(e):
            print(f"Erro GPS: {e.error}")
            try:
                page.open(ft.SnackBar(ft.Text(f"GPS Falhou: {e.error}. Usando IP."), bgcolor="orange"))
            except: pass
            try_ip_location()

        # Criamos o GPS Vazio
        geolocator = ft.Geolocator()
        geolocator.on_position = on_gps_position
        geolocator.on_error = on_gps_error

        # *** AQUI ESTÁ A CORREÇÃO CRÍTICA ***
        # Adicionamos ao overlay (onde invisíveis devem morar)
        # Mas verificamos se já existe para não duplicar
        if file_picker not in page.overlay:
            page.overlay.append(file_picker)
            
        if geolocator not in page.overlay:
            page.overlay.append(geolocator)
            
        # Importante: Atualizamos a página para o Flet registrar os componentes
        page.update()

        # --- NAVEGAÇÃO E DIÁLOGOS ---
        def back_click(e):
            page.go("/novo")

        def close_success_dialog(e):
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

        # --- LISTA DE IMAGENS ---
        images_list_container = ft.Column(spacing=15)

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
                            alignment=ft.MainAxisAlignment.CENTER, spacing=2, expand=True,
                            controls=[
                                ft.Text(file.name, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text("Imagem", color="grey", size=12)
                            ]
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
                vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
            )
            images_list_container.controls.append(add_btn_row)

        # --- DADOS ---
        neighborhoods_db = {
            "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"],
            "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
        }

        # --- MODAL GPS ---
        gps_overlay = ft.Container(
            visible=False, bgcolor="#80000000", alignment=ft.alignment.center, expand=True, 
            on_click=lambda e: None,
            content=ft.Container(
                width=320, bgcolor="white", border_radius=20, padding=25, shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, height=350,
                    controls=[
                        ft.Icon(ft.Icons.MAP_SHARP, color="#39BFEF", size=50),
                        ft.Text("Localização Encontrada!", size=20, weight="bold", color="#39BFEF"),
                        ft.Text(value="Fonte: ...", size=10, color="grey"),
                        ft.Divider(),
                        ft.Text("Confira os dados abaixo:", size=14, color="grey"),
                        ft.Container(bgcolor="#F5F5F5", padding=15, border_radius=10, content=ft.Column([ft.Text(value="", weight="bold", color="black", size=14), ft.Text(value="", size=13, color="black"), ft.Text(value="", size=12, color="grey")], spacing=2)),
                        ft.Container(height=10),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.OutlinedButton("Cancelar", on_click=lambda e: close_gps_modal()), ft.ElevatedButton("Confirmar", bgcolor="#39BFEF", color="white", on_click=lambda e: confirm_gps_fill())])
                    ]
                )
            )
        )
        
        lbl_gps_rua = gps_overlay.content.content.controls[5].content.controls[0]
        lbl_gps_bairro = gps_overlay.content.content.controls[5].content.controls[1]
        lbl_gps_cidade = gps_overlay.content.content.controls[5].content.controls[2]
        lbl_gps_source = gps_overlay.content.content.controls[2]

        def close_gps_modal():
            gps_overlay.visible = False; btn_gps.text = "GPS NOVO V7"; btn_gps.icon = ft.Icons.LOCATION_ON; btn_gps.disabled = False; page.update()

        def confirm_gps_fill():
            fill_address_fields(gps_address_data); close_gps_modal()

        # --- FUNÇÕES AUXILIARES ---
        def try_ip_location():
            if btn_gps.disabled:
                try:
                    res = requests.get("http://ip-api.com/json/", timeout=5)
                    if res.status_code == 200:
                        data = res.json()
                        get_address_from_coords(data.get('lat'), data.get('lon'), source="Internet (Aproximado)")
                    else: raise Exception("Falha IP")
                except:
                    btn_gps.text = "GPS Indisponível"; btn_gps.disabled = False; page.update()

        def gps_timeout_handler():
            if btn_gps.disabled == True:
                page.open(ft.SnackBar(ft.Text("Sinal de GPS demorou. Usando rede..."), bgcolor="orange"))
                try_ip_location()

        def get_gps_click(e):
            btn_gps.text = "Localizando..."; btn_gps.icon = ft.Icons.HOURGLASS_TOP; btn_gps.disabled = True; page.update()
            
            # AUMENTAMOS PARA 15 SEGUNDOS (Tempo para o satélite responder)
            threading.Timer(15.0, gps_timeout_handler).start()
            
            try:
                geolocator.get_current_position(accuracy=ft.GeolocatorPositionAccuracy.HIGH)
            except Exception as ex:
                print(f"Erro GPS Call: {ex}")
                try_ip_location()

        def get_address_from_coords(lat, lon, source="GPS"):
            try:
                headers = {'User-Agent': 'VigiAA/1.0'}
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
                res = requests.get(url, headers=headers).json()
                addr = res.get("address", {})
                
                gps_address_data.clear()
                gps_address_data["localidade"] = addr.get("city") or addr.get("town") or addr.get("municipality")
                gps_address_data["bairro"] = addr.get("suburb") or addr.get("neighbourhood")
                gps_address_data["logradouro"] = addr.get("road")
                gps_address_data["cep"] = addr.get("postcode")
                gps_address_data["numero"] = addr.get("house_number")
                
                lbl_gps_rua.value = gps_address_data["logradouro"] or "Rua não detectada"
                lbl_gps_bairro.value = gps_address_data["bairro"] or "Bairro não detectado"
                lbl_gps_cidade.value = gps_address_data["localidade"] or "Cidade não detectada"
                lbl_gps_source.value = f"Fonte: {source}"
                lbl_gps_source.color = "red" if "Internet" in source else "green"
                
                gps_overlay.visible = True
                btn_gps.text = "Capturar localização pelo GPS"; btn_gps.icon = ft.Icons.LOCATION_ON; btn_gps.disabled = False; page.update()
            except:
                page.open(ft.SnackBar(ft.Text("Erro ao traduzir endereço."), bgcolor="red"))
                btn_gps.text = "Tentar Novamente"; btn_gps.icon = ft.Icons.REFRESH; btn_gps.disabled = False; page.update()

        def normalize_string(s):
            if not s: return ""
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

        def fill_address_fields(data):
            city_api = data.get("localidade") or ""
            city_clean = normalize_string(city_api)
            target_city = None
            if "balneario" in city_clean and "camboriu" in city_clean: target_city = "Balneário Camboriú"
            elif "camboriu" in city_clean and "balneario" not in city_clean: target_city = "Camboriú"
            if target_city:
                dd_municipio.value = target_city
                dd_bairro.disabled = False
                if target_city in neighborhoods_db:
                    opts = neighborhoods_db[target_city]
                    b = data.get("bairro")
                    if b:
                        if b not in opts: opts.append(b); opts.sort()
                        dd_bairro.value = b
                    dd_bairro.options = [ft.dropdown.Option(o) for o in opts]
                tf_rua.value = data.get("logradouro")
                tf_cep.value = data.get("cep")
                if data.get("numero"): tf_numero.value = data.get("numero")
            else:
                dd_municipio.value = None; dd_bairro.value = None; dd_bairro.disabled = True; dd_bairro.options = []; tf_rua.value = ""; tf_numero.value = ""; tf_cep.value = ""
                page.open(ft.SnackBar(content=ft.Text(f"Atenção: Serviço indisponível em {city_api}. Apenas Camboriú e BC.", color="white"), bgcolor="red", duration=5000))
            page.update()

        # --- BUSCA DE RUA ---
        overlay_list_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        address_overlay = ft.Container(
            visible=False, bgcolor="#80000000", alignment=ft.alignment.center, expand=True, on_click=lambda e: close_manual_modal(None),
            content=ft.Container(width=320, height=500, bgcolor="white", border_radius=20, padding=20, shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"), on_click=lambda e: None,
                content=ft.Column(controls=[ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("Selecione a Rua", size=18, weight="bold", color="#39BFEF"), ft.Icon(ft.Icons.LOCATION_CITY, color="#39BFEF")]), ft.Divider(height=1, color="#EEEEEE"), ft.Container(height=10), ft.Container(content=overlay_list_content, expand=True), ft.Container(height=10), ft.ElevatedButton("Fechar", bgcolor="#39BFEF", color="white", width=float("inf"), height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: close_manual_modal(None))])))

        def open_manual_modal(address_list):
            overlay_list_content.controls.clear()
            overlay_list_content.controls.append(ft.Container(padding=ft.padding.only(bottom=10), content=ft.Text(f"{len(address_list)} ruas encontradas:", size=12, color="grey")))
            for addr in address_list:
                overlay_list_content.controls.append(ft.Container(padding=15, border=ft.border.only(bottom=ft.BorderSide(1, "#F5F5F5")), content=ft.Row([ft.Icon(ft.Icons.PLACE, color="grey", size=16), ft.Column([ft.Text(addr.get("logradouro", ""), weight="bold", size=14, color="#333333"), ft.Text(f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}", size=12, color="grey")], spacing=2, expand=True)], spacing=10), on_click=lambda e, a=addr: select_address_manual(a), bgcolor="white", ink=True, border_radius=8))
            address_overlay.visible = True; page.update()
        
        def close_manual_modal(e): address_overlay.visible = False; page.update()
        def select_address_manual(addr_data): address_overlay.visible = False; page.update(); fill_address_fields(addr_data)
        
        def search_cep(e):
            cep = tf_cep.value.replace("-", "").replace(".", "").strip()
            if len(cep) == 8:
                try:
                    res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
                    if "erro" not in res: fill_address_fields(res)
                except: pass
        
        def search_address_by_name(e):
            city = dd_municipio.value; street = tf_rua.value
            if not city: page.open(ft.SnackBar(ft.Text("Selecione a cidade!"), bgcolor="orange")); return
            if len(street) < 3: page.open(ft.SnackBar(ft.Text("Mínimo 3 letras."), bgcolor="orange")); return
            btn_search_rua.icon = ft.Icons.HOURGLASS_TOP; btn_search_rua.update()
            try:
                res = requests.get(f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street)}/json/").json()
                if isinstance(res, list) and len(res) > 0: open_manual_modal(res)
                else: page.open(ft.SnackBar(ft.Text("Nada encontrado."), bgcolor="red"))
            except: page.open(ft.SnackBar(ft.Text("Erro na busca."), bgcolor="red"))
            btn_search_rua.icon = ft.Icons.SEARCH; btn_search_rua.update()

        def on_city_change(e):
            city = dd_municipio.value
            if city in neighborhoods_db: dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[city]]; dd_bairro.disabled = False
            else: dd_bairro.disabled = True
            page.update()

        # --- CAMPOS UI ---
        tf_cep = ft.TextField(hint_text="Digite o CEP", on_change=search_cep, keyboard_type=ft.KeyboardType.NUMBER, border="none", text_size=14, content_padding=10)
        dd_municipio = ft.Dropdown(hint_text="Selecione a cidade", options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")], on_change=on_city_change, icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        dd_bairro = ft.Dropdown(hint_text="Selecione o bairro", disabled=True, icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        tf_rua = ft.TextField(hint_text="Digite o nome da rua", on_submit=search_address_by_name, border="none", text_size=14, content_padding=10)
        btn_search_rua = ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#39BFEF", tooltip="Pesquisar rua", on_click=search_address_by_name)
        tf_numero = ft.TextField(hint_text="Digite o número", border="none", text_size=14, content_padding=10)
        tf_descricao = ft.TextField(hint_text="Descreva o local", multiline=True, min_lines=3, border="none", text_size=14, content_padding=10)
        btn_gps = ft.ElevatedButton("VERSÃO FINAL V8", icon=ft.Icons.LOCATION_ON, bgcolor="#39BFEF", color="white", width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=get_gps_click)
        btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

        def submit_form(e):
            token = page.client_storage.get("token")
            if not token: page.go("/login"); return
            if not all([dd_municipio.value, dd_bairro.value, tf_rua.value, tf_numero.value]): page.open(ft.SnackBar(ft.Text("Preencha obrigatórios!"), bgcolor="red")); return
            btn_submit.text = "Enviando..."; btn_submit.disabled = True; page.update()
            try:
                data = {"cep": tf_cep.value, "city": dd_municipio.value, "neighborhood": dd_bairro.value, "street": tf_rua.value, "number": tf_numero.value, "description": tf_descricao.value, "latitude": "-27.000", "longitude": "-48.000"}
                files = [('uploaded_images', (f.name, open(f.path, 'rb'), 'image/jpeg')) for f in selected_files]
                headers = {"Authorization": f"Bearer {token}"}
                res = requests.post(f"{API_URL}/api/report-focus/", data=data, files=files, headers=headers)
                if res.status_code == 201: page.dialog = success_dialog; success_dialog.open = True; page.update()
                else: page.open(ft.SnackBar(ft.Text(f"Erro: {res.text}"), bgcolor="red"))
            except Exception as ex: page.open(ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red"))
            btn_submit.text = "CADASTRAR"; btn_submit.disabled = False; page.update()

        btn_submit.on_click = submit_form
        update_images_display()

        # --- LAYOUT FINAL ---
        header = ft.Container(padding=ft.padding.only(top=40, left=10, right=20, bottom=15), bgcolor="white", content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20), ft.Text("Focos de mosquitos", size=18, weight="bold", color="black"), ft.Container(width=40)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        def create_row(label, field, extra=None): return ft.Column([ft.Container(padding=ft.padding.symmetric(vertical=5, horizontal=20), content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(width=100, content=ft.Text(label, style=ft.TextStyle(color="black", weight="bold", size=12))), ft.Row([ft.Container(content=field, expand=True)] + ([extra] if extra else []), expand=True)])), ft.Divider(height=1, color="#F5F5F5")], spacing=0)

        form_body = ft.Container(bgcolor="white", expand=True, content=ft.ListView(padding=ft.padding.only(bottom=30), controls=[
            ft.Container(padding=20, content=btn_gps),
            create_row("CEP", tf_cep), create_row("MUNICÍPIO", dd_municipio), create_row("BAIRRO", dd_bairro), create_row("RUA", tf_rua, btn_search_rua), create_row("NÚMERO", tf_numero), create_row("DESCRIÇÃO", tf_descricao),
            ft.Container(padding=20, content=ft.Column([ft.Text("IMAGENS", weight="bold", size=12), images_list_container])), ft.Container(padding=20, content=btn_submit),
        ]))

# --- AQUI ESTÁ A GARANTIA CONTRA TELA VERMELHA ---
        return ft.View(
            route="/form-foco", 
            bgcolor="white", 
            padding=0, 
            controls=[
                # 1. Os invisíveis ficam aqui "soltos" (O Flet sabe lidar com eles aqui)
                file_picker,
                geolocator,
                
                # 2. A parte visual fica dentro da Stack
                ft.Stack(
                    expand=True, 
                    controls=[
                        # Cabeçalho e Corpo
                        ft.Column(expand=True, spacing=0, controls=[header, ft.Divider(height=1, color="#EEEEEE"), form_body]),
                        
                        # Modais (Janelas flutuantes)
                        gps_overlay, 
                        address_overlay
                    ]
                )
            ]
        )

    except Exception as e:
        print(f"Erro ao criar tela: {e}")
        return ft.View(route="/form-foco", controls=[ft.Text(f"Erro crítico: {e}", color="red")])