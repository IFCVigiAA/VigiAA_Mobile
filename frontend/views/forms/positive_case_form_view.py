from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast
import requests
import threading
import config

store = JsonStore('sessao_app.json')

KV_POSITIVE_FORM = '''
<PositiveCaseFormScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # --- Top Bar (Fundo branco, setinha preta) verbatim design looks
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

            # Spacer verbatim design trick
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

                # --- FORM ROWS (Estilo Tabela) verbatim design looks and functionality
                
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
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_nome
                        hint_text: "Digite seu nome"
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]

                # CPF
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "CPF"
                        bold: True
                        size_hint_x: None
                        width: "130dp"
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_cpf
                        hint_text: "000.000.000-00"
                        input_filter: "int"
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
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
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_telefone
                        hint_text: "(XX) XXXXX-XXXX"
                        input_filter: "int"
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
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
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_local_teste
                        hint_text: "Selecione o local"
                        readonly: True
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2]
                        on_focus: if self.focus: root.open_local_menu()
                    MDIconButton:
                        icon: "chevron-down"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1
                        pos_hint: {"center_y": .5}
                        on_release: root.open_local_menu()
                        
                # O ESPAÇADOR VITAL PARA O BOTÃO NÃO TAMPAR O FINAL
                Widget:
                    size_hint_y: None
                    height: "100dp"

        # --- Botão CADASTRAR fixo no rodapé (Em sobreposição) ---
        # anchors the button at the very bottom of the screen verbatim design looks
        AnchorLayout:
            anchor_x: "center"
            anchor_y: "bottom"
            size_hint_y: None
            height: "80dp"
            padding: ["15dp", "0dp", "15dp", "15dp"] # Padding around anchored button for full width design feel verbatim design feel

            # Styled full-width filled blue button verbatim design look image_a7d941.png
            # Standard FillRoundFlatButton style used for ripple safety but styled light blue
            MDFillRoundFlatButton:
                id: btn_submit
                text: "CADASTRAR" # Match design text verbatim design look image_a7d941.png
                font_size: "18sp"
                bold: True # Make bold text matching design look
                md_bg_color: 0.22, 0.75, 0.94, 1 # Standard light blue design color
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1 # White
                size_hint_x: 1 # Standard filled blue button full width anchored style
                height: "56dp"
                # Ripple safety standard
                radius: [15, 15, 15, 15] # Rounded corner style verbatim design look image_a7d941.png
                on_release: root.submit_form()
'''

Builder.load_string(KV_POSITIVE_FORM)

class PositiveCaseFormScreen(MDScreen):
    opcoes_locais = ["Posto de Saúde", "Farmácia", "Hospital", "Laboratório"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_locais = None
        self.success_dialog = None

    def on_pre_enter(self, *args):
        self.ids.tf_nome.text = ""
        self.ids.tf_cpf.text = ""
        self.ids.tf_telefone.text = ""
        self.ids.tf_local_teste.text = ""
        self.ids.btn_submit.text = "CADASTRAR CASO"
        self.ids.btn_submit.disabled = False

    def go_back(self):
        self.manager.current = 'form_caso'

    def go_home(self):
        self.manager.current = 'home'
        self.manager.get_screen('home').ids.bottom_nav.switch_tab('tab_new')

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
            toast("Erro: Caso base não encontrado. Volte e tente novamente.")
            return
            
        dengue_case_id = store.get("current_case")["id"]
        token = store.get("session")["token"]
        
        if not all([self.ids.tf_nome.text, self.ids.tf_telefone.text, self.ids.tf_local_teste.text]):
            toast("Preencha todos os campos obrigatórios (*)")
            return
            
        self.ids.btn_submit.text = "Enviando..."
        self.ids.btn_submit.disabled = True
        threading.Thread(target=self._worker_submit, args=(token, dengue_case_id), daemon=True).start()

    def _worker_submit(self, token, dengue_case_id):
        try:
            data = {
                "dengue_case": dengue_case_id,
                "patient_name": self.ids.tf_nome.text,
                "cpf": self.ids.tf_cpf.text,
                "phone": self.ids.tf_telefone.text,
                "test_location": self.ids.tf_local_teste.text
            }
                
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{config.API_URL}/api/report-positive-case/", json=data, headers=headers)
            
            if res.status_code in [200, 201]: 
                store.delete("current_case")
                Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else: 
                Clock.schedule_once(lambda dt: toast(f"Erro no servidor. Código: {res.status_code}"), 0)
                
        except Exception as ex: 
            Clock.schedule_once(lambda dt: toast("Erro de comunicação com o sistema."), 0)
            
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "VINCULAR PACIENTE"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        self.success_dialog = MDDialog(
            title="Sucesso!",
            text="Paciente identificado com sucesso!",
            buttons=[
                MDFlatButton(text="OK", text_color=(1,1,1,1), md_bg_color=(0, 0.7, 0, 1), on_release=self.close_success_modal)
            ]
        )
        self.success_dialog.open()

    def close_success_modal(self, instance):
        self.success_dialog.dismiss()
        self.go_home()