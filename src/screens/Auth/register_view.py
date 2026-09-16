from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivymd.toast import toast
import requests
import threading
import config

KV_REGISTER = '''
<RegisterScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # PARTE SUPERIOR (Arredondada COM O SEU DEGRADÊ NATIVO)
        GradientRoundedLayout:
            orientation: "vertical"
            size_hint_y: 0.38  # Ajuste leve para acomodar bem os labels
            padding: "20dp"
            spacing: "8dp"
            radius: [0, 0, 60, 60] 

            Image:
                source: "assets/images/logo-sem-fundo.png"
                size_hint: None, None
                size: "90dp", "90dp"  # Tamanho idêntico ao login
                pos_hint: {"center_x": .5}

            MDLabel:
                text: "VigiAA"
                font_style: "H4"
                bold: True
                halign: "center"
                adaptive_height: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1

            MDLabel:
                text: "Crie sua conta"
                font_style: "Subtitle1"
                bold: True
                halign: "center"
                adaptive_height: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1

        # FORMULÁRIO DE CADASTRO
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: ["25dp", "20dp", "25dp", "20dp"]
                spacing: "12dp"
                adaptive_height: True

                # Inputs discretos e arredondados no modo rectangle
                MDTextField:
                    id: tf_nome
                    hint_text: "Nome"
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1  # Cinza claro/discreto
                    radius: [12, 12, 12, 12]
                    
                MDTextField:
                    id: tf_sobrenome
                    hint_text: "Sobrenome"
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1
                    radius: [12, 12, 12, 12]

                MDTextField:
                    id: tf_usuario
                    hint_text: "Usuário"
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1
                    radius: [12, 12, 12, 12]

                MDTextField:
                    id: tf_email
                    hint_text: "Email"
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1
                    radius: [12, 12, 12, 12]

                MDTextField:
                    id: tf_senha
                    hint_text: "Senha"
                    password: True
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1
                    radius: [12, 12, 12, 12]

                MDTextField:
                    id: tf_confirma_senha
                    hint_text: "Confirmar senha"
                    password: True
                    mode: "rectangle"
                    line_color_normal: 0.8, 0.8, 0.8, 1
                    radius: [12, 12, 12, 12]

                Widget:
                    size_hint_y: None
                    height: "10dp"

                # BOTÃO PRETO BLINDADO
                MDFlatButton:
                    id: btn_register
                    text: "Cadastrar"
                    md_bg_color: 0, 0, 0, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    size_hint_x: 1
                    height: "50dp"
                    radius: [12, 12, 12, 12]
                    on_release: root.register_click()

                # RODAPÉ
                MDBoxLayout:
                    adaptive_size: True
                    pos_hint: {"center_x": .5}
                    spacing: "2dp"
                    padding: [0, "10dp", 0, "20dp"]

                    MDLabel:
                        text: "Já possui uma conta?"
                        theme_text_color: "Custom"
                        text_color: 0, 0, 0, 1
                        adaptive_size: True
                        font_size: "13sp"
                        pos_hint: {"center_y": .5}

                    MDFlatButton:
                        text: "Faça login"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.46, 0.82, 1
                        font_size: "13sp"
                        bold: True
                        pos_hint: {"center_y": .5}
                        on_release: root.go_to_login()
'''

Builder.load_string(KV_REGISTER)

class RegisterScreen(MDScreen):
    def on_pre_enter(self, *args):
        # Limpa os campos toda vez que a tela abre
        self.ids.tf_nome.text = ""
        self.ids.tf_sobrenome.text = ""
        self.ids.tf_usuario.text = ""
        self.ids.tf_email.text = ""
        self.ids.tf_senha.text = ""
        self.ids.tf_confirma_senha.text = ""
        self.ids.btn_register.text = "Cadastrar"
        self.ids.btn_register.disabled = False

    def go_to_login(self):
        # Vai para a tela de login
        self.manager.current = 'login'

    def register_click(self):
        nome = self.ids.tf_nome.text.strip()
        sobrenome = self.ids.tf_sobrenome.text.strip()
        usuario = self.ids.tf_usuario.text.strip()
        email = self.ids.tf_email.text.strip()
        senha = self.ids.tf_senha.text
        confirma_senha = self.ids.tf_confirma_senha.text

        if not all([nome, sobrenome, usuario, email, senha, confirma_senha]):
            toast("Preencha todos os campos!")
            return

        if senha != confirma_senha:
            toast("As senhas não coincidem!")
            return

        self.ids.btn_register.text = "Cadastrando..."
        self.ids.btn_register.disabled = True

        threading.Thread(target=self._worker_register, args=(nome, sobrenome, usuario, email, senha, confirma_senha), daemon=True).start()

    def _worker_register(self, nome, sobrenome, usuario, email, senha, confirma_senha):
        try:
            data = {
                "first_name": nome,
                "last_name": sobrenome,
                "username": usuario,
                "email": email,
                "password": senha,
                "password2": confirma_senha
            }
            
            res = requests.post(f"{config.API_URL}/api/register/", json=data)

            if res.status_code in [200, 201]:
                Clock.schedule_once(lambda dt: self._on_register_success(), 0)
            else:
                erro_msg = "Erro ao cadastrar. Verifique os dados."
                try:
                    erro_api = res.json()
                    if 'error' in erro_api:
                        erro_msg = erro_api['error']
                    elif isinstance(erro_api, dict) and len(erro_api) > 0:
                        chave = list(erro_api.keys())[0]
                        erro_msg = f"{chave}: {erro_api[chave][0]}"
                except:
                    pass
                Clock.schedule_once(lambda dt, msg=erro_msg: self._on_register_error(msg), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_register_error("Erro de conexão com o servidor."), 0)

    @mainthread
    def _on_register_success(self):
        toast("Conta criada com sucesso! Faça login.")
        self.go_to_login()

    @mainthread
    def _on_register_error(self, message):
        toast(message)
        self.ids.btn_register.text = "Cadastrar"
        self.ids.btn_register.disabled = False