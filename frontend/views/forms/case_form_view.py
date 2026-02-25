import flet as ft
import requests
import config
from urllib.parse import quote
import unicodedata
import datetime
import threading

def create_case_form_view(page: ft.Page):
    try:
        API_URL = config.API_URL
        gps_address_data = {} 
        
        txt_gps_rua = ft.Text(value="Carregando...", weight="bold", color="black", size=14)
        txt_gps_bairro = ft.Text(value="...", size=13, color="black")
        txt_gps_cidade = ft.Text(value="...", size=12, color="grey")
        txt_gps_source = ft.Text(value="...", size=10, color="grey")
        
        btn_gps = ft.ElevatedButton("Capturar localização (Rede)", icon=ft.Icons.WIFI, bgcolor="#39BFEF", color="white", width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
        btn_submit = ft.ElevatedButton("CADASTRAR", bgcolor="#39BFEF", color="white", width=float("inf"), height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

        gps_overlay = ft.Container(visible=False) 
        address_overlay = ft.Container(visible=False)

        def normalize_string(s):
            if not s: return ""
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

        neighborhoods_db = {"Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"], "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]}

        tf_cep = ft.TextField(hint_text="Digite o CEP", keyboard_type=ft.KeyboardType.NUMBER, border="none", text_size=14, content_padding=10)
        dd_municipio = ft.Dropdown(hint_text="Selecione a cidade", options=[ft.dropdown.Option("Camboriú"), ft.dropdown.Option("Balneário Camboriú")], icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        dd_bairro = ft.Dropdown(hint_text="Selecione o bairro", disabled=True, icon=ft.Icons.KEYBOARD_ARROW_DOWN, border="none", text_size=14, content_padding=10)
        btn_search_inline = ft.IconButton(icon=ft.Icons.SEARCH, icon_color="#39BFEF", tooltip="Pesquisar rua")
        tf_rua = ft.TextField(hint_text="Selecione a rua", border="none", text_size=14, content_padding=10, suffix=btn_search_inline)
        tf_numero = ft.TextField(hint_text="Digite o número", border="none", text_size=14, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)

        dias = [ft.dropdown.Option(str(i)) for i in range(1, 32)]
        meses = [ft.dropdown.Option(m) for m in ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]]
        anos_nasc = [ft.dropdown.Option(str(i)) for i in range(datetime.date.today().year, 1920, -1)]
        anos_notif = [ft.dropdown.Option(str(datetime.date.today().year)), ft.dropdown.Option(str(datetime.date.today().year - 1))]

        # Trocamos o Width pelo Expand
        estilo_data = {"border_color": "#E0E0E0", "border_radius": 12, "content_padding": 5, "text_size": 13, "expand": 1}
        
        dd_notif_dia = ft.Dropdown(options=dias, hint_text="Dia", **estilo_data)
        dd_notif_mes = ft.Dropdown(options=meses, hint_text="Mês", **estilo_data)
        dd_notif_ano = ft.Dropdown(options=anos_notif, hint_text="Ano", **estilo_data)
        row_data_notif = ft.Row([dd_notif_dia, dd_notif_mes, dd_notif_ano], spacing=5)

        dd_nasc_dia = ft.Dropdown(options=dias, hint_text="Dia", **estilo_data)
        dd_nasc_mes = ft.Dropdown(options=meses, hint_text="Mês", **estilo_data)
        dd_nasc_ano = ft.Dropdown(options=anos_nasc, hint_text="Ano", **estilo_data)
        row_data_nasc = ft.Row([dd_nasc_dia, dd_nasc_mes, dd_nasc_ano], spacing=5)

        rg_teste = ft.RadioGroup(content=ft.Row([ft.Radio(value="sim", label="Sim", active_color="black"), ft.Radio(value="nao", label="Não", active_color="black")]))

        def fill_address_fields(data):
            city_api = data.get("localidade") or ""
            city_clean = normalize_string(city_api)
            target_city = "Balneário Camboriú" if "balneario" in city_clean and "camboriu" in city_clean else "Camboriú" if "camboriu" in city_clean else None
            if target_city:
                dd_municipio.value = target_city
                dd_bairro.disabled = False
                if target_city in neighborhoods_db:
                    opts = neighborhoods_db[target_city] 
                    b = data.get("bairro")
                    if b and b not in opts: opts.append(b); opts.sort()
                    if b: dd_bairro.value = b
                    dd_bairro.options = [ft.dropdown.Option(o) for o in opts]
                tf_rua.value = data.get("logradouro")
                tf_cep.value = data.get("cep")
            page.update()

        def on_city_change(e):
            if dd_municipio.value in neighborhoods_db: 
                dd_bairro.options = [ft.dropdown.Option(b) for b in neighborhoods_db[dd_municipio.value]]
                dd_bairro.disabled = False
            else: dd_bairro.disabled = True
            page.update()
        dd_municipio.on_change = on_city_change

        def search_cep(e):
            cep = tf_cep.value.replace("-", "").replace(".", "").strip()
            if len(cep) == 8:
                try:
                    res = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5).json()
                    if "erro" not in res: fill_address_fields(res)
                except: pass
        tf_cep.on_change = search_cep

        def search_address_by_name(e=None):
            city = dd_municipio.value
            street = tf_rua.value
            if not city or not street or len(street) < 3: return
            tf_rua.suffix = ft.Container(content=ft.ProgressRing(width=20, height=20, stroke_width=2), padding=10); page.update()
            try:
                url = f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street)}/json/"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list) and len(data) > 0: open_manual_modal(data)
            except: pass
            tf_rua.suffix = btn_search_inline; page.update()

        btn_search_inline.on_click = search_address_by_name
        tf_rua.on_submit = search_address_by_name

        def run_ip_location():
            btn_gps.text = "Buscando..."; btn_gps.icon = ft.Icons.HOURGLASS_TOP; btn_gps.disabled = True; page.update()
            try:
                res = requests.get("http://ip-api.com/json/", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    get_address_from_coords(data.get('lat'), data.get('lon'), source="Internet (Aproximado)")
            except: 
                page.open(ft.SnackBar(ft.Text("Erro de conexão."), bgcolor="red"))
                btn_gps.text = "Capturar localização (Rede)"; btn_gps.icon = ft.Icons.WIFI; btn_gps.disabled = False; page.update()

        def get_address_from_coords(lat, lon, source="Rede"):
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
                
                txt_gps_rua.value = gps_address_data["logradouro"] or "Rua não detectada"
                txt_gps_bairro.value = gps_address_data["bairro"] or "Bairro não detectado"
                txt_gps_cidade.value = gps_address_data["localidade"] or "Cidade não detectada"
                txt_gps_source.value = f"Fonte: {source}"
                
                gps_overlay.visible = True
                btn_gps.text = "Localização Encontrada!"; btn_gps.icon = ft.Icons.CHECK; btn_gps.disabled = False; page.update()
            except:
                page.open(ft.SnackBar(ft.Text("Erro ao traduzir endereço."), bgcolor="red"))
                btn_gps.text = "Capturar localização (Rede)"; btn_gps.icon = ft.Icons.WIFI; btn_gps.disabled = False; page.update()

        btn_gps.on_click = lambda e: threading.Thread(target=run_ip_location).start()

        def close_gps_modal(e=None): gps_overlay.visible = False; btn_gps.text = "Capturar localização (Rede)"; btn_gps.icon = ft.Icons.WIFI; btn_gps.disabled = False; page.update()
        def confirm_gps_fill(e=None): fill_address_fields(gps_address_data); close_gps_modal()

        gps_overlay = ft.Container(visible=False, bgcolor="#80000000", alignment=ft.alignment.center, expand=True, content=ft.Container(width=320, bgcolor="white", border_radius=20, padding=25, shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color="#4D000000"), content=ft.Column(alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, height=350, controls=[ft.Icon(ft.Icons.MAP_SHARP, color="#39BFEF", size=50), ft.Text("Localização Encontrada!", size=20, weight="bold", color="#39BFEF"), txt_gps_source, ft.Divider(), ft.Text("Confira os dados abaixo:", size=14, color="grey"), ft.Container(bgcolor="#F5F5F5", padding=15, border_radius=10, content=ft.Column([txt_gps_rua, txt_gps_bairro, txt_gps_cidade], spacing=2)), ft.Container(height=10), ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.OutlinedButton("Cancelar", on_click=close_gps_modal), ft.ElevatedButton("Confirmar", bgcolor="#39BFEF", color="white", on_click=confirm_gps_fill)])])))
        
        overlay_list_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        def close_manual_modal(e): address_overlay.visible = False; page.update()
        def select_address_manual(addr_data): address_overlay.visible = False; page.update(); fill_address_fields(addr_data)

        address_overlay = ft.Container(visible=False, bgcolor="#80000000", alignment=ft.alignment.center, expand=True, content=ft.Container(width=320, height=500, bgcolor="white", border_radius=20, padding=20, content=ft.Column(controls=[ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("Selecione a Rua", size=18, weight="bold", color="#39BFEF"), ft.Icon(ft.Icons.LOCATION_CITY, color="#39BFEF")]), ft.Divider(height=1, color="#EEEEEE"), ft.Container(content=overlay_list_content, expand=True), ft.ElevatedButton("Fechar", bgcolor="#39BFEF", color="white", width=float("inf"), on_click=close_manual_modal)])))

        def open_manual_modal(address_list):
            overlay_list_content.controls.clear()
            overlay_list_content.controls.append(ft.Text(f"{len(address_list)} ruas encontradas:", size=12, color="grey"))
            for addr in address_list: overlay_list_content.controls.append(ft.Container(padding=10, content=ft.Row([ft.Icon(ft.Icons.PLACE, size=16), ft.Column([ft.Text(addr.get("logradouro", ""), weight="bold"), ft.Text(f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}", size=12)])]), on_click=lambda e, a=addr: select_address_manual(a), ink=True))
            address_overlay.visible = True; page.update()

        def close_success_dialog(e):
            try: page.close(success_dialog)
            except: pass
            page.go("/novo") 

        success_dialog = ft.AlertDialog(modal=True, title=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=30), ft.Text("Sucesso!")]), content=ft.Text("Caso de dengue cadastrado!"), actions=[ft.TextButton("OK", on_click=close_success_dialog)])

        def confirm_positive_and_submit(e):
            try: page.close(aviso_identificacao_dialog)
            except: pass
            execute_submit(is_positive=True)

        aviso_identificacao_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.WARNING, color="black"), ft.Text("Aviso", weight="bold")]),
            content=ft.Text("Nos casos de teste positivo o\npaciente deve ser identificado.", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton("Ok", bgcolor="#39BFEF", color="white", width=150, on_click=confirm_positive_and_submit)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )

        def pre_submit_check(e):
            if not all([tf_cep.value, dd_municipio.value, dd_bairro.value, tf_rua.value, tf_numero.value, rg_teste.value, dd_notif_dia.value, dd_nasc_dia.value]): 
                page.open(ft.SnackBar(ft.Text("Preencha todos os campos obrigatórios (*)!"), bgcolor="red"))
                return
            
            if rg_teste.value == "sim":
                page.open(aviso_identificacao_dialog)
            else:
                execute_submit(is_positive=False)

        def execute_submit(is_positive):
            token = page.client_storage.get("token")
            btn_submit.text = "Enviando..."; btn_submit.disabled = True; page.update()
            
            data_notif = f"{int(dd_notif_dia.value):02d}/{meses.index(next(m for m in meses if m.key == dd_notif_mes.value))+1:02d}/{dd_notif_ano.value}"
            data_nasc = f"{int(dd_nasc_dia.value):02d}/{meses.index(next(m for m in meses if m.key == dd_nasc_mes.value))+1:02d}/{dd_nasc_ano.value}"
            
            try:
                data = {
                    "notification_date": data_notif,
                    "cep": tf_cep.value,
                    "city": dd_municipio.value,
                    "neighborhood": dd_bairro.value,
                    "street": tf_rua.value,
                    "number": tf_numero.value,
                    "birth_date": data_nasc,
                    "positive_test": is_positive
                }
                headers = {"Authorization": f"Bearer {token}"}
                res = requests.post(f"{API_URL}/api/report-case/", json=data, headers=headers)
                
                if res.status_code in [200, 201]: 
                    case_data = res.json()
                    case_id = case_data.get('id')
                    
                    if is_positive:
                        page.session.set("current_case_id", case_id)
                        page.go("/form-caso-positivo")
                    else:
                        try: page.open(success_dialog)
                        except: page.dialog = success_dialog; success_dialog.open = True; page.update()
                
                # BLINDAGEM CONTRA TELA VERMELHA
                else: 
                    page.open(ft.SnackBar(ft.Text(f"Erro no servidor. Código: {res.status_code}"), bgcolor="red"))
                    
            except Exception as ex: 
                # BLINDAGEM CONTRA TELA VERMELHA
                page.open(ft.SnackBar(ft.Text("Erro de comunicação com o sistema."), bgcolor="red"))
                
            btn_submit.text = "CADASTRAR"; btn_submit.disabled = False; page.update()

        btn_submit.on_click = pre_submit_check

        def back_click(e): 
            page.go("/novo")
                
        header = ft.Container(padding=ft.padding.only(top=40, left=10, right=20, bottom=15), bgcolor="white", content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=back_click, icon_size=20), ft.Text("Casos de dengue", size=18, weight="bold", color="black"), ft.Container(width=40)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        
        def create_row(label, field, obrigatorio=True): 
            label_controls = [ft.Text(label, style=ft.TextStyle(color="black", weight="bold", size=12))]
            if obrigatorio: label_controls.append(ft.Text(" *", color="red", weight="bold", size=14))
            return ft.Column([ft.Container(padding=ft.padding.symmetric(vertical=5, horizontal=20), content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(width=120, content=ft.Row(label_controls, spacing=0)), ft.Row([ft.Container(content=field, expand=True)], expand=True)])), ft.Divider(height=1, color="#F5F5F5")], spacing=0)

        caixa_aviso = ft.Container(
            margin=ft.padding.symmetric(horizontal=20, vertical=10),
            padding=15,
            border=ft.border.all(1, "#BDBDBD"),
            border_radius=8,
            bgcolor="#F5F5F5",
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="grey"), ft.Text("Aviso", weight="bold", color="grey")], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("Nosso objetivo é registrar a ocorrência de casos de dengue.\n\nNão identificamos o paciente.", text_align=ft.TextAlign.CENTER, color="grey", size=13)
                ]
            )
        )

        form_body = ft.Container(bgcolor="white", expand=True, content=ft.ListView(padding=ft.padding.only(bottom=30), controls=[
            ft.Container(padding=20, content=btn_gps),
            ft.Container(padding=ft.padding.only(left=20, bottom=10), content=ft.Text("Campos marcados com * são obrigatórios", size=10, color="black")),
            create_row("Data da notificação", row_data_notif), 
            create_row("CEP", tf_cep), 
            create_row("MUNICÍPIO", dd_municipio), 
            create_row("BAIRRO", dd_bairro), 
            create_row("RUA", tf_rua), 
            create_row("NÚMERO", tf_numero), 
            create_row("Data de nascimento", row_data_nasc),
            create_row("Teste positivo", rg_teste),
            caixa_aviso,
            ft.Container(padding=20, content=btn_submit),
        ]))

        return ft.View(
            route="/form-caso", 
            bgcolor="white", 
            padding=0, 
            controls=[
                ft.Stack(expand=True, controls=[
                    ft.Column(expand=True, spacing=0, controls=[header, ft.Divider(height=1, color="#EEEEEE"), form_body]), 
                    gps_overlay, 
                    address_overlay
                ])
            ]
        )

    except Exception as e:
        print(f"Erro ao criar tela: {e}")
        return ft.View(route="/form-caso", controls=[ft.Text(f"Erro crítico da tela.", color="red")])