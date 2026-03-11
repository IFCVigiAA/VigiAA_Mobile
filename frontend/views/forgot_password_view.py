from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests
import threading
import config

KV_FORGOT_PASSWORD = '''
<ForgotPasswordScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # --- HEADER (Com botão de voltar) ---
        MDTopAppBar:
            title: "Recuperar Senha"
            md_bg_color: 0.22, 0.75, 0.94, 1  # Azul Ciano (#39BFEF)
            specific_text_color: 1, 1, 1, 1
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        # --- CORPO DA TELA ---
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "30dp"
                spacing: "20dp"
                adaptive_height: True

                MDBoxLayout:
                    size_hint_y: None
                    height: "10dp"

                # Ícone do cadeado
                MDIcon:
                    icon: "lock-reset"
                    font_size: "80sp"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.75, 0.94, 1

                MDLabel:
                    text: "Esqueceu sua senha?"
                    font_size: "20sp"
                    bold: True
                    halign: "center"
                    adaptive_height: True

                MDLabel:
                    text: "Digite seu email para receber o link."
                    theme_text_color: "Hint"
                    halign: "center"
                    adaptive_height: True

                MDBoxLayout:
                    size_hint_y: None
                    height: "20dp"

                # Campo de Email
                MDTextField:
                    id: email_field
                    hint_text: "Digite seu email cadastrado"
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDBoxLayout:
                    size_hint_y: None
                    height: "10dp"

                # Botão de Envio
                MDRaisedButton:
                    id: btn_send
                    text: "Enviar Link"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    elevation: 0
                    padding: "15dp"
                    on_release: root.send_reset_click()
'''
Builder.load_string(KV_FORGOT_PASSWORD)

class ForgotPasswordScreen(MDScreen):
    
    def on_pre_enter(self, *args):
        # A nossa clássica faxina! Limpa a tela antes de você entrar nela
        self.ids.email_field.text = ""
        self.ids.btn_send.text = "Enviar Link"
        self.ids.btn_send.disabled = False

    def go_back(self):
        # Desliza a tela de volta para o Login
        self.manager.current = 'login'

    def send_reset_click(self):
        email = self.ids.email_field.text
        
        if not email:
            self.mostrar_aviso("Por favor, digite o email.", "red")
            return

        # Feedback visual imediato e desativação do botão contra duplo-clique
        self.ids.btn_send.text = "Conectando..."
        self.ids.btn_send.disabled = True

        threading.Thread(target=self._worker_send, args=(email,)).start()

    def _worker_send(self, email):
        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.post(
                f"{config.API_URL}/api/password-reset-request/", 
                data={"email": email},
                headers=headers,
                timeout=15
            )
            
            if response.status_code in [200, 204]:
                self.mostrar_aviso("Verifique seu e-mail! Enviamos um link.", "green")
                # Se der certo, espera 2 segundos e volta pro login automaticamente
                Clock.schedule_once(lambda dt: self.go_back(), 2)
            else:
                self.resetar_botao(f"Erro: {response.text}")
                
        except Exception as ex:
            self.resetar_botao("Erro de conexão com o servidor.")

    @mainthread
    def resetar_botao(self, mensagem_erro):
        self.mostrar_aviso(mensagem_erro, "red")
        self.ids.btn_send.text = "Enviar Link"
        self.ids.btn_send.disabled = False

    @mainthread
    def mostrar_aviso(self, texto, cor):
        cores_rgba = {"red": (1, 0, 0, 1), "green": (0, 0.7, 0, 1)}
        cor_escolhida = cores_rgba.get(cor, (1, 1, 1, 1))
        MDSnackbar(
            MDLabel(text=texto, theme_text_color="Custom", text_color=cor_escolhida)
        ).open()