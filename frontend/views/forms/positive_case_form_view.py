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

store = JsonStore('vigiaa_storage.json')

KV_POSITIVE_FORM = '''
<PositiveCaseFormScreen>:
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
                text: "Identificação do Paciente"
                font_size: "20sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": .5}

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "20dp"
                adaptive_height: True

                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    padding: "15dp"
                    spacing: "10dp"
                    md_bg_color: 0.88, 0.96, 1, 1 
                    
                    MDLabel:
                        text: "Teste Positivo Confirmado"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.46, 0.82, 1
                        halign: "center"

                    MDLabel:
                        text: "Como o caso foi positivo, os dados do paciente são obrigatórios para a vigilância epidemiológica."
                        theme_text_color: "Hint"
                        font_style: "Caption"
                        halign: "center"

                MDLabel:
                    text: "Campos marcados com * são obrigatórios"
                    font_style: "Caption"
                    theme_text_color: "Hint"

                MDTextField:
                    id: tf_nome
                    hint_text: "Nome completo *"
                    icon_left: "account-outline"

                MDTextField:
                    id: tf_cpf
                    hint_text: "CPF (Apenas números)"
                    icon_left: "card-account-details-outline"
                    input_filter: "int"
                    max_text_length: 11

                MDTextField:
                    id: tf_telefone
                    hint_text: "Telefone com DDD *"
                    icon_left: "phone-outline"
                    input_filter: "int"
                    max_text_length: 11

                MDTextField:
                    id: tf_local_teste
                    hint_text: "Local do teste *"
                    icon_left: "hospital-building"
                    readonly: True
                    on_focus: if self.focus: root.open_local_menu()

                Widget:
                    size_hint_y: None
                    height: "20dp"

                # BOTÃO SEM SOMBRA ANTI-CRASH
                MDFlatButton:
                    id: btn_submit
                    text: "VINCULAR PACIENTE"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    padding: "15dp"
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
        self.ids.btn_submit.text = "VINCULAR PACIENTE"
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