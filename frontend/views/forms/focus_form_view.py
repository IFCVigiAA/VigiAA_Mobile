from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.list import OneLineListItem
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from plyer import filechooser
import requests
import threading
import unicodedata
from urllib.parse import quote
import os
import config
from plyer import gps
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission

store = JsonStore('vigiaa_storage.json')

KV_FOCUS_FORM = '''
<ImageCard@MDBoxLayout>:
    orientation: "horizontal"
    adaptive_height: True
    spacing: "10dp"
    padding: "5dp"
    image_path: ""
    image_name: ""
    
    Image:
        source: root.image_path
        size_hint: None, None
        size: "60dp", "60dp"
        allow_stretch: True
        keep_ratio: False
        
    MDBoxLayout:
        orientation: "vertical"
        pos_hint: {"center_y": .5}
        MDLabel:
            text: root.image_name
            font_style: "Caption"
            bold: True
            shorten: True
            shorten_from: "right"
        MDLabel:
            text: "Imagem"
            font_style: "Caption"
            theme_text_color: "Hint"
            
    MDIconButton:
        icon: "delete-outline"
        theme_text_color: "Error"
        pos_hint: {"center_y": .5}
        on_release: app.root.get_screen('form_foco').remove_image(root.image_path)

<FocusFormScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 0.22, 0.75, 0.94, 1
            padding: ["5dp", "0dp", "15dp", "0dp"]
            spacing: "10dp"

            MDIconButton:
                icon: "chevron-left"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": .5}
                on_release: root.go_back()

            MDLabel:
                text: "Cadastrar Foco"
                font_size: "20sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": .5}

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "15dp"
                adaptive_height: True

                # BOTÃO SEM SOMBRA ANTI-CRASH
                MDRectangleFlatIconButton:
                    id: btn_gps
                    text: "Capturar localização (GPS/Rede)"
                    icon: "map-marker"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    icon_color: 1, 1, 1, 1
                    line_color: 0.22, 0.75, 0.94, 1
                    pos_hint: {"center_x": .5}
                    radius: [8, 8, 8, 8]
                    on_release: root.start_location()

                MDLabel:
                    text: "Campos marcados com * são obrigatórios"
                    font_style: "Caption"
                    theme_text_color: "Hint"

                MDTextField:
                    id: tf_cep
                    hint_text: "CEP *"
                    input_filter: "int"
                    on_text: root.on_cep_change(self.text)

                MDTextField:
                    id: tf_city
                    hint_text: "MUNICÍPIO *"
                    readonly: True
                    on_focus: if self.focus: root.open_city_menu()

                MDTextField:
                    id: tf_neighborhood
                    hint_text: "BAIRRO *"
                    readonly: True
                    disabled: True
                    on_focus: if self.focus: root.open_neighborhood_menu()

                MDBoxLayout:
                    adaptive_height: True
                    spacing: "10dp"
                    MDTextField:
                        id: tf_street
                        hint_text: "RUA *"
                        size_hint_x: 0.8
                        on_text_validate: root.search_address_by_name()
                    MDIconButton:
                        id: btn_search_street
                        icon: "magnify"
                        theme_text_color: "Custom"
                        text_color: 0.22, 0.75, 0.94, 1
                        on_release: root.search_address_by_name()

                MDTextField:
                    id: tf_number
                    hint_text: "NÚMERO *"

                MDTextField:
                    id: tf_description
                    hint_text: "DESCRIÇÃO"
                    multiline: True

                MDLabel:
                    text: "IMAGENS"
                    bold: True
                    font_style: "Caption"

                MDBoxLayout:
                    id: images_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "10dp"

                MDFlatButton:
                    text: "+ Adicionar imagem"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.75, 0.94, 1
                    on_release: root.pick_image()

                Widget:
                    size_hint_y: None
                    height: "20dp"

                # BOTÃO SEM SOMBRA ANTI-CRASH
                MDFlatButton:
                    id: btn_submit
                    text: "CADASTRAR FOCO"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    padding: "15dp"
                    on_release: root.submit_form()
'''

Builder.load_string(KV_FOCUS_FORM)

class FocusFormScreen(MDScreen):
    neighborhoods_db = {
        "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"], 
        "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_files = []
        self.gps_address_data = {}
        self.menu_cities = None
        self.menu_neighborhoods = None
        self.gps_dialog = None
        self.manual_dialog = None
        self.success_dialog = None

    def on_pre_enter(self, *args):
        self.selected_files.clear()
        self.gps_address_data.clear()
        self.update_images_display()
        self.ids.tf_cep.text = ""
        self.ids.tf_city.text = ""
        self.ids.tf_neighborhood.text = ""
        self.ids.tf_neighborhood.disabled = True
        self.ids.tf_street.text = ""
        self.ids.tf_number.text = ""
        self.ids.tf_description.text = ""
        self.ids.btn_gps.text = "Capturar localização (GPS/Rede)"
        self.ids.btn_gps.icon = "map-marker"

    def go_back(self):
        self.manager.current = 'home'
        self.manager.get_screen('home').ids.bottom_nav.switch_tab('tab_new')

    def open_city_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": city, "on_release": lambda x=city: self.set_city(x)}
            for city in self.neighborhoods_db.keys()
        ]
        self.menu_cities = MDDropdownMenu(caller=self.ids.tf_city, items=menu_items, width_mult=4)
        self.menu_cities.open()

    def set_city(self, text_item):
        self.ids.tf_city.text = text_item
        self.ids.tf_neighborhood.disabled = False
        self.ids.tf_neighborhood.text = ""
        self.menu_cities.dismiss()

    def open_neighborhood_menu(self):
        city = self.ids.tf_city.text
        if city in self.neighborhoods_db:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": bairro, "on_release": lambda x=bairro: self.set_neighborhood(x)}
                for bairro in self.neighborhoods_db[city]
            ]
            self.menu_neighborhoods = MDDropdownMenu(caller=self.ids.tf_neighborhood, items=menu_items, width_mult=4)
            self.menu_neighborhoods.open()

    def set_neighborhood(self, text_item):
        self.ids.tf_neighborhood.text = text_item
        self.menu_neighborhoods.dismiss()

    def normalize_string(self, s):
        if not s: return ""
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

    @mainthread
    def mostrar_aviso(self, texto, cor="blue"):
        from kivymd.toast import toast
        toast(texto)

    @mainthread
    def fill_address_fields(self, data):
        city_api = data.get("localidade") or ""
        city_clean = self.normalize_string(city_api)
        target_city = None
        
        if "balneario" in city_clean and "camboriu" in city_clean: target_city = "Balneário Camboriú"
        elif "camboriu" in city_clean and "balneario" not in city_clean: target_city = "Camboriú"
        
        if target_city:
            self.ids.tf_city.text = target_city
            self.ids.tf_neighborhood.disabled = False
            if target_city in self.neighborhoods_db:
                opts = self.neighborhoods_db[target_city]
                b = data.get("bairro")
                if b:
                    if b not in opts: opts.append(b); opts.sort()
                    self.ids.tf_neighborhood.text = b
            self.ids.tf_street.text = data.get("logradouro", "")
            self.ids.tf_cep.text = data.get("cep", "").replace("-", "")
            if data.get("numero"): self.ids.tf_number.text = data.get("numero")
        else:
            self.ids.tf_city.text = ""
            self.ids.tf_neighborhood.text = ""
            self.ids.tf_neighborhood.disabled = True
            self.ids.tf_street.text = ""
            self.ids.tf_number.text = ""
            self.ids.tf_cep.text = ""
            self.mostrar_aviso(f"Serviço indisponível em {city_api}", "red")

    def on_cep_change(self, text):
        cep = text.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            threading.Thread(target=self._worker_search_cep, args=(cep,), daemon=True).start()

    def _worker_search_cep(self, cep):
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
            if "erro" not in res:
                self.fill_address_fields(res)
        except: pass

    def search_address_by_name(self):
        city = self.ids.tf_city.text
        street = self.ids.tf_street.text
        if not city or len(street) < 3:
            self.mostrar_aviso("Selecione a cidade e digite 3 letras da rua.", "orange")
            return
            
        self.ids.btn_search_street.icon = "timer-sand"
        threading.Thread(target=self._worker_search_street, args=(city, street), daemon=True).start()

    def _worker_search_street(self, city, street):
        try:
            url = f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street)}/json/"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0: 
                    Clock.schedule_once(lambda dt: self.open_manual_modal(data), 0)
                else: 
                    self.mostrar_aviso("Rua não encontrada.", "orange")
            else:
                self.mostrar_aviso(f"Erro do ViaCEP: {res.status_code}", "red")
        except Exception: 
            self.mostrar_aviso("Erro na busca da rua.", "red")
            
        Clock.schedule_once(lambda dt: self._reset_search_icon(), 0)

    @mainthread
    def _reset_search_icon(self):
        self.ids.btn_search_street.icon = "magnify"

    @mainthread
    def open_manual_modal(self, address_list):
        from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
        from kivy.uix.scrollview import ScrollView
        
        content = ScrollView(size_hint_y=None, height=dp(300))
        box = MDBoxLayout(orientation='vertical', adaptive_height=True)
        for addr in address_list:
            item = TwoLineIconListItem(
                text=addr.get("logradouro", ""),
                secondary_text=f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}",
                on_release=lambda x, a=addr: self.select_address_manual(a)
            )
            item.add_widget(IconLeftWidget(icon="map-marker"))
            box.add_widget(item)
        content.add_widget(box)

        self.manual_dialog = MDDialog(
            title="Selecione a Rua",
            type="custom",
            content_cls=content,
            buttons=[MDFlatButton(text="Fechar", radius=[8, 8, 8, 8], on_release=lambda x: self.manual_dialog.dismiss())]
        )
        self.manual_dialog.open()

    def select_address_manual(self, addr_data):
        if self.manual_dialog: self.manual_dialog.dismiss()
        self.fill_address_fields(addr_data)

    def start_location(self):
        self.ids.btn_gps.text = "Pedindo permissão..."
        self.ids.btn_gps.icon = "crosshairs-gps"
        self.ids.btn_gps.disabled = True

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], self._on_permissions_result)
        else:
            # Teste no PC: Usando IP aproximado instantâneo
            threading.Thread(target=self._worker_ip_location, daemon=True).start()

    def _on_permissions_result(self, permissions, grants):
        if all(grants):
            try:
                gps.configure(on_location=self._on_gps_location, on_status=self._on_gps_status)
                
                # 1. Ligamos a Antena Nativa (Fino)
                gps.start(minTime=1000, minDistance=1) 
                self.ids.btn_gps.text = "Conectando ao Satélite..."
                
                # 2. THE FIX: Ligamos o cronômetro de paciência curta (3 segundos)
                # Se o satélite demorar, nós fugimos para o "Fused Simulation" (Rede)
                Clock.schedule_once(self._gps_escape_fused, 3)
                
            except Exception as e:
                self.mostrar_aviso(f"Erro no sensor: {e}")
                self._reset_gps_btn()
        else:
            self.mostrar_aviso("Você precisa permitir o uso do GPS!")
            self._reset_gps_btn()
    
    @mainthread
    def _gps_escape_fused(self, dt):
        # 3. Escape Hatch (Fuga para a Memória/Rede)
        # Se depois de 3 longos segundos ele não achar NADA, aí sim ele desiste do satélite puro.
        if self.ids.btn_gps.text == "Conectando ao Satélite...":
            
            # Muda o texto para avisar o usuário
            self.ids.btn_gps.text = "A buscar rede rápida..."
            self.mostrar_aviso("Satélites demorando. Buscando localização aproximada...")
            
            # Aciona a função de IP que é instantânea (Pega "da memória" do OpenStreetMap via IP)
            threading.Thread(target=self._worker_ip_location, daemon=True).start()

    @mainthread
    def _on_gps_location(self, **kwargs):
        # 4. GPS Nativo ACHOU! (PRECISÃO MÁXIMA)
        # Se o satélite puro responder antes dos 3 segundos ou se responder depois, cancelamos Plan B.
        Clock.unschedule(self._gps_escape_fused) # Impede o Plan B de rodar
        gps.stop() 
        
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        
        self.ids.btn_gps.text = "Coordenada Capturada!"
        self.ids.btn_gps.icon = "check"
        
        # Manda direto pro seu tradutor de ruas que preenche os campos
        threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Satélite GPS Nativo"), daemon=True).start()

    @mainthread
    def _on_gps_status(self, stype, status):
        pass
        

    def _worker_ip_location(self):
        try:
            res = requests.get("http://ip-api.com/json/", timeout=5)
            if res.status_code == 200:
                data = res.json()
                self._worker_get_address_from_coords(data.get('lat'), data.get('lon'), "Internet (Aproximado)")
                return
        except: pass
        self.mostrar_aviso("Erro de conexão.", "red")
        Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    def _worker_get_address_from_coords(self, lat, lon, source="Rede"):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            res = requests.get(url, headers={'User-Agent': 'VigiAA/1.0'}).json()
            addr = res.get("address", {})
            self.gps_address_data.clear()
            self.gps_address_data["lat"] = str(lat)
            self.gps_address_data["lon"] = str(lon) 
            self.gps_address_data["localidade"] = addr.get("city") or addr.get("town") or addr.get("municipality")
            self.gps_address_data["bairro"] = addr.get("suburb") or addr.get("neighbourhood")
            self.gps_address_data["logradouro"] = addr.get("road")
            self.gps_address_data["cep"] = addr.get("postcode")
            self.gps_address_data["numero"] = addr.get("house_number")
            Clock.schedule_once(lambda dt: self.open_gps_modal(source), 0)
        except:
            self.mostrar_aviso("Erro ao traduzir endereço.", "red")
            Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    @mainthread
    def _reset_gps_btn(self): 
        self.ids.btn_gps.text = "Capturar localização (GPS/Rede)"
        self.ids.btn_gps.icon = "map-marker"
        self.ids.btn_gps.disabled = False

    @mainthread
    def open_gps_modal(self, source):
        self.ids.btn_gps.text = "Localização Encontrada!"
        self.ids.btn_gps.icon = "check"
        self.ids.btn_gps.disabled = False
        
        rua = self.gps_address_data.get("logradouro") or "Rua não detectada"
        bairro = self.gps_address_data.get("bairro") or "Bairro não detectado"
        cidade = self.gps_address_data.get("localidade") or "Cidade não detectada"
        texto_dialog = f"[b]Rua:[/b] {rua}\n[b]Bairro:[/b] {bairro}\n[b]Cidade:[/b] {cidade}\n\n[i]Fonte: {source}[/i]"
        
        self.gps_dialog = MDDialog(
            title="Confirme os Dados:",
            text=texto_dialog,
            buttons=[
                MDFlatButton(text="Cancelar", text_color=(1,0,0,1), radius=[8, 8, 8, 8], on_release=lambda x: self.gps_dialog.dismiss()),
                MDFlatButton(text="Confirmar", text_color=(1,1,1,1), md_bg_color=(0.22, 0.75, 0.94, 1), radius=[8, 8, 8, 8], on_release=self.confirm_gps_fill)
            ]
        )
        self.gps_dialog.open()

    def confirm_gps_fill(self, instance):
        self.gps_dialog.dismiss()
        self.fill_address_fields(self.gps_address_data)

    def pick_image(self):
        try:
            filechooser.open_file(on_selection=self._handle_selection, filters=[("Images", "*.png", "*.jpg", "*.jpeg")])
        except Exception as e:
            self.mostrar_aviso("Permissão de galeria negada ou indisponível.", "red")

    def _handle_selection(self, selection):
        if selection:
            for path in selection:
                if path not in self.selected_files:
                    self.selected_files.append(path)
            Clock.schedule_once(lambda dt: self.update_images_display(), 0)

    def remove_image(self, path):
        if path in self.selected_files:
            self.selected_files.remove(path)
            self.update_images_display()

    @mainthread
    def update_images_display(self):
        self.ids.images_container.clear_widgets()
        for path in self.selected_files:
            nome_arquivo = os.path.basename(path)
            card = Builder.template('ImageCard', image_path=path, image_name=nome_arquivo)
            self.ids.images_container.add_widget(card)

    def submit_form(self):
        if not store.exists("session"):
            self.manager.current = 'login'
            return
            
        token = store.get("session")["token"]
        cidade = self.ids.tf_city.text
        bairro = self.ids.tf_neighborhood.text
        rua = self.ids.tf_street.text
        numero = self.ids.tf_number.text
        
        if not all([cidade, bairro, rua, numero]):
            self.mostrar_aviso("Preencha os campos obrigatórios (*)", "red")
            return
            
        self.ids.btn_submit.text = "Enviando..."
        self.ids.btn_submit.disabled = True
        threading.Thread(target=self._worker_submit, args=(token,), daemon=True).start()

    def _worker_submit(self, token):
        try:
            data = {
                "cep": self.ids.tf_cep.text, 
                "city": self.ids.tf_city.text, 
                "neighborhood": self.ids.tf_neighborhood.text, 
                "street": self.ids.tf_street.text, 
                "number": self.ids.tf_number.text, 
                "description": self.ids.tf_description.text, 
                "latitude": self.gps_address_data.get("lat", "-27.000"), 
                "longitude": self.gps_address_data.get("lon", "-48.000")
            }
            
            files = []
            file_handles = []
            for path in self.selected_files:
                f = open(path, 'rb')
                file_handles.append(f)
                files.append(('uploaded_images', (os.path.basename(path), f, 'image/jpeg')))
                
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{config.API_URL}/api/report-focus/", data=data, files=files, headers=headers)
            
            for f in file_handles: f.close()
            
            if res.status_code in [200, 201]: 
                Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else: 
                self.mostrar_aviso(f"Erro no servidor. Código: {res.status_code}", "red")
                
        except Exception as ex: 
            self.mostrar_aviso("Erro de comunicação com o sistema.", "red")
            
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "CADASTRAR FOCO"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        self.success_dialog = MDDialog(
            title="Sucesso!",
            text="Foco de dengue cadastrado com sucesso!",
            buttons=[
                MDFlatButton(text="OK", text_color=(1,1,1,1), md_bg_color=(0, 0.7, 0, 1), radius=[8, 8, 8, 8], on_release=self.close_success_modal)
            ]
        )
        self.success_dialog.open()

    def close_success_modal(self, instance):
        self.success_dialog.dismiss()
        self.go_back()