from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp
from kivymd.toast import toast
import requests
import threading
import unicodedata
from urllib.parse import quote
import config
from plyer import gps
from kivy.utils import platform
import time
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.utils import platform

from kivy.properties import VariableListProperty
from kivymd.uix.button import MDFlatButton, MDTextButton

# Injetamos o 'radius' à força nos botões base se eles não tiverem
if not hasattr(MDFlatButton, 'radius'):
    MDFlatButton.radius = VariableListProperty([16, 16, 16, 16])
if not hasattr(MDTextButton, 'radius'):
    MDTextButton.radius = VariableListProperty([16, 16, 16, 16])

# Tentamos injetar diretamente na classe secreta de anos do Calendário
try:
    from kivymd.uix.pickers.datepicker.datepicker import MDDatePickerItemText
    if not hasattr(MDDatePickerItemText, 'radius'):
        MDDatePickerItemText.radius = VariableListProperty([16, 16, 16, 16])
except ImportError:
    pass

store = JsonStore('sessao_app.json')

if platform == 'android':
    from android.permissions import request_permissions, Permission

store = JsonStore('sessao_app.json')

KV_CASE_FORM = '''
<CaseFormScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # --- Top Bar (Fundo branco, texto e ícone pretos centralizados) ---
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            padding: ["10dp", "0dp", "10dp", "0dp"]
            spacing: "10dp"
            
            canvas.after:
                Color:
                    rgb: 0.9, 0.9, 0.9
                Line:
                    points: self.x, self.y, self.width, self.y
                    width: 1.1

            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                pos_hint: {"center_y": .5}
                on_release: root.go_back()

            MDLabel:
                text: "Casos de dengue"
                font_size: "20sp"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                pos_hint: {"center_y": .5}

            Widget:
                size_hint_x: None
                width: "48dp"

        # --- Corpo do Formulário ---
        # TROCAMOS PARA MDScrollView PARA EVITAR O ERRO 'on_scroll_stop'
        MDScrollView:
            id: scroller
            MDBoxLayout:
                orientation: "vertical"
                padding: ["20dp", "20dp", "20dp", "20dp"]
                spacing: "5dp"
                adaptive_height: True

                # --- Botão GPS ---
                MDFillRoundFlatIconButton:
                    id: btn_gps
                    text: "Capturar localização pelo GPS"
                    icon: "map-marker-outline"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    icon_color: 1, 1, 1, 1
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.9
                    radius: [15, 15, 15, 15]
                    on_release: root.start_location()

                MDLabel:
                    text: "Campos marcados com * são obrigatórios"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)

                # --- FORM ROWS (Estilo Tabela) ---

                # Data da notificação
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Data da notificação[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp" # Aumentado para o * caber perfeitamente
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_notif_date
                        hint_text: "Selecione a data"
                        readonly: True
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.show_date_picker('notif')
                    MDIconButton:
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.show_date_picker('notif')

                # CEP
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "CEP"
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_cep
                        hint_text: "Digite o CEP"
                        input_filter: "int"
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_text: root.on_cep_change(self.text)

                # Município
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "MUNICÍPIO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_city
                        hint_text: "Selecione o nome da cidade"
                        readonly: True
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_city_menu()
                    MDIconButton:
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.open_city_menu()

                # Bairro
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "BAIRRO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_neighborhood
                        hint_text: "Selecione o nome do bairro"
                        readonly: True
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_neighborhood_menu()
                    MDIconButton:
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.open_neighborhood_menu()

                # Rua
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "RUA[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_street
                        hint_text: "Selecione o nome da rua"
                        multiline: False
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_text_validate: root.search_address_by_name()
                    MDIconButton:
                        id: btn_search_street
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.search_address_by_name()

                # Número
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "NÚMERO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_number
                        hint_text: "Digite o número"
                        input_filter: "int"
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]

                # Data de nascimento
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Data de nasc.[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_birth_date
                        hint_text: "Selecione a data"
                        readonly: True
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.show_date_picker('birth')
                    MDIconButton:
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.show_date_picker('birth')

                # Teste positivo (Checkboxes alinhados)
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Teste positivo[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "160dp"
                        theme_text_color: "Primary"
                    MDBoxLayout:
                        adaptive_height: True
                        pos_hint: {"center_y": .5}
                        spacing: "0dp"
                        MDCheckbox:
                            id: chk_sim
                            group: 'teste'
                            size_hint: None, None
                            size: "40dp", "40dp"
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "Sim"
                            adaptive_width: True
                            pos_hint: {"center_y": .5}
                        Widget:
                            size_hint_x: None
                            width: "20dp"
                        MDCheckbox:
                            id: chk_nao
                            group: 'teste'
                            size_hint: None, None
                            size: "40dp", "40dp"
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "Não"
                            adaptive_width: True
                            pos_hint: {"center_y": .5}
                            
                # O ESPAÇADOR VITAL PARA O BOTÃO NÃO TAMPAR O FINAL
                Widget:
                    size_hint_y: None
                    height: "100dp"

        # --- Botão CADASTRAR fixo no rodapé ---
        AnchorLayout:
            anchor_x: "center"
            anchor_y: "bottom"
            size_hint_y: None  # <-- A CORREÇÃO MÁGICA DO QUADRADO BRANCO
            height: "80dp"
            padding: ["15dp", "0dp", "15dp", "15dp"]

            MDFillRoundFlatButton:
                id: btn_submit
                text: "CADASTRAR"
                font_size: "18sp"
                bold: True
                md_bg_color: 0.22, 0.75, 0.94, 1
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_x: 1
                height: "56dp"
                radius: [15, 15, 15, 15]
                on_release: root.pre_submit_check()
'''

Builder.load_string(KV_CASE_FORM)

class CaseFormScreen(MDScreen):
    neighborhoods_db = {
        "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"], 
        "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps_address_data = {}
        self.menu_cities = None
        self.menu_neighborhoods = None
        self.gps_dialog = None
        self.manual_dialog = None
        self.success_dialog = None
        self.warning_dialog = None

    def on_pre_enter(self, *args):
        self.gps_address_data.clear()
        self.ids.tf_notif_date.text = ""
        self.ids.tf_birth_date.text = ""
        self.ids.tf_cep.text = ""
        self.ids.tf_city.text = ""
        self.ids.tf_neighborhood.text = ""
        self.ids.tf_neighborhood.disabled = True
        self.ids.tf_street.text = ""
        self.ids.tf_number.text = ""
        self.ids.chk_sim.active = False
        self.ids.chk_nao.active = False
        self.ids.btn_gps.text = "Capturar localização (GPS/Rede)"
        self.ids.btn_gps.icon = "map-marker"

    def go_back(self):
        self.manager.current = 'home'
        self.manager.get_screen('home').ids.bottom_nav.switch_tab('tab_new')

    def show_date_picker(self, field_type):
        date_dialog = MDDatePicker()
        if field_type == 'notif': date_dialog.bind(on_save=self.on_save_notif)
        else: date_dialog.bind(on_save=self.on_save_birth)
        date_dialog.open()

    def on_save_notif(self, instance, value, date_range): self.ids.tf_notif_date.text = value.strftime("%d/%m/%Y")
    def on_save_birth(self, instance, value, date_range): self.ids.tf_birth_date.text = value.strftime("%d/%m/%Y")

    def open_city_menu(self):
        menu_items = [{"viewclass": "OneLineListItem", "text": city, "on_release": lambda x=city: self.set_city(x)} for city in self.neighborhoods_db.keys()]
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
            menu_items = [{"viewclass": "OneLineListItem", "text": bairro, "on_release": lambda x=bairro: self.set_neighborhood(x)} for bairro in self.neighborhoods_db[city]]
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
        toast(texto)

    @mainthread
    def fill_address_fields(self, data):
        city_api = data.get("localidade") or ""
        city_clean = self.normalize_string(city_api)
        target_city = "Balneário Camboriú" if "balneario" in city_clean and "camboriu" in city_clean else "Camboriú" if "camboriu" in city_clean else None
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
            self.ids.tf_city.text = ""; self.ids.tf_neighborhood.text = ""; self.ids.tf_neighborhood.disabled = True
            self.ids.tf_street.text = ""; self.ids.tf_number.text = ""; self.ids.tf_cep.text = ""
            self.mostrar_aviso(f"Serviço indisponível em {city_api}")

    def on_cep_change(self, text):
        cep = text.replace("-", "").replace(".", "").strip()
        if len(cep) == 8: threading.Thread(target=self._worker_search_cep, args=(cep,), daemon=True).start()

    def _worker_search_cep(self, cep):
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
            if "erro" not in res: self.fill_address_fields(res)
        except: pass

    def search_address_by_name(self):
        city = self.ids.tf_city.text
        # O .strip() remove qualquer "Enter" ou espaço em branco escondido no início ou fim!
        street = self.ids.tf_street.text.strip() 
        
        if not city or len(street) < 3: return
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
                else: self.mostrar_aviso("Rua não encontrada.")
            else: self.mostrar_aviso(f"Erro do ViaCEP: {res.status_code}")
        except Exception: self.mostrar_aviso("Erro na busca.")
        Clock.schedule_once(lambda dt: self._reset_search_icon(), 0)

    @mainthread
    def _reset_search_icon(self): self.ids.btn_search_street.icon = "magnify"

    @mainthread
    def open_manual_modal(self, address_list):
        from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
        from kivy.uix.scrollview import ScrollView
        from kivymd.uix.boxlayout import MDBoxLayout # <-- A vacina contra o NameError aqui!
        
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
            buttons=[
                MDFlatButton(
                    text="Fechar", 
                    theme_text_color="Custom",
                    text_color=(0.22, 0.75, 0.94, 1), # Deixei azulzinho para combinar com seu app!
                    on_release=lambda x: self.manual_dialog.dismiss()
                )
            ]
        )
        self.manual_dialog.open()

    def select_address_manual(self, addr_data):
        if self.manual_dialog: self.manual_dialog.dismiss()
        self.fill_address_fields(addr_data)

# -------------------------------------------------------------
    # LÓGICA DE GPS (IDÊNTICA AO FORMULÁRIO DE FOCOS - COM PYJNIUS)
    # -------------------------------------------------------------
    
    def start_location(self):
        self.ids.btn_gps.text = "Pedindo permissão..."
        self.ids.btn_gps.icon = "crosshairs-gps"
        self.ids.btn_gps.disabled = True

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], self._on_permissions_result)
        else:
            self.mostrar_aviso("Teste no PC: Usando IP.")
            threading.Thread(target=self._worker_ip_location, daemon=True).start()

    def _on_permissions_result(self, permissions, grants):
        if all(grants):
            try:
                gps.configure(on_location=self._on_gps_location, on_status=self._on_gps_status)
                gps.start(minTime=1000, minDistance=1) 
                
                self.gps_tempo = 40 
                self.ids.btn_gps.text = f"Buscando satélite ({self.gps_tempo}s)..."
                
                self.gps_event = Clock.schedule_interval(self._gps_countdown, 1)
                
            except Exception as e:
                self.mostrar_aviso(f"Erro no sensor: {e}")
                self._reset_gps_btn()
        else:
            self.mostrar_aviso("Você precisa permitir o uso do GPS!")
            self._reset_gps_btn()

    @mainthread
    def _gps_countdown(self, dt):
        self.gps_tempo -= 1
        if self.gps_tempo > 0:
            self.ids.btn_gps.text = f"Buscando satélite ({self.gps_tempo}s)..."
        else:
            self.gps_event.cancel()
            self._gps_escape_memory(None)

    @mainthread
    def _gps_escape_memory(self, dt):
        if self.ids.btn_gps.text.startswith("Buscando"):
            gps.stop() 
            self.ids.btn_gps.text = "Lendo memória do celular..."
            
            # THE MAGIC: Pega da memória cruzada (Rede/Antenas da rua)
            lat, lon = self._get_last_known_location_android()
            
            if lat and lon:
                self.ids.btn_gps.text = "Coordenada da Memória!"
                self.ids.btn_gps.icon = "check"
                self.mostrar_aviso("Usando localização nativa da rede.")
                threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Memória do Android"), daemon=True).start()
            else:
                self.mostrar_aviso("Memória vazia. Tente ir para um local mais aberto.", "red")
                self._reset_gps_btn()

    def _get_last_known_location_android(self):
        try:
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            LocationManager = autoclass('android.location.LocationManager')
            
            activity = PythonActivity.mActivity
            lm = activity.getSystemService(Context.LOCATION_SERVICE)
            
            loc = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
            if not loc:
                loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)
                
            if loc:
                return loc.getLatitude(), loc.getLongitude()
        except Exception as e:
            print("Erro ao acessar memória do GPS:", e)
            
        return None, None

    @mainthread
    def _on_gps_location(self, **kwargs):
        if hasattr(self, 'gps_event'):
            self.gps_event.cancel()
            
        gps.stop() 
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        
        self.ids.btn_gps.text = "Coordenada Capturada!"
        self.ids.btn_gps.icon = "check"
        
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
        self.mostrar_aviso("Erro de conexão.")
        Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    def _worker_get_address_from_coords(self, lat, lon, source="Rede"):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            res = requests.get(url, headers={'User-Agent': 'VigiAA/1.0'}).json()
            addr = res.get("address", {})
            self.gps_address_data.clear()
            self.gps_address_data["lat"] = str(lat); self.gps_address_data["lon"] = str(lon) 
            self.gps_address_data["localidade"] = addr.get("city") or addr.get("town") or addr.get("municipality")
            self.gps_address_data["bairro"] = addr.get("suburb") or addr.get("neighbourhood")
            self.gps_address_data["logradouro"] = addr.get("road")
            self.gps_address_data["cep"] = addr.get("postcode")
            self.gps_address_data["numero"] = addr.get("house_number")
            Clock.schedule_once(lambda dt: self.open_gps_modal(source), 0)
        except:
            self.mostrar_aviso("Erro ao traduzir endereço.")
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
        texto_dialog = f"[b]Rua:[/b] {rua}\\n[b]Bairro:[/b] {bairro}\\n[b]Cidade:[/b] {cidade}\\n\\n[i]Fonte: {source}[/i]"
        
        self.gps_dialog = MDDialog(
            title="Confirme os Dados:",
            text=texto_dialog,
            buttons=[
                MDFlatButton(text="Cancelar", text_color=(1,0,0,1), on_release=lambda x: self.gps_dialog.dismiss()),
                MDFlatButton(text="Confirmar", text_color=(1,1,1,1), md_bg_color=(0.22, 0.75, 0.94, 1), on_release=self.confirm_gps_fill)
            ]
        )
        self.gps_dialog.open()

    def confirm_gps_fill(self, instance):
        self.gps_dialog.dismiss()
        self.fill_address_fields(self.gps_address_data)

    def pre_submit_check(self):
        if not all([self.ids.tf_cep.text, self.ids.tf_city.text, self.ids.tf_neighborhood.text, self.ids.tf_street.text, self.ids.tf_number.text, self.ids.tf_notif_date.text, self.ids.tf_birth_date.text]):
            self.mostrar_aviso("Preencha todos os campos obrigatórios (*)")
            return
        if not self.ids.chk_sim.active and not self.ids.chk_nao.active:
            self.mostrar_aviso("Selecione se o teste foi positivo ou negativo")
            return
        if self.ids.chk_sim.active: self.open_warning_modal()
        else: self.execute_submit(is_positive=False)

    @mainthread
    def open_warning_modal(self):
        from kivy.uix.modalview import ModalView
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel, MDIcon
        from kivy.metrics import dp

        # 1. O Modal Puro (Agora com 260dp de altura para caber o novo texto!)
        self.warning_dialog = ModalView(
            size_hint=(0.85, None),
            height=dp(260), # <--- ALTURA AUMENTADA AQUI
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.5)
        )

        # 2. A Caixa Branca Arredondada
        card = MDCard(
            orientation="vertical",
            padding="20dp",
            spacing="15dp",
            radius=[15, 15, 15, 15],
            md_bg_color=(1, 1, 1, 1),
            elevation=1
        )

        # 3. O Título Customizado (Ícone + Aviso)
        title_box = MDBoxLayout(adaptive_size=True, spacing="10dp", pos_hint={"center_x": .5})
        title_box.add_widget(MDIcon(icon="alert", theme_text_color="Custom", text_color=(0, 0, 0, 1), font_size="24sp"))
        title_box.add_widget(MDLabel(text="Aviso", bold=True, adaptive_size=True, font_size="20sp"))
        card.add_widget(title_box)

        # 4. O Novo Texto (Com fonte Body2 para ficar elegante em textos longos)
        card.add_widget(MDLabel(
            text="Nos casos de teste positivo o paciente deve ser identificado. A Secretaria de Saúde irá entrar em contato com o número cadastrado para eventuais procedimentos.",
            halign="center",
            theme_text_color="Primary",
            font_style="Body2" # <--- Fonte ideal para textos longos no KivyMD
        ))

        # 5. O Botão Azul Largo (MDCard blindado)
        btn = MDCard(
            size_hint=(0.6, None),
            height=dp(40),
            md_bg_color=(0.22, 0.75, 0.94, 1),
            radius=[10, 10, 10, 10],
            ripple_behavior=False,
            pos_hint={"center_x": .5}
        )
        btn.bind(on_release=self.confirm_positive)
        
        btn.add_widget(MDLabel(
            text="Ok", 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1), 
            halign="center", 
            bold=True
        ))
        
        card.add_widget(btn)

        self.warning_dialog.add_widget(card)
        self.warning_dialog.open()

    def confirm_positive(self, instance):
        if self.warning_dialog:
            self.warning_dialog.dismiss()
        self.execute_submit(is_positive=True)

    def execute_submit(self, is_positive):
        if not store.exists("session"):
            self.manager.current = 'login'
            return
        token = store.get("session")["token"]
        self.ids.btn_submit.text = "Enviando..."
        self.ids.btn_submit.disabled = True
        threading.Thread(target=self._worker_submit, args=(token, is_positive), daemon=True).start()

    def _worker_submit(self, token, is_positive):
        try:
            data = {
                "notification_date": self.ids.tf_notif_date.text,
                "cep": self.ids.tf_cep.text,
                "city": self.ids.tf_city.text,
                "neighborhood": self.ids.tf_neighborhood.text,
                "street": self.ids.tf_street.text,
                "number": self.ids.tf_number.text,
                "birth_date": self.ids.tf_birth_date.text,
                "positive_test": is_positive
            }
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{config.API_URL}/api/report-case/", json=data, headers=headers)
            
            if res.status_code in [200, 201]: 
                case_data = res.json()
                case_id = case_data.get('id')
                if is_positive:
                    store.put("current_case", id=case_id)
                    Clock.schedule_once(lambda dt: self.go_to_positive_screen(), 0)
                else:
                    Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else: self.mostrar_aviso("Erro no servidor.")
        except Exception as ex: self.mostrar_aviso("Erro de comunicação com o sistema.")
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def go_to_positive_screen(self):
        try: self.manager.current = 'form_caso_positivo'
        except Exception: self.mostrar_aviso("A tela de identificação ainda não foi criada!")

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "CADASTRAR"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        self.success_dialog = MDDialog(
            title="Sucesso!",
            text="Caso de dengue cadastrado com sucesso!",
            buttons=[MDFlatButton(text="OK", text_color=(1,1,1,1), md_bg_color=(0, 0.7, 0, 1), on_release=self.close_success_modal)]
        )
        self.success_dialog.open()

    def close_success_modal(self, instance):
        self.success_dialog.dismiss()
        self.go_back()