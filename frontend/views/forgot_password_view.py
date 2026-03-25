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

        # --- HEADER CURVADO (COM DEGRADÊ NATIVO IGUAL AO LOGIN) ---
        GradientRoundedLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "300dp" # Altura para caber o logo e os textos confortavelmente
            padding: ["20dp", "40dp", "20dp", "20dp"]
            spacing: "15dp"

            # IMPORTANTE: Coloque o caminho correto da sua imagem do mosquito aqui!
            Image:
                source: "assets/images/logo-sem-fundo.png" # <--- Troque pelo nome do seu arquivo de imagem (ex: "assets/images/logo-sem-fundo.png")
                size_hint_y: None
                height: "120dp"
                allow_stretch: True
                keep_ratio: True
                pos_hint: {"center_x": .5}

            MDLabel:
                text: "VigiAA"
                font_size: "26sp"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                adaptive_height: True

            MDLabel:
                text: "Esqueceu sua senha?"
                font_size: "18sp"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                adaptive_height: True

        # --- CORPO DA TELA (Campos e Botão) ---
        MDBoxLayout:
            orientation: "vertical"
            padding: ["30dp", "40dp", "30dp", "20dp"]
            spacing: "25dp"

            MDLabel:
                text: "Digite seu email cadastrado para receber o link"
                theme_text_color: "Hint"
                halign: "center"
                font_size: "14sp"
                adaptive_height: True

            # Campo de Email (Com borda retangular igual à foto)
            MDTextField:
                id: email_field
                hint_text: "Email cadastrado"
                mode: "rectangle" # Modo de contorno em vez de apenas uma linha
                font_size: "16sp"

            Widget:
                size_hint_y: None
                height: "5dp" # Pequeno respiro antes do botão

            # Botão Preto (Feito com MDCard para design idêntico e sem crash)
            MDCard:
                id: btn_send # O crachá do botão
                size_hint_y: None
                height: "50dp"
                md_bg_color: 0, 0, 0, 1 # Preto absoluto
                radius: [8, 8, 8, 8]
                ripple_behavior: True
                elevation: 0
                on_release: root.send_reset_click()

                MDLabel:
                    id: btn_send_text # O crachá do texto
                    text: "Enviar link"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1 # Texto Branco
                    halign: "center"
                    font_size: "16sp"
                    bold: True

            # Este Widget vazio empurra tudo para cima, não deixando o layout se espalhar
            Widget:
'''
Builder.load_string(KV_FORGOT_PASSWORD)

class ForgotPasswordScreen(MDScreen):
    
    def on_pre_enter(self, *args):
        # A nossa clássica faxina! Limpa a tela antes de você entrar nela
        self.ids.email_field.text = ""
        self.ids.btn_send_text.text = "Enviar link"
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