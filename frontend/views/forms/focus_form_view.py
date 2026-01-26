import flet as ft
import requests
import config
from urllib.parse import quote
import unicodedata

def create_focus_form_view(page: ft.Page):
    # Limpeza inicial
    page.overlay.clear()
    
    API_URL = config.API_URL
    selected_files = []
    gps_address_data = {} 
    
    # --- FILE PICKER ---
    def on_file_result(e):
        if e.files:
            selected_files.extend(e.files)
            update_images_display()
            
    file_picker = ft.FilePicker(on_result=on_file_result)
    # Adiciona o FilePicker no overlay para garantir que funcione sempre
    page.overlay.append(file_picker)
    
    # --- FUNÇÕES DE NAVEGAÇÃO ---
    def back_click(e):
        page.go("/novo")

    # ===============================================================
    # 1. COMPONENTE GPS (NOVA ESTRUTURA)
    # ===============================================================
    
    def on_gps_position(e):
        lat = e.latitude
        lon = e.longitude
        accuracy = e.accuracy
        print(f"GPS Nativo SUCESSO! Lat: {lat}, Lon: {lon}, Acc: {accuracy}")
        get_address_from_coords(lat, lon, source="GPS (Preciso)")

    def on_gps_error(e):
        print(f"Erro GPS Nativo: {e.error}")
        # Mostra erro visual
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"GPS falhou: {e.error}. Verifique se o GPS está ligado!"),
            bgcolor="red",
            duration=4000
        )
        page.snack_bar.open = True
        page.update()
        
        # Tenta o IP como último recurso
        try_ip_location()

    geolocator = ft.Geolocator()
    geolocator.on_position = on_gps_position
    geolocator.on_error = on_gps_error
    
    # IMPORTANTE: Adiciona o Geolocator no Overlay (Camada Superior)
    page.overlay.append(geolocator)

    # ===============================================================
    # 2. OVERLAY DE ERRO (ÁREA DE COBERTURA)
    # ===============================================================
    error_overlay = ft.Container(
        visible=False,
        bgcolor="#80000000",
        alignment=ft.alignment.center,
        expand=True,
        on_click=lambda e: close_error_modal(None),
        content=ft.Container(
            width=300,
            bgcolor="white",
            border_radius=20,
            padding=25,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                height=280,
                controls=[
                    ft.Icon(ft.Icons.LOCATION_OFF, color="red", size=60),
                    ft.Text("Fora da área!", size=22, weight="bold", color="black"),
                    ft.Text(
                        "O endereço informado não pertence a Camboriú ou Balneário Camboriú.", 
                        size=14, 
                        color="grey", 
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.ElevatedButton(
                        "Entendi", 
                        bgcolor="red", 
                        color="white", 
                        width=120, 
                        on_click=lambda e: close_error_modal(None)
                    )
                ]
            )
        )
    )

    def open_error_modal():
        error_overlay.visible = True
        page.update()

    def close_error_modal(e):
        dd_municipio.value = None
        dd_bairro.value = None
        tf_rua.value = ""
        tf_numero.value = ""
        dd_bairro.disabled = True
        error_overlay.visible = False
        page.update()

    # ===============================================================
    # 3. OVERLAY DE CONFIRMAÇÃO DO GPS
    # ===============================================================
    gps_overlay = ft.Container(
        visible=False,
        bgcolor="#80000000",
        alignment=ft.alignment.center,
        expand=True,
        on_click=lambda e: None,
        content=ft.Container(
            width=320,
            bgcolor="white",
            border_radius=20,
            padding=25,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                height=380,
                controls=[
                    ft.Icon(ft.Icons.MAP_SHARP, color="#39BFEF", size=50),
                    ft.Text("Localização Encontrada!", size=20, weight="bold", color="#39BFEF"),
                    ft.Text(value="Fonte: GPS", size=10, color="grey", text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    ft.Text("Confira os dados abaixo:", size=14, color="grey"),
                    ft.Container(
                        bgcolor="#F5F5F5",
                        padding=15,
                        border_radius=10,
                        content=ft.Column([
                            ft.Text(value="", weight="bold", color="black", size=14), # Rua
                            ft.Text(value="", size=13, color="black"), # Bairro
                            ft.Text(value="", size=12, color="grey"), # Cidade
                        ], spacing=2)
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.OutlinedButton("Cancelar", on_click=lambda e: close_gps_modal()),
                            ft.ElevatedButton("Confirmar", bgcolor="#39BFEF", color="white", on_click=lambda e: confirm_gps_fill())
                        ]
                    )
                ]
            )
        )
    )
    
    lbl_gps_rua = gps_overlay.content.content.controls[5].content.controls[0]
    lbl_gps_bairro = gps_overlay.content.content.controls[5].content.controls[1]
    lbl_gps_cidade = gps_overlay.content.content.controls[5].content.controls[2]
    lbl_gps_source = gps_overlay.content.content.controls[2]

    def close_gps_modal():
        gps_overlay.visible = False
        btn_gps.text = "Capturar localização pelo GPS"
        btn_gps.icon = ft.Icons.LOCATION_ON
        btn_gps.disabled = False
        page.update()

    def confirm_gps_fill():
        fill_address_fields(gps_address_data)
        close_gps_modal()

    # ===============================================================
    # 4. OVERLAY DE SUCESSO
    # ===============================================================
    success_overlay = ft.Container(
        visible=False,
        bgcolor="#80000000",
        alignment=ft.alignment.center,
        expand=True,
        on_click=lambda e: close_success_manual(None), 
        content=ft.Container(
            width=300,
            height=200,
            bgcolor="white",
            border_radius=20,
            padding=25,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"),
            on_click=lambda e: e.control.focus(), 
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=60),
                    ft.Text("Sucesso!", size=22, weight="bold", color="black"),
                    ft.Text("Foco cadastrado corretamente.", size=14, color="grey", text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton("OK", bgcolor="#39BFEF", color="white", width=120, on_click=lambda e: close_success_manual(None))
                ]
            )
        )
    )

    def open_success_manual():
        success_overlay.visible = True
        page.update()

    def close_success_manual(e):
        success_overlay.visible = False
        page.update()
        back_click(None)

    # ===============================================================
    # 5. OVERLAY DE ENDEREÇO (MANUAL)
    # ===============================================================
    overlay_list_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
    
    address_overlay = ft.Container(
        visible=False,
        bgcolor="#80000000",
        alignment=ft.alignment.center,
        expand=True, 
        on_click=lambda e: close_manual_modal(None),
        content=ft.Container(
            width=320,
            height=500,
            bgcolor="white",
            border_radius=20,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"),
            on_click=lambda e: e.control.focus(),
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[ft.Text("Selecione a Rua", size=18, weight="bold", color="#39BFEF"), ft.Icon(ft.Icons.LOCATION_CITY, color="#39BFEF")]
                    ),
                    ft.Divider(height=1, color="#EEEEEE"),
                    ft.Container(height=10),
                    ft.Container(content=overlay_list_content, expand=True),
                    ft.Container(height=10),
                    ft.ElevatedButton("Fechar", bgcolor="#39BFEF", color="white", width=float("inf"), height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: close_manual_modal(None))
                ]
            )
        )
    )

    def open_manual_modal(address_list):
        overlay_list_content.controls.clear()
        overlay_list_content.controls.append(ft.Container(padding=ft.padding.only(bottom=10), content=ft.Text(f"{len(address_list)} ruas encontradas:", size=12, color="grey")))
        for addr in address_list:
            overlay_list_content.controls.append(
                ft.Container(
                    padding=15,
                    border=ft.border.only(bottom=ft.BorderSide(1, "#F5F5F5")),
                    content=ft.Row([ft.Icon(ft.Icons.PLACE, color="grey", size=16), ft.Column([ft.Text(addr.get("logradouro", ""), weight="bold", size=14, color="#333333"), ft.Text(f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}", size=12, color="grey")], spacing=2, expand=True)], spacing=10),
                    on_click=lambda e, a=addr: select_address_manual(a), bgcolor="white", ink=True, border_radius=8
                )
            )
        address_overlay.visible = True
        page.update()

    def close_manual_modal(e):
        address_overlay.visible = False
        page.update()

    def select_address_manual(addr_data):
        address_overlay.visible = False
        page.update()
        fill_address_fields(addr_data)

    # --- LÓGICA DE IMAGENS ---
    images_list_container = ft.Column(spacing=15)
    def remove_image(file_obj):
        if file_obj in selected_files: selected_files.remove(file_obj); update_images_display()

    def update_images_display():
        images_list_container.controls.clear()
        for file in selected_files:
            img_row = ft.Row(controls=[ft.Image(src=file.path, width=60, height=60, fit=ft.ImageFit.COVER, border_radius=8), ft.Column(alignment=ft.MainAxisAlignment.CENTER, spacing=2, expand=True, controls=[ft.Text(file.name, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), ft.Text("Imagem", color="grey", size=12)]), ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="black54", on_click=lambda e, f=file: remove_image(f))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            images_list_container.controls.append(img_row)
        add_btn_row = ft.Row(controls=[ft.Container(width=60, height=60, bgcolor="#E0E0E0", border_radius=8, alignment=ft.alignment.center, content=ft.Icon(ft.Icons.ADD, size=30, color="black54"), on_click=lambda _: file_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)), ft.Text("Adicionar imagem", color="grey", size=16)], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        images_list_container.controls.append(add_btn_row)
        page.update()

    # --- DADOS E API ---
    neighborhoods_db = {
        "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"],
        "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
    }

    # --- LÓGICA DO GPS (COM FALLBACK IP) ---
    def try_ip_location():
        print("Tentando via IP (Fallback)...")
        try:
            res = requests.get("http://ip-api.com/json/", timeout=5)
            if res.status_code == 200:
                data = res.json()
                get_address_from_coords(data.get('lat'), data.get('lon'), source="Internet (Aproximado)")
            else: raise Exception("API IP falhou")
        except:
            btn_gps.text = "GPS Indisponível"; btn_gps.disabled = False; page.update()

    def get_gps_click(e):
        btn_gps.text = "Localizando..."; btn_gps.icon = ft.Icons.HOURGLASS_TOP; btn_gps.disabled = True; page.update()
        try:
            # Solicita sem parâmetros para maximizar compatibilidade
            geolocator.get_current_position()
        except Exception as ex:
            print(f"Falha chamada GPS: {ex}")
            try_ip_location()

    def get_address_from_coords(lat, lon, source="GPS"):
        try:
            headers = {'User-Agent': 'VigiAA/1.0'}
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            addr = data.get("address", {})
            
            gps_address_data.clear()
            
            gps_address_data["localidade"] = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("village")
            gps_address_data["bairro"] = addr.get("suburb") or addr.get("neighbourhood") or addr.get("quarter")
            gps_address_data["logradouro"] = addr.get("road") or addr.get("pedestrian")
            gps_address_data["cep"] = addr.get("postcode")
            gps_address_data["numero"] = addr.get("house_number")
            
            lbl_gps_rua.value = gps_address_data["logradouro"] or "Rua não detectada"
            lbl_gps_bairro.value = gps_address_data["bairro"] or "Bairro não detectado"
            lbl_gps_cidade.value = gps_address_data["localidade"] or "Cidade não detectada"
            lbl_gps_source.value = f"Fonte: {source}"
            
            if "Internet" in source:
                lbl_gps_source.color = "red"
            else:
                lbl_gps_source.color = "green"
            
            gps_overlay.visible = True
            btn_gps.text = "Capturar localização pelo GPS"; btn_gps.icon = ft.Icons.LOCATION_ON; btn_gps.disabled = False
            page.update()
        except Exception as ex:
            print(f"Erro GPS: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao traduzir coordenadas."), bgcolor="red"); page.snack_bar.open = True; page.update()
            btn_gps.text = "Tentar Novamente"; btn_gps.icon = ft.Icons.REFRESH; btn_gps.disabled = False; page.update()

    # --- PREENCHIMENTO E BLOQUEIO ---
    def normalize_string(s):
        if not s: return ""
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

    def fill_address_fields(data):
        print(f"Validando dados: {data}")
        
        city_api = data.get("localidade") or ""
        city_clean = normalize_string(city_api)
        target_city = None
        
        if "balneario" in city_clean and "camboriu" in city_clean:
            target_city = "Balneário Camboriú"
        elif "camboriu" in city_clean and "balneario" not in city_clean:
            target_city = "Camboriú"
        
        if not target_city:
            open_error_modal()
            return

        dd_municipio.value = target_city
        dd_bairro.disabled = False
        
        if target_city in neighborhoods_db:
            current_opts = neighborhoods_db[target_city]
            bairro_api = data.get("bairro")
            if bairro_api:
                if bairro_api not in current_opts:
                    current_opts.append(bairro_api)
                    current_opts.sort()
                dd_bairro.value = bairro_api
            else:
                dd_bairro.value = None
            dd_bairro.options = [ft.dropdown.Option(b) for b in current_opts]
        
        tf_rua.value = data.get("logradouro")
        tf_cep.value = data.get("cep")
        if data.get("numero"): tf_numero.value = data.get("numero")
        
        page.update()

    # --- FUNÇÕES DE BUSCA ---
    def search_cep(e):
        cep = tf_cep.value.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            try:
                res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
                if "erro" not in res: fill_address_fields(res)
            except: pass

    def search_address_by_name(e):
        city = dd_municipio.value
        street_part = tf_rua.value
        if not city: page.snack_bar = ft.SnackBar(ft.Text("Selecione a cidade primeiro."), bgcolor="orange"); page.snack_bar.open = True; page.update(); return
        if len(street_part) < 3: page.snack_bar = ft.SnackBar(ft.Text("Digite pelo menos 3 letras."), bgcolor="orange"); page.snack_bar.open = True; page.update(); return
        btn_search_rua.icon = ft.Icons.HOURGLASS_TOP; btn_search_rua.update()
        try:
            url = f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street_part)}/json/"
            res = requests.get(url).json()
            if isinstance(res, list) and len(res) > 0: open_manual_modal(res)
            else: page.snack_bar = ft.SnackBar(ft.Text("Nenhuma rua encontrada."), bgcolor="red"); page.snack_bar.open = True; page.update()
        except: pass
        btn_search_rua.icon = ft.Icons.SEARCH; btn_search_rua.update()

    def on_city_change(e):
        city = dd_municipio.value
        if city in neighborhoods_db:
            dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[city]]
            dd_bairro.disabled = False
        else: dd_bairro.disabled = True; dd_bairro.update()

    # --- CAMPOS ---
    input_style = {"border": "none", "text_size": 14, "content_padding": 10}
    tf_cep = ft.TextField(hint_text="Digite o CEP", on_change=search_cep, keyboard_type=ft.KeyboardType.NUMBER, **input_style)
    dd_municipio = ft.Dropdown(hint_text="Selecione a cidade", options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")], on_change=on_city_change, **input_style, icon=ft.Icons.KEYBOARD_ARROW_DOWN)
    dd_bairro = ft.Dropdown(hint_text="Selecione o bairro", disabled=True, **input_style, icon=ft.Icons.KEYBOARD_ARROW_DOWN)
    tf_rua = ft.TextField(hint_text="Digite o nome da rua", on_submit=search_address_by_name, **input_style)
    btn_search_rua = ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#39BFEF", tooltip="Pesquisar rua", on_click=search_address_by_name)
    tf_numero = ft.TextField(hint_text="Digite o número", **input_style)
    tf_descricao = ft.TextField(hint_text="Descreva a situação do local.\nObs: não se identifique de nenhuma forma", multiline=True, min_lines=3, **input_style)

    btn_gps = ft.ElevatedButton(
        "Capturar localização pelo GPS", 
        icon=ft.Icons.LOCATION_ON, 
        bgcolor="#39BFEF", 
        color="white", 
        width=float("inf"), 
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=get_gps_click
    )

    btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    def submit_form(e):
        token = page.client_storage.get("token")
        if not token: page.go("/login"); return
        if not all([dd_municipio.value, dd_bairro.value, tf_rua.value, tf_numero.value]): page.snack_bar = ft.SnackBar(ft.Text("Preencha os campos obrigatórios!"), bgcolor="red"); page.snack_bar.open = True; page.update(); return
        btn_submit.text = "Enviando..."; btn_submit.disabled = True; page.update()
        try:
            data = {"cep": tf_cep.value, "city": dd_municipio.value, "neighborhood": dd_bairro.value, "street": tf_rua.value, "number": tf_numero.value, "description": tf_descricao.value, "latitude": "-27.000", "longitude": "-48.000"}
            files = [('uploaded_images', (f.name, open(f.path, 'rb'), 'image/jpeg')) for f in selected_files]
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{API_URL}/api/report-focus/", data=data, files=files, headers=headers)
            for _, (n, f, t) in files: f.close()
            if res.status_code == 201: open_success_manual()
            else: page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {res.text}"), bgcolor="red"); page.snack_bar.open = True
        except Exception as ex: page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red"); page.snack_bar.open = True
        btn_submit.text = "CADASTRAR"; btn_submit.disabled = False; page.update()

    btn_submit.on_click = submit_form
    update_images_display() 

    # --- LAYOUT PRINCIPAL ---
    header = ft.Container(padding=ft.padding.only(top=40, left=10, right=20, bottom=15), bgcolor="white", content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20), ft.Text("Focos de mosquitos", size=18, weight="bold", color="black"), ft.Container(width=40)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
    def create_row(label, field, required=False, extra=None):
        spans = [ft.TextSpan(label, style=ft.TextStyle(color="black", weight="bold", size=12))]
        if required: spans.append(ft.TextSpan("*", style=ft.TextStyle(color="red", weight="bold")))
        row_controls = [ft.Container(content=field, expand=True)]
        if extra: row_controls.append(extra)
        return ft.Column([ft.Container(padding=ft.padding.symmetric(vertical=5, horizontal=20), content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(width=100, content=ft.Text(spans=spans)), ft.Row(row_controls, expand=True)])), ft.Divider(height=1, thickness=1, color="#F5F5F5")], spacing=0)

    form_body = ft.Container(bgcolor="white", expand=True, content=ft.ListView(padding=ft.padding.only(bottom=30), controls=[
        ft.Container(padding=20, content=btn_gps),
        ft.Container(padding=ft.padding.only(left=20, right=20, bottom=10), content=ft.Row([ft.Text("*", color="red", weight="bold", size=12), ft.Text("Itens marcados com asterisco são obrigatórios", color="grey", size=12)], spacing=5)),
        create_row("CEP", tf_cep),
        create_row("MUNICÍPIO", dd_municipio, required=True),
        create_row("BAIRRO", dd_bairro, required=True),
        create_row("RUA", tf_rua, required=True, extra=btn_search_rua),
        create_row("NÚMERO", tf_numero, required=True),
        create_row("DESCRIÇÃO", tf_descricao),
        ft.Container(padding=20, content=ft.Column([ft.Text("IMAGENS", weight="bold", size=12), ft.Container(height=10), images_list_container])),
        ft.Container(padding=20, content=btn_submit),
    ]))

    return ft.View(
        route="/form-foco", bgcolor="white", padding=0, 
        controls=[
            ft.Stack(expand=True, controls=[
                ft.Column(expand=True, spacing=0, controls=[header, ft.Divider(height=1, thickness=1, color="#EEEEEE"), form_body]),
                address_overlay,
                success_overlay,
                gps_overlay, 
                error_overlay 
            ]),
            # Adicionado corretamente ao overlay agora
            # (Removemos da Stack visual e colocamos no append acima)
        ]
    )