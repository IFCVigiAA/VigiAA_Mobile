from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests
import threading
import config

KV_REGISTER = '''
<RegisterScreen>:
    md_bg_color: 1, 1, 1, 1

    ScrollView:
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True

            # --- PARTE SUPERIOR (Arredondada) ---
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: "280dp"
                padding: ["20dp", "40dp", "20dp", "20dp"]
                spacing: "0dp"
                canvas.before:
                    Color:
                        rgba: 0.22, 0.75, 0.94, 1  # Mantendo o azul ciano padrão da Home/Login
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [0, 0, 50, 50]
                
                Image:
                    source: "assets/images/logo-sem-fundo.png"
                    size_hint: None, None
                    size: "170dp", "170dp"
                    pos_hint: {"center_x": .5}
                    
                MDLabel:
                    text: "VigiAA"
                    font_size: "26sp"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.1, 0.1, 1
                    size_hint_y: None
                    height: "30dp"
                
                MDLabel:
                    text: "Crie sua conta"
                    font_size: "16sp"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.1, 0.1, 1
                    size_hint_y: None
                    height: "30dp"

            # --- PARTE INFERIOR (Formulário) ---
            MDBoxLayout:
                orientation: "vertical"
                padding: ["30dp", "20dp", "30dp", "20dp"]
                spacing: "15dp"
                adaptive_height: True

                MDTextField:
                    id: first_name
                    hint_text: "Nome"
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDTextField:
                    id: last_name
                    hint_text: "Sobrenome"
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDTextField:
                    id: username
                    hint_text: "Usuário"
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDTextField:
                    id: email
                    hint_text: "Email"
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDTextField:
                    id: password
                    hint_text: "Senha"
                    password: True
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1

                MDTextField:
                    id: password2
                    hint_text: "Confirmar Senha"
                    password: True
                    mode: "round"
                    fill_color_normal: 1, 1, 1, 1
                    text_color_normal: 0, 0, 0, 1
                    
                MDBoxLayout:
                    size_hint_y: None
                    height: "10dp"

                MDRaisedButton:
                    id: btn_register
                    text: "Cadastrar"
                    md_bg_color: 0, 0, 0, 1
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    elevation: 0
                    padding: "15dp"
                    on_release: root.register_clicked()

                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_height: True
                    spacing: "5dp"
                    pos_hint: {"center_x": .5}

                    MDLabel:
                        text: "Já possui conta?"
                        theme_text_color: "Hint"
                        font_size: "13sp"
                        adaptive_width: True

                    MDTextButton:
                        text: "Faça Login"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.46, 0.82, 1
                        font_size: "13sp"
                        on_release: root.go_to_login()
'''
Builder.load_string(KV_REGISTER)

class RegisterScreen(MDScreen):
    def register_clicked(self):
        # Validação básica
        if not self.ids.username.text or not self.ids.password.text:
            self.mostrar_aviso("Preencha todos os campos obrigatórios.", "red")
            return

        if self.ids.password.text != self.ids.password2.text:
            self.mostrar_aviso("As senhas não coincidem.", "red")
            return

        # Feedback visual
        self.ids.btn_register.text = "Criando..."
        self.ids.btn_register.disabled = True

        # Pega os dados
        payload = {
            "first_name": self.ids.first_name.text,
            "last_name": self.ids.last_name.text,
            "username": self.ids.username.text,
            "email": self.ids.email.text,
            "password": self.ids.password.text,
            "password2": self.ids.password2.text
        }

        # Inicia a thread para não travar a tela
        threading.Thread(target=self._worker_register, args=(payload,)).start()

    def _worker_register(self, payload):
        try:
            response = requests.post(f"{config.API_URL}/api/register/", json=payload, timeout=15)
            
            if response.status_code == 201:
                self.mostrar_aviso("Conta criada! Redirecionando...", "green")
                Clock.schedule_once(lambda dt: self.go_to_login(), 1.5)
            else:
                try:
                    error_data = response.json()
                    msg = error_data.get("error") or str(error_data)
                except:
                    msg = f"Erro {response.status_code}: {response.text}"
                
                self.resetar_botao(msg)

        except requests.exceptions.ConnectionError:
            self.resetar_botao("Erro de conexão com o servidor.")
        except Exception as ex:
            self.resetar_botao(f"Erro inesperado: {ex}")

    @mainthread
    def resetar_botao(self, mensagem_erro):
        self.mostrar_aviso(mensagem_erro, "red")
        self.ids.btn_register.text = "Cadastrar"
        self.ids.btn_register.disabled = False

    @mainthread
    def go_to_login(self):
        # Desliza a tela para o Login
        self.manager.current = 'login'

    @mainthread
    def mostrar_aviso(self, texto, cor):
        cores_rgba = {
            "red": (1, 0, 0, 1),
            "green": (0, 0.7, 0, 1)
        }
        cor_escolhida = cores_rgba.get(cor, (1, 1, 1, 1))
        MDSnackbar(
            MDLabel(text=texto, theme_text_color="Custom", text_color=cor_escolhida)
        ).open()