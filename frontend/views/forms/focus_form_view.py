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
        
        # =====================================================================
        # 1. SINGLETONS (Componentes de Memória)
        # =====================================================================
        
        # --- File Picker ---
        if not hasattr(page, "vigi_file_picker"):
            page.vigi_file_picker = ft.FilePicker()
            page.overlay.append(page.vigi_file_picker)
            page.update()
        
        def on_file_result_current(e):
            if e.files:
                selected_files.extend(e.files)
                update_images_display()
        
        page.vigi_file_picker.on_result = on_file_result_current

        # --- GPS ---
        if not hasattr(page, "vigi_geolocator"):
            page.vigi_geolocator = ft.Geolocator()
            page.overlay.append(page.vigi_geolocator)
            page.update()

        # =====================================================================
        # 2. DEFINIÇÃO VISUAL SEGURA (Criamos os Textos ANTES do Layout)
        # =====================================================================
        # Isso evita o erro de "Index out of range" que quebrava o modal
        
        txt_gps_rua = ft.Text(value="Carregando rua...", weight="bold", color="black", size=14)
        txt_gps_bairro = ft.Text(value="Carregando bairro...", size=13, color="black")
        txt_gps_cidade = ft.Text(value="Carregando cidade...", size=12, color="grey")
        txt_gps_source = ft.Text(value="Fonte: ...", size=10, color="grey")

        # =====================================================================
        # 3. FUNÇÕES LÓGICAS
        # =====================================================================

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
                dd_municipio.value = None; dd_bairro.value = None; dd_bairro.disabled = True; dd_bairro.options = []
                tf_rua.value = ""; tf_numero.value = ""; tf_cep.value = ""
                page.open(ft.SnackBar(content=ft.Text(f"Serviço indisponível em {city_api}", color="white"), bgcolor="red"))
            
            page.update()

        # --- Overlay Manual ---
        overlay_list_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        
        def close_manual_modal(e): 
            address_overlay.visible = False; page.update()
            
        def select_address_manual(addr_data): 
            address_overlay.visible = False; page.update(); fill_address_fields(addr_data)

        address_overlay = ft.Container(
            visible=False, bgcolor="#80000000", alignment=ft.alignment.center, expand=True,
            content=ft.Container(width=320, height=500, bgcolor="white", border_radius=20, padding=20,
                content=ft.Column(controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("Selecione a Rua", size=18, weight="bold", color="#39BFEF"), ft.Icon(ft.Icons.LOCATION_CITY, color="#39BFEF")]),
                    ft.Divider(height=1, color="#EEEEEE"),
                    ft.Container(content=overlay_list_content, expand=True),
                    ft.ElevatedButton("Fechar", bgcolor="#39BFEF", color="white", width=float("inf"), on_click=close_manual_modal)
                ]))
        )

        def open_manual_modal(address_list):
            overlay_list_content.controls.clear()
            overlay_list_content.controls.append(ft.Text(f"{len(address_list)} ruas encontradas:", size=12, color="grey"))
            for addr in address_list:
                overlay_list_content.controls.append(ft.Container(padding=10, content=ft.Row([ft.Icon(ft.Icons.PLACE, size=16), ft.Column([ft.Text(addr.get("logradouro", ""), weight="bold"), ft.Text(f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}", size=12)])]), on_click=lambda e, a=addr: select_address_manual(a), ink=True))
            address_overlay.visible = True; page.update()

        # --- Buscas ---
        def search_cep(e):
            cep = tf_cep.value.replace("-", "").replace(".", "").strip()
            if len(cep) == 8:
                try:
                    res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
                    if "erro" not in res: fill_address_fields(res)
                except: pass
        
        def search_address_by_name(e):
            city = dd_municipio.value; street = tf_rua.value
            if not city or len(street) < 3: return
            btn_search_rua.icon = ft.Icons.HOURGLASS_TOP; btn_search_rua.update()
            try:
                res = requests.get(f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street)}/json/").json()
                if isinstance(res, list) and len(res) > 0: open_manual_modal(res)
                else: page.open(ft.SnackBar(ft.Text("Nada encontrado."), bgcolor="red"))
            except: page.open(ft.SnackBar(ft.Text("Erro na busca."), bgcolor="red"))
            btn_search_rua.icon = ft.Icons.SEARCH; btn_search_rua.update()

        neighborhoods_db = {"Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"], "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]}

        def on_city_change(e):
            if dd_municipio.value in neighborhoods_db: 
                dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[dd_municipio.value]]
                dd_bairro.disabled = False
            else: dd_bairro.disabled = True
            page.update()

        # --- LÓGICA DO GPS (MODO MEDIUM) ---
        def run_ip_location():
            # Roda em thread separada para não travar a UI
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
                page.open(ft.SnackBar(ft.Text("Sinal GPS fraco. Usando rede..."), bgcolor="orange"))
                threading.Thread(target=run_ip_location).start()
        
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
                
                # Atualiza os textos do modal (Seguro)
                txt_gps_rua.value = gps_address_data["logradouro"] or "Rua não detectada"
                txt_gps_bairro.value = gps_address_data["bairro"] or "Bairro não detectado"
                txt_gps_cidade.value = gps_address_data["localidade"] or "Cidade não detectada"
                txt_gps_source.value = f"Fonte: {source}"
                txt_gps_source.color = "red" if "Internet" in source else "green"
                
                gps_overlay.visible = True
                btn_gps.text = "Capturar localização pelo GPS"; btn_gps.icon = ft.Icons.LOCATION_ON; btn_gps.disabled = False; page.update()
            except:
                page.open(ft.SnackBar(ft.Text("Erro ao traduzir endereço."), bgcolor="red"))
                btn_gps.text = "Tentar Novamente"; btn_gps.disabled = False; page.update()

        def on_gps_position(e):
            get_address_from_coords(e.latitude, e.longitude, source="GPS (Preciso)")

        def on_gps_error(e):
            print(f"Erro GPS: {e.error}")
            try_ip_location_thread()

        def try_ip_location_thread():
             threading.Thread(target=run_ip_location).start()

        page.vigi_geolocator.on_position = on_gps_position
        page.vigi_geolocator.on_error = on_gps_error

        def get_gps_click(e):
            btn_gps.text = "Localizando..."; btn_gps.icon = ft.Icons.HOURGLASS_TOP; btn_gps.disabled = True; page.update()
            threading.Timer(12.0, gps_timeout_handler).start()
            try:
                # MUDANÇA: MEDIUM é mais rápido e funciona dentro de casa
                page.vigi_geolocator.get_current_position(accuracy=ft.GeolocatorPositionAccuracy.MEDIUM)
            except:
                try_ip_location_thread()

        # =====================================================================
        # 4. CRIAÇÃO DOS CAMPOS VISUAIS (CORREÇÃO DE LAYOUT)
        # =====================================================================
        
        tf_cep = ft.TextField(hint_text="Digite o CEP", on_change=search_cep, keyboard_type=ft.KeyboardType.NUMBER, border="none", text_size=14, content_padding=10)
        dd_municipio = ft.Dropdown(hint_text="Selecione a cidade", options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")], on_change=on_city_change, icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        dd_bairro = ft.Dropdown(hint_text="Selecione o bairro", disabled=True, icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        tf_rua = ft.TextField(hint_text="Digite o nome da rua", on_submit=search_address_by_name, border="none", text_size=14, content_padding=10)
        btn_search_rua = ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#39BFEF", tooltip="Pesquisar rua", on_click=search_address_by_name)
        tf_numero = ft.TextField(hint_text="Digite o número", border="none", text_size=14, content_padding=10)
        tf_descricao = ft.TextField(hint_text="Descreva o local", multiline=True, min_lines=3, border="none", text_size=14, content_padding=10)
        btn_gps = ft.ElevatedButton("GPS V14 (MEDIUM)", icon=ft.Icons.LOCATION_ON, bgcolor="#39BFEF", color="white", width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=get_gps_click)
        btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

        # --- MODAL DO GPS (CORRIGIDO) ---
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
                        txt_gps_source, # Usando variável direta
                        ft.Divider(),
                        ft.Text("Confira os dados abaixo:", size=14, color="grey"),
                        ft.Container(bgcolor="#F5F5F5", padding=15, border_radius=10, content=ft.Column([
                            txt_gps_rua, # Usando variável direta
                            txt_gps_bairro, # Usando variável direta
                            txt_gps_cidade # Usando variável direta
                        ], spacing=2)),
                        ft.Container(height=10),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.OutlinedButton("Cancelar", on_click=lambda e: close_gps_modal()), ft.ElevatedButton("Confirmar", bgcolor="#39BFEF", color="white", on_click=lambda e: confirm_gps_fill())])
                    ]
                )
            )
        )

        def close_gps_modal():
            gps_overlay.visible = False; btn_gps.text = "GPS V14 (MEDIUM)"; btn_gps.icon = ft.Icons.LOCATION_ON; btn_gps.disabled = False; page.update()

        # --- LISTA DE IMAGENS ---
        images_list_container = ft.Column(spacing=15)
        def remove_image(file_obj):
            if file_obj in selected_files: selected_files.remove(file_obj); update_images_display()

        def update_images_display():
            images_list_container.controls.clear()
            for file in selected_files:
                images_list_container.controls.append(ft.Row([
                    ft.Image(src=file.path, width=60, height=60, fit=ft.ImageFit.COVER, border_radius=8),
                    ft.Column([ft.Text(file.name, weight="bold"), ft.Text("Imagem", size=12)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, on_click=lambda e, f=file: remove_image(f))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
            
            images_list_container.controls.append(ft.Row([
                ft.Container(width=60, height=60, bgcolor="#E0E0E0", border_radius=8, alignment=ft.alignment.center, content=ft.Icon(ft.Icons.ADD, size=30), on_click=lambda _: page.vigi_file_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)),
                ft.Text("Adicionar imagem", size=16)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15))
            if page.views: page.update()

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

        # --- LAYOUT FINAL (SIMPLIFICADO) ---
        # Aqui removemos a complexidade de Rows dentro de Rows que quebrava o Android
        
        def back_click(e): page.go("/")
        def close_success_dialog(e): success_dialog.open = False; page.update(); back_click(None)
        
        success_dialog = ft.AlertDialog(modal=True, title=ft.Text("Sucesso!"), content=ft.Text("Foco cadastrado!"), actions=[ft.TextButton("OK", on_click=close_success_dialog)])
        
        header = ft.Container(padding=ft.padding.only(top=40, left=10, right=20, bottom=15), bgcolor="white", content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20), ft.Text("Focos V14 (Safe)", size=18, weight="bold", color="black"), ft.Container(width=40)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        
        # FUNÇÃO CREATE_ROW CORRIGIDA (SEM expand NO CONTAINER INTERNO)
        # Isso evita que o celular tente esticar o campo infinitamente e dê tela vermelha
        def create_row(label, field, extra=None): 
            content_list = [ft.Container(content=field, expand=True)]
            if extra: content_list.append(extra)
            
            return ft.Column([
                ft.Container(padding=ft.padding.symmetric(vertical=5, horizontal=20), content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                    vertical_alignment=ft.CrossAxisAlignment.CENTER, 
                    controls=[
                        ft.Container(width=100, content=ft.Text(label, style=ft.TextStyle(color="black", weight="bold", size=12))), 
                        ft.Row(content_list, expand=True) # Row interna segura
                    ]
                )), 
                ft.Divider(height=1, color="#F5F5F5")
            ], spacing=0)

        form_body = ft.Container(bgcolor="white", expand=True, content=ft.ListView(padding=ft.padding.only(bottom=30), controls=[
            ft.Container(padding=20, content=btn_gps),
            create_row("CEP", tf_cep), create_row("MUNICÍPIO", dd_municipio), create_row("BAIRRO", dd_bairro), create_row("RUA", tf_rua, btn_search_rua), create_row("NÚMERO", tf_numero), create_row("DESCRIÇÃO", tf_descricao),
            ft.Container(padding=20, content=ft.Column([ft.Text("IMAGENS", weight="bold", size=12), images_list_container])), ft.Container(padding=20, content=btn_submit),
        ]))

        return ft.View(
            route="/form-foco", 
            bgcolor="white", 
            padding=0, 
            controls=[
                ft.Stack(
                    expand=True, 
                    controls=[
                        ft.Column(expand=True, spacing=0, controls=[header, ft.Divider(height=1, color="#EEEEEE"), form_body]),
                        gps_overlay, 
                        address_overlay
                    ]
                )
            ]
        )

    except Exception as e:
        print(f"Erro ao criar tela: {e}")
        return ft.View(route="/form-foco", controls=[ft.Text(f"Erro crítico: {e}", color="red")])