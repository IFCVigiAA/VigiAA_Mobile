from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests
import threading
import config

store = JsonStore('vigiaa_storage.json')

KV_CHANGE_PASSWORD = '''
<ChangePasswordScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # HEADER
        MDTopAppBar:
            title: "Alterar senha"
            md_bg_color: 0.22, 0.75, 0.94, 1  # Azul ciano
            specific_text_color: 1, 1, 1, 1
            elevation: 2
            left_action_items: [["chevron-left", lambda x: root.go_back()]]

        # BODY
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "30dp"
                spacing: "20dp"
                adaptive_height: True

                MDLabel:
                    text: "Defina sua nova credencial"
                    theme_text_color: "Hint"
                    font_size: "14sp"
                    adaptive_height: True

                MDTextField:
                    id: old_pass
                    hint_text: "Senha Atual"
                    password: True
                    color_mode: "custom"
                    line_color_focus: 0.22, 0.75, 0.94, 1

                MDTextField:
                    id: new_pass
                    hint_text: "Nova Senha"
                    password: True
                    color_mode: "custom"
                    line_color_focus: 0.22, 0.75, 0.94, 1

                MDTextField:
                    id: confirm_pass
                    hint_text: "Confirmar Nova Senha"
                    password: True
                    color_mode: "custom"
                    line_color_focus: 0.22, 0.75, 0.94, 1

                # Espaçamento extra
                MDBoxLayout:
                    size_hint_y: None
                    height: "20dp"

                MDRaisedButton:
                    text: "Salvar Nova Senha"
                    md_bg_color: 0, 0, 0, 1
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    elevation: 0
                    padding: "15dp"
                    on_release: root.change_click()
'''
Builder.load_string(KV_CHANGE_PASSWORD)

class ChangePasswordScreen(MDScreen):
    def go_back(self):
        self.manager.current = 'home'
        self.manager.get_screen('home').ids.bottom_nav.switch_tab('tab_profile')

    def change_click(self):
        old_p = self.ids.old_pass.text
        new_p = self.ids.new_pass.text
        conf_p = self.ids.confirm_pass.text

        if not old_p or not new_p or not conf_p:
            self.mostrar_aviso("Preencha todos os campos.", "red")
            return

        if new_p != conf_p:
            self.mostrar_aviso("As novas senhas não coincidem.", "red")
            return

        self.mostrar_aviso("Salvando...", "blue")
        threading.Thread(target=self._worker_change, args=(old_p, new_p)).start()

    def _worker_change(self, old_p, new_p):
        if not store.exists("session"):
            Clock.schedule_once(lambda dt: self.ir_para_login(), 0)
            return
            
        token = store.get("session")["token"]
        
        try:
            headers = {"Authorization": f"Bearer {token}", "ngrok-skip-browser-warning": "true"}
            response = requests.put(
                f"{config.API_URL}/api/change-password/", 
                data={"old_password": old_p, "new_password": new_p},
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                self.mostrar_aviso("Senha alterada com sucesso!", "green")
                Clock.schedule_once(self.limpar_campos, 0)
            elif response.status_code == 400:
                self.mostrar_aviso("Senha incorreta ou inválida.", "red")
            elif response.status_code == 401:
                Clock.schedule_once(lambda dt: self.ir_para_login(), 0)
            else:
                self.mostrar_aviso(f"Erro {response.status_code}", "red")
        except Exception as ex:
            self.mostrar_aviso("Erro de conexão com a internet.", "red")

    @mainthread
    def limpar_campos(self, dt):
        self.ids.old_pass.text = ""
        self.ids.new_pass.text = ""
        self.ids.confirm_pass.text = ""
        
        # Opcional: volta pra aba de perfil automaticamente depois de 1.5s
        Clock.schedule_once(lambda dt: self.go_back(), 1.5)

    @mainthread
    def ir_para_login(self):
        self.manager.current = 'login'

    @mainthread
    def mostrar_aviso(self, texto, cor):
        cores_rgba = {
            "red": (1, 0, 0, 1),
            "green": (0, 0.7, 0, 1),
            "blue": (0.22, 0.75, 0.94, 1)
        }
        cor_escolhida = cores_rgba.get(cor, (1, 1, 1, 1))
        
        MDSnackbar(
            MDLabel(text=texto, theme_text_color="Custom", text_color=cor_escolhida)
        ).open()