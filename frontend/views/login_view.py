from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Color, RoundedRectangle, Rectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
import requests
import threading
import time
import uuid
import webbrowser
import config  # Garanta que o config.py está acessível

store = JsonStore('vigiaa_storage.json')
HEADERS = {"ngrok-skip-browser-warning": "true"}

# --- A MÁGICA DO DEGRADÊ NATIVO (COM MÁSCARA DE RECORTE) ---
class GradientRoundedLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Textura simples de 2 pixels. O Kivy interpola o resto perfeitamente!
        self.texture = Texture.create(size=(1, 2), colorfmt='rgba')
        
        # Base: Verde (#72FC90) -> RGB(114, 252, 144)
        # Topo: Azul Ciano (#3AC0ED) -> RGB(58, 192, 237)
        buf = bytes([
            114, 252, 144, 255,  # Pixel de baixo
            58, 192, 237, 255    # Pixel de cima
        ])
        self.texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        
        with self.canvas.before:
            # 1. Inicia a "Tesoura" (Máscara)
            StencilPush()
            self.mask = RoundedRectangle(radius=[0, 0, 50, 50])
            StencilUse()
            
            # 2. Desenha o Degradê perfeito por cima (ele vai respeitar o corte)
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(texture=self.texture)
            
            # 3. Limpa a "Tesoura" da memória
            StencilUnUse()
            self.mask_clear = RoundedRectangle(radius=[0, 0, 50, 50])
            StencilPop()
            
        # Garante que o recorte e o degradê acompanhem o tamanho da tela
        self.bind(pos=self._update_rect, size=self._update_rect)
        
    def _update_rect(self, *args):
        self.mask.pos = self.pos
        self.mask.size = self.size
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.mask_clear.pos = self.pos
        self.mask_clear.size = self.size

# A INTERFACE VISUAL EXATA DO LOGIN
KV_LOGIN = '''
<LoginScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"

        # PARTE SUPERIOR (Arredondada COM DEGRADÊ NATIVO)
        GradientRoundedLayout:
            orientation: "vertical"
            size_hint_y: 0.65
            padding: "30dp"
            spacing: "15dp"

            Image:
                source: "assets/images/logo-sem-fundo.png"
                size_hint: None, None
                size: "140dp", "140dp"
                pos_hint: {"center_x": .5}

            MDLabel:
                text: "VigiAA"
                font_style: "H4"
                bold: True
                halign: "center"

            MDLabel:
                text: "Entre na sua conta"
                font_style: "Subtitle1"
                bold: True
                halign: "center"

            # CAMPO DE E-MAIL
            MDBoxLayout:
                size_hint_y: None
                height: "50dp"
                md_bg_color: 1, 1, 1, 1
                radius: [8, 8, 8, 8]
                padding: ["25dp", "0dp", "15dp", "0dp"]
                spacing: "15dp"

                MDIcon:
                    icon: "email-outline"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_size: "20sp"
                    pos_hint: {"center_y": .5}

                TextInput:
                    id: email_field
                    hint_text: "email@domain.com"
                    background_normal: "" 
                    background_color: 0, 0, 0, 0
                    foreground_color: 0, 0, 0, 1
                    hint_text_color: 0.6, 0.6, 0.6, 1
                    cursor_color: 0, 0, 0, 1
                    multiline: False
                    size_hint_y: 1
                    padding: ["10dp", (self.height - self.line_height) / 2, 0, 0]

            # CAMPO DE SENHA
            MDBoxLayout:
                size_hint_y: None
                height: "50dp"
                md_bg_color: 1, 1, 1, 1
                radius: [8, 8, 8, 8]
                padding: ["25dp", "0dp", "15dp", "0dp"]
                spacing: "15dp"

                MDIcon:
                    icon: "lock-outline"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_size: "20sp"
                    pos_hint: {"center_y": .5}

                TextInput:
                    id: password_field
                    hint_text: "senha"
                    password: True
                    background_normal: ""
                    background_color: 0, 0, 0, 0
                    foreground_color: 0, 0, 0, 1
                    hint_text_color: 0.6, 0.6, 0.6, 1
                    cursor_color: 0, 0, 0, 1
                    multiline: False
                    size_hint_y: 1
                    padding: ["10dp", (self.height - self.line_height) / 2, 0, 0]

            # BOTÃO DE CONTINUAR (BLINDADO)
            MDFlatButton:
                text: "Continue"
                md_bg_color: 0, 0, 0, 1
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_x: 1
                padding: "15dp"
                radius: [8, 8, 8, 8]  # <-- A cura da ondinha!
                on_release: root.login_click()

            # ESPAÇO DE FEEDBACK DE ERRO
            MDLabel:
                id: error_text
                text: ""
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                size_hint_y: None
                height: self.texture_size[1]

        # PARTE INFERIOR
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: 0.35
            # AQUI: Aumentamos o 10dp para 30dp para afastar mais do bloco de cima!
            padding: ["20dp", "30dp", "20dp", "20dp"] 
            spacing: "10dp"
            md_bg_color: 1, 1, 1, 1

            MDTextButton:
                text: "Esqueci minha senha"
                theme_text_color: "Custom"
                text_color: 0.1, 0.46, 0.82, 1
                font_size: "12sp"
                bold: True
                pos_hint: {"center_x": .5}
                on_release: root.go_forgot()

            Widget:
                size_hint_y: None
                height: "5dp"

            # LINHAS LATERAIS E A PALAVRA "OU"
            MDBoxLayout:
                orientation: "horizontal"
                adaptive_height: True
                spacing: "10dp"
                pos_hint: {"center_x": .5}
                
                MDBoxLayout:
                    size_hint_y: None
                    height: "1dp"
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    pos_hint: {"center_y": .5}
                
                MDLabel:
                    text: "ou"
                    halign: "center"
                    theme_text_color: "Hint"
                    font_size: "12sp"
                    adaptive_width: True
                    pos_hint: {"center_y": .5}

                MDBoxLayout:
                    size_hint_y: None
                    height: "1dp"
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    pos_hint: {"center_y": .5}

            Widget:
                size_hint_y: None
                height: "5dp"

            MDRectangleFlatIconButton:
                icon: "google"
                text: "Continue com Google"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                icon_color: 0.85, 0.19, 0.16, 1
                line_color: 0.96, 0.96, 0.96, 1
                md_bg_color: 0.96, 0.96, 0.96, 1
                size_hint_x: 1
                radius: [8, 8, 8, 8]  # <-- A cura da ondinha!
                on_release: root.login_google()

            Widget:
                size_hint_y: None
                height: "10dp"

            MDLabel:
                text: "Ao clicar em continuar, você aceita nossos\\n[b]Termos de Serviço[/b] e [b]Política de Privacidade[/b]"
                markup: True
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Hint"
                font_size: "11.5sp"

            MDBoxLayout:
                orientation: "horizontal"
                adaptive_size: True
                pos_hint: {"center_x": .5}
                spacing: "4dp"

                MDLabel:
                    text: "Não possui uma conta?"
                    theme_text_color: "Hint"
                    font_size: "12sp"
                    adaptive_width: True
                    pos_hint: {"center_y": .5}

                MDTextButton:
                    text: "Crie sua conta aqui"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.46, 0.82, 1
                    font_size: "12sp"
                    bold: True
                    pos_hint: {"center_y": .5}
                    on_release: root.go_register()
'''
# O Builder carrega o visual para a memória
Builder.load_string(KV_LOGIN)

# A Lógica da Tela
class LoginScreen(MDScreen):
    def on_pre_enter(self, *args):
        # 1. Limpa os campos de texto
        if 'email_field' in self.ids:
            self.ids.email_field.text = ""
        if 'password_field' in self.ids:
            self.ids.password_field.text = ""
            
        # 2. Apaga a mensagem estática
        if 'error_text' in self.ids:
            self.ids.error_text.text = ""

    def login_click(self):
        email = self.ids.email_field.text
        senha = self.ids.password_field.text

        if not email or not senha:
            self.mostrar_erro("Preencha todos os campos", "red")
            return

        self.mostrar_erro("Conectando...", "blue")
        threading.Thread(target=self.fazer_requisicao_login, args=(email, senha)).start()

    def fazer_requisicao_login(self, email, senha):
        try:
            response = requests.post(
                f"{config.API_URL}/api/token/", 
                data={"username": email, "password": senha}, 
                headers=HEADERS
            )
            if response.status_code == 200:
                data = response.json()
                store.put("session", token=data.get("access"))
                self.mostrar_erro("Login efetuado! Redirecionando...", "green")

                Clock.schedule_once(lambda dt: self.ir_para_home(), 1)
            else:
                self.mostrar_erro("Email ou senha incorretos.", "red")
        except Exception as ex:
            self.mostrar_erro(f"Erro: {ex}", "red")

    def login_google(self):
        try:
            my_login_id = str(uuid.uuid4())
            webbrowser.open(f"{config.API_URL}/api/start-login/?login_id={my_login_id}")
            self.mostrar_erro("Aguardando navegador...", "blue")
            threading.Thread(target=self.check_google_status, args=(my_login_id,), daemon=True).start()
        except Exception as ex:
            self.mostrar_erro("Erro ao abrir Google", "red")

    def check_google_status(self, login_id):
        for _ in range(30):
            time.sleep(2)
            try:
                res = requests.get(f"{config.API_URL}/api/check-login/?login_id={login_id}", headers=HEADERS)
                if res.status_code == 200 and res.json().get('status') == 'success':
                    store.put("session", token=res.json().get('access_token'))
                    self.mostrar_erro("Conectado! Redirecionando...", "green")
                    Clock.schedule_once(lambda dt: self.ir_para_home(), 1)
                    return
            except: pass
        self.mostrar_erro("Tempo limite esgotado.", "red")

    @mainthread
    def mostrar_erro(self, texto, cor):
        self.ids.error_text.text = texto
        cores = {"red": (1,0,0,1), "blue": (0,0,1,1), "green": (0,0.5,0,1)}
        self.ids.error_text.text_color = cores.get(cor, (0,0,0,1))

    # --- NAVEGAÇÃO ---
    def go_register(self):
        self.manager.current = 'register'

    def go_forgot(self):
        self.manager.current = 'forgot_password'
        
    def ir_para_home(self):
        self.manager.current = 'home'