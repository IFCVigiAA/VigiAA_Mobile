# --- 1. A VACINA DEFINITIVA (Deve ser a PRIMEIRA coisa do arquivo) ---
from kivy.properties import VariableListProperty
from kivymd.uix.button import (
    MDFlatButton, 
    MDRectangleFlatIconButton, 
    MDRaisedButton, 
    MDFillRoundFlatButton, 
    MDFillRoundFlatIconButton
)

# Injetamos o 'radius' em TODAS as classes de botões possíveis. 
# Isso impede o crash de Ripple Behavior (image_c99f09) de uma vez por todas.
classes_para_vacinar = [
    MDFlatButton, MDRectangleFlatIconButton, MDRaisedButton, 
    MDFillRoundFlatButton, MDFillRoundFlatIconButton
]

for cls in classes_para_vacinar:
    if not hasattr(cls, 'radius'):
        cls.radius = VariableListProperty([0, 0, 0, 0])

try:
    # Vacina específica para os números dentro do calendário
    from kivymd.uix.pickers.datepicker.datepicker import MDDatePickerItemText
    if not hasattr(MDDatePickerItemText, 'radius'):
        MDDatePickerItemText.radius = VariableListProperty([0, 0, 0, 0])
except Exception:
    pass
# ---------------------------------------------------------------------

from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp
from kivy.utils import platform
import requests
import threading
import unicodedata
from urllib.parse import quote
import config
from plyer import gps
import os
import time

store = JsonStore('sessao_app.json')

# KV corrigido: Propriedades em linhas separadas para evitar erro 'Invalid data' (image_c6ff16)
KV_CASE_FORM = '''
<CaseFormScreen>:
    md_bg_color: 1, 1, 1, 1
    MDBoxLayout:
        orientation: "vertical"
        
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
                on_release: root.go_back()
            MDLabel:
                text: "Casos de dengue"
                font_size: "20sp"
                bold: True
                halign: "center"
            Widget:
                size_hint_x: None
                width: "48dp"

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: ["20dp", "20dp", "20dp", "20dp"]
                spacing: "5dp"
                adaptive_height: True

                MDFillRoundFlatIconButton:
                    id: btn_gps
                    text: "Capturar localização pelo GPS"
                    icon: "map-marker-outline"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.9
                    on_release: root.start_location()

                MDLabel:
                    text: "Campos marcados com * são obrigatórios"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: dp(30)

                # --- Campos ---
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Data Notificação[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_notif_date
                        hint_text: "Selecionar"
                        readonly: True
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.show_date_picker('notif')

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "CEP"
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_cep
                        hint_text: "Digite o CEP"
                        input_filter: "int"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_text: root.on_cep_change(self.text)

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "MUNICÍPIO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_city
                        hint_text: "Selecionar"
                        readonly: True
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_city_menu()

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "BAIRRO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_neighborhood
                        hint_text: "Selecionar"
                        readonly: True
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_neighborhood_menu()

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "RUA[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_street
                        hint_text: "Digite a rua"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                    MDIconButton:
                        id: btn_search_street
                        icon: "magnify"
                        on_release: root.search_address_by_name()

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "NÚMERO[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_number
                        hint_text: "Número"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Nascimento[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    TextInput:
                        id: tf_birth_date
                        hint_text: "Selecionar"
                        readonly: True
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.show_date_picker('birth')

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Teste positivo[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "150dp"
                    MDBoxLayout:
                        adaptive_height: True
                        pos_hint: {"center_y": .5}
                        MDCheckbox:
                            id: chk_sim
                            group: 'teste'
                            size_hint: None, None
                            size: "40dp", "40dp"
                        MDLabel:
                            text: "Sim"
                            adaptive_width: True
                        Widget:
                            size_hint_x: None
                            width: "10dp"
                        MDCheckbox:
                            id: chk_nao
                            group: 'teste'
                            size_hint: None, None
                            size: "40dp", "40dp"
                        MDLabel:
                            text: "Não"
                            adaptive_width: True

                Widget:
                    size_hint_y: None
                    height: "100dp"

        AnchorLayout:
            anchor_x: "center"
            anchor_y: "bottom"
            size_hint_y: None
            height: "80dp"
            padding: "15dp"
            MDFillRoundFlatButton:
                id: btn_submit
                text: "CADASTRAR"
                md_bg_color: 0.22, 0.75, 0.94, 1
                size_hint_x: 1
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
        self.dialog = None

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
        self._reset_gps_btn()

    @mainthread
    def mostrar_aviso(self, texto):
        from kivymd.toast import toast
        toast(texto)

    def go_back(self):
        self.manager.current = 'home'

    # --- DATAS ---
    def show_date_picker(self, field_type):
        self.ids.tf_notif_date.focus = False
        self.ids.tf_birth_date.focus = False
        date_dialog = MDDatePicker()
        if field_type == 'notif':
            date_dialog.bind(on_save=self.on_save_notif, on_cancel=lambda x, y: x.dismiss())
        else:
            date_dialog.bind(on_save=self.on_save_birth, on_cancel=lambda x, y: x.dismiss())
        Clock.schedule_once(lambda dt: date_dialog.open(), 0.1)

    def on_save_notif(self, instance, value, date_range):
        self.ids.tf_notif_date.text = value.strftime("%d/%m/%Y")
        instance.dismiss()

    def on_save_birth(self, instance, value, date_range):
        self.ids.tf_birth_date.text = value.strftime("%d/%m/%Y")
        instance.dismiss()

    # --- GPS (PRECISÃO FOCOS) ---
    def start_location(self):
        self.ids.btn_gps.text = "Buscando..."
        self.ids.btn_gps.disabled = True
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], self._on_permissions_result)
        else:
            self._reset_gps_btn()
            self.mostrar_aviso("GPS indisponível no PC.")

    def _on_permissions_result(self, perms, grants):
        Clock.schedule_once(lambda dt: self._safe_gps_start(grants), 0)

    def _safe_gps_start(self, grants):
        if any(grants):
            try:
                gps.configure(on_location=self._on_gps_location)
                gps.start(minTime=1000, minDistance=1)
                self.gps_tempo = 35
                self.gps_event = Clock.schedule_interval(self._gps_countdown, 1)
            except Exception: self._reset_gps_btn()
        else: self._reset_gps_btn()

    def _gps_countdown(self, dt):
        self.gps_tempo -= 1
        if self.gps_tempo <= 0:
            self.gps_event.cancel()
            self._gps_escape_memory()
        else:
            self.ids.btn_gps.text = f"Sinal ({self.gps_tempo}s)..."

    @mainthread
    def _gps_escape_memory(self):
        gps.stop()
        lat, lon = self._get_last_known_location_android()
        if lat and lon:
            threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Memória")).start()
        else:
            self._reset_gps_btn()
            self.mostrar_aviso("Sinal fraco.")

    def _get_last_known_location_android(self):
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            lm = activity.getSystemService(autoclass('android.content.Context').LOCATION_SERVICE)
            loc = lm.getLastKnownLocation(autoclass('android.location.LocationManager').GPS_PROVIDER)
            if not loc: loc = lm.getLastKnownLocation(autoclass('android.location.LocationManager').NETWORK_PROVIDER)
            if loc: return loc.getLatitude(), loc.getLongitude()
        except Exception: pass
        return None, None

    @mainthread
    def _on_gps_location(self, **kwargs):
        if hasattr(self, 'gps_event'): self.gps_event.cancel()
        gps.stop()
        threading.Thread(target=self._worker_get_address_from_coords, args=(kwargs.get('lat'), kwargs.get('lon'), "Satélite")).start()

    def _worker_get_address_from_coords(self, lat, lon, source):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18"
            res = requests.get(url, headers={'User-Agent': 'VigiAA/1.0'}).json()
            addr = res.get("address", {})
            self.gps_address_data = {"lat": str(lat), "lon": str(lon), "localidade": addr.get("city") or addr.get("town"), "bairro": addr.get("suburb"), "logradouro": addr.get("road"), "cep": addr.get("postcode"), "numero": addr.get("house_number")}
            Clock.schedule_once(lambda dt: self.open_gps_modal(source), 0)
        except Exception: Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    @mainthread
    def open_gps_modal(self, source):
        self.ids.btn_gps.text = "Localizado!"
        self.ids.btn_gps.disabled = False
        self.dialog = MDDialog(title="Confirmar Local?", text=f"Rua: {self.gps_address_data.get('logradouro')}\\nBairro: {self.gps_address_data.get('bairro')}",
            buttons=[MDFlatButton(text="OK", text_color=(0.22,0.75,0.94,1), on_release=self.confirm_gps_fill)])
        self.dialog.open()

    def confirm_gps_fill(self, x):
        self.dialog.dismiss()
        self.fill_address_fields(self.gps_address_data)

    def _reset_gps_btn(self):
        self.ids.btn_gps.text = "Capturar localização pelo GPS"
        self.ids.btn_gps.disabled = False

    # --- BUSCA RUA ---
    def search_address_by_name(self):
        city = self.ids.tf_city.text
        street = self.ids.tf_street.text.strip()
        if not city or len(street) < 3:
            self.mostrar_aviso("Selecione a cidade e digite 3 letras.")
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
                else: self.mostrar_aviso("Rua não encontrada.")
            else: self.mostrar_aviso("Erro no servidor.")
        except Exception: self.mostrar_aviso("Erro de conexão.")
        Clock.schedule_once(lambda dt: setattr(self.ids.btn_search_street, 'icon', 'magnify'), 0)

    @mainthread
    def open_manual_modal(self, address_list):
        from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
        from kivy.uix.scrollview import ScrollView
        from kivymd.uix.boxlayout import MDBoxLayout
        content = ScrollView(size_hint_y=None, height=dp(300))
        box = MDBoxLayout(orientation='vertical', adaptive_height=True)
        for addr in address_list:
            item = TwoLineIconListItem(text=addr.get("logradouro", ""), secondary_text=f"{addr.get('bairro', '')}", 
                                       on_release=lambda x, a=addr: self.select_address_manual(a))
            item.add_widget(IconLeftWidget(icon="map-marker"))
            box.add_widget(item)
        content.add_widget(box)
        self.dialog = MDDialog(title="Selecione a Rua", type="custom", content_cls=content, buttons=[MDFlatButton(text="FECHAR", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def select_address_manual(self, addr_data):
        self.dialog.dismiss()
        self.fill_address_fields(addr_data)

    # --- SUBMISSÃO E FLUXO ---
    def pre_submit_check(self):
        # 1. CAPTURAMOS TUDO (Incluindo o CEP que estava faltando)
        payload = {
            "notification_date": self.ids.tf_notif_date.text,
            "cep": self.ids.tf_cep.text, # <--- O FALTANTE!
            "city": self.ids.tf_city.text,
            "neighborhood": self.ids.tf_neighborhood.text,
            "street": self.ids.tf_street.text,
            "number": self.ids.tf_number.text,
            "birth_date": self.ids.tf_birth_date.text,
            "positive_test": self.ids.chk_sim.active,
            "latitude": self.gps_address_data.get("lat", "-27.000"),
            "longitude": self.gps_address_data.get("lon", "-48.000")
        }

        # Validação simples no Kivy
        if not all([payload["city"], payload["street"], payload["notification_date"]]):
            self.mostrar_aviso("Preencha os campos obrigatórios (*)")
            return
        
        if not self.ids.chk_sim.active and not self.ids.chk_nao.active:
            self.mostrar_aviso("Selecione o resultado do teste.")
            return

        if payload["positive_test"]:
            Clock.schedule_once(lambda dt: self.open_warning_modal(payload), 0.1)
        else:
            self.execute_submit(payload)

    @mainthread
    def open_warning_modal(self, payload):
        btn_ok = MDRaisedButton(
            text="OK", 
            md_bg_color=(0.22, 0.75, 0.94, 1),
            on_release=lambda x: self.confirm_positive(payload)
        )
        self.dialog = MDDialog(
            title="Aviso de Teste Positivo",
            text="O paciente deve ser identificado. A Secretaria de Saúde entrará em contato para os procedimentos.",
            buttons=[btn_ok]
        )
        self.dialog.ids.button_box.anchor_x = "center"
        self.dialog.open()

    def confirm_positive(self, payload):
        self.dialog.dismiss()
        self.execute_submit(payload)

    def execute_submit(self, payload):
        if not store.exists("session"): 
            self.manager.current = 'login'
            return
        token = store.get("session")["token"]
        self.ids.btn_submit.text = "Enviando..."
        self.ids.btn_submit.disabled = True
        threading.Thread(target=self._worker_submit, args=(token, payload), daemon=True).start()

    def _worker_submit(self, token, payload):
        try:
            url = f"{config.API_URL}/api/report-case/"
            headers = {
                "Authorization": f"Bearer {token}",
                "ngrok-skip-browser-warning": "true"
            }
            
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # DEBUG: Se der erro 400 de novo, o terminal vai te dizer QUAL campo está errado
            if res.status_code == 400:
                print(f"ERRO 400 DO DJANGO: {res.text}")
            
            if res.status_code in [200, 201]:
                case_id = res.json().get('id')
                if payload["positive_test"]:
                    store.put("current_case", id=case_id)
                    Clock.schedule_once(lambda dt: self.go_to_positive_screen(), 0.2)
                else:
                    Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else:
                self.mostrar_aviso(f"Erro {res.status_code} no servidor.")
        except Exception as e:
            self.mostrar_aviso("Erro de conexão.")
            
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def go_to_positive_screen(self):
        try:
            self.manager.current = 'form_caso_positivo' 
        except Exception:
            self.mostrar_aviso("Tela não encontrada.")
            self.manager.current = 'home'

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "CADASTRAR"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        self.dialog = MDDialog(title="Sucesso!", text="Caso registrado.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.go_back())])
        self.dialog.open()

    # --- AUXILIARES ---
    def fill_address_fields(self, data):
        self.ids.tf_city.text = data.get("localidade") or ""
        self.ids.tf_neighborhood.text = data.get("bairro") or ""
        self.ids.tf_street.text = data.get("logradouro") or ""
        self.ids.tf_cep.text = (data.get("cep") or "").replace("-", "")
        if self.ids.tf_city.text: self.ids.tf_neighborhood.disabled = False

    def open_city_menu(self):
        items = [{"viewclass": "OneLineListItem", "text": c, "on_release": lambda x=c: self.set_city(x)} for c in self.neighborhoods_db.keys()]
        MDDropdownMenu(caller=self.ids.tf_city, items=items, width_mult=4).open()

    def set_city(self, x): self.ids.tf_city.text = x; self.ids.tf_neighborhood.disabled = False

    def open_neighborhood_menu(self):
        city = self.ids.tf_city.text
        if city in self.neighborhoods_db:
            items = [{"viewclass": "OneLineListItem", "text": b, "on_release": lambda x=b: self.set_neighborhood(x)} for b in self.neighborhoods_db[city]]
            MDDropdownMenu(caller=self.ids.tf_neighborhood, items=items, width_mult=4).open()

    def set_neighborhood(self, x): self.ids.tf_neighborhood.text = x

    def on_cep_change(self, text):
        if len(text.replace("-","")) == 8: threading.Thread(target=self._worker_search_cep, args=(text,), daemon=True).start()

    def _worker_search_cep(self, cep):
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
            if "erro" not in res: Clock.schedule_once(lambda dt: self.fill_address_fields(res), 0)
        except Exception: pass