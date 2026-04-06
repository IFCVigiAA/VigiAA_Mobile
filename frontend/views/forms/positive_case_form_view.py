from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivy.properties import VariableListProperty
from kivy.metrics import dp
import requests
import threading
import config

# --- [VACINA DNA FIX] ---
# Garante que botões não causem crash de ripple nesta tela
if not hasattr(MDRaisedButton, 'radius'):
    MDRaisedButton.radius = VariableListProperty([dp(8), dp(8), dp(8), dp(8)])
# ------------------------

store = JsonStore('sessao_app.json')

KV_POSITIVE_FORM = '''
<PositiveCaseFormScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # --- Top Bar ---
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
                text: "Identificação do Paciente"
                font_size: "20sp"
                bold: True
                halign: "center"

            Widget:
                size_hint_x: None
                width: "48dp"

        MDScrollView:
            id: scroller
            MDBoxLayout:
                orientation: "vertical"
                padding: ["20dp", "20dp", "20dp", "20dp"]
                spacing: "5dp"
                adaptive_height: True

                MDLabel:
                    text: "Os dados abaixo são para uso exclusivo da Secretaria de Saúde."
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: dp(40)

                # Nome
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Nome[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "130dp"
                    TextInput:
                        id: tf_nome
                        hint_text: "Digite o nome completo"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]

                # CPF
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "CPF[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "130dp"
                    TextInput:
                        id: tf_cpf
                        hint_text: "000.000.000-00"
                        input_filter: "int"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]

                # Telefone
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Telefone[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "130dp"
                    TextInput:
                        id: tf_telefone
                        hint_text: "(XX) XXXXX-XXXX"
                        input_filter: "int"
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]

                # Local do teste
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "Local do teste[color=#FF0000]*[/color]"
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "130dp"
                    TextInput:
                        id: tf_local_teste
                        hint_text: "Selecione o local"
                        readonly: True
                        background_color: 0,0,0,0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_local_menu()
                    MDIconButton:
                        icon: "chevron-down"
                        on_release: root.open_local_menu()
                        pos_hint: {"center_y": .5}

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
                text: "FINALIZAR VINCULAÇÃO"
                md_bg_color: 0.22, 0.75, 0.94, 1
                size_hint_x: 1
                height: "56dp"
                radius: [15, 15, 15, 15]
                on_release: root.submit_form()
'''

Builder.load_string(KV_POSITIVE_FORM)

class PositiveCaseFormScreen(MDScreen):
    opcoes_locais = ["Posto de Saúde", "Farmácia", "Hospital", "Laboratório", "Outros"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_locais = None
        self.success_dialog = None

    def on_pre_enter(self, *args):
        self.ids.tf_nome.text = ""
        self.ids.tf_cpf.text = ""
        self.ids.tf_telefone.text = ""
        self.ids.tf_local_teste.text = ""
        self.ids.btn_submit.text = "FINALIZAR VINCULAÇÃO"
        self.ids.btn_submit.disabled = False

    def go_back(self):
        self.manager.current = 'home'

    def open_local_menu(self):
        menu_items = [{"viewclass": "OneLineListItem", "text": local, "on_release": lambda x=local: self.set_local(x)} for local in self.opcoes_locais]
        self.menu_locais = MDDropdownMenu(caller=self.ids.tf_local_teste, items=menu_items, width_mult=4)
        self.menu_locais.open()

    def set_local(self, text_item):
        self.ids.tf_local_teste.text = text_item
        self.menu_locais.dismiss()

    def submit_form(self):
        if not store.exists("session"):
            self.manager.current = 'login'
            return
            
        if not store.exists("current_case"):
            toast("Erro: Caso base não encontrado.")
            return

        # 1. CAPTURA DE DADOS NO FIO PRINCIPAL (Vital!) 🛡️
        payload = {
            "dengue_case": store.get("current_case")["id"],
            "patient_name": self.ids.tf_nome.text,
            "cpf": self.ids.tf_cpf.text,
            "phone": self.ids.tf_telefone.text,
            "test_location": self.ids.tf_local_teste.text
        }

        # Validação simples
        if not all([payload["patient_name"], payload["phone"], payload["test_location"]]):
            toast("Preencha todos os campos obrigatórios (*)")
            return
            
        token = store.get("session")["token"]
        self.ids.btn_submit.text = "Vinculando..."
        self.ids.btn_submit.disabled = True
        
        # Inicia a thread passando o payload já pronto
        threading.Thread(target=self._worker_submit, args=(token, payload), daemon=True).start()

    def _worker_submit(self, token, payload):
        try:
            url = f"{config.API_URL}/api/report-positive-case/"
            headers = {
                "Authorization": f"Bearer {token}",
                "ngrok-skip-browser-warning": "true" # Passaporte ngrok 🎫
            }
            
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if res.status_code in [200, 201]: 
                store.delete("current_case")
                Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else: 
                print(f"DEBUG DJANGO: {res.text}")
                Clock.schedule_once(lambda dt: toast(f"Erro no servidor: {res.status_code}"), 0)
                
        except Exception as ex: 
            Clock.schedule_once(lambda dt: toast("Erro de conexão."), 0)
            
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "FINALIZAR VINCULAÇÃO"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        # Botão OK centralizado e com design limpo
        btn_ok = MDRaisedButton(
            text="OK", 
            md_bg_color=(0.22, 0.75, 0.94, 1),
            on_release=self.close_success_modal
        )
        self.success_dialog = MDDialog(
            title="Sucesso!",
            text="Paciente identificado e vinculado ao caso com sucesso!",
            buttons=[btn_ok],
            auto_dismiss=False
        )
        self.success_dialog.ids.button_box.anchor_x = "center"
        self.success_dialog.open()

    def close_success_modal(self, instance):
        self.success_dialog.dismiss()
        self.manager.current = 'home'