import traceback

try:
    # --- INÍCIO DO CÓDIGO DO SEU APP ---
    from kivymd.app import MDApp
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen

    # Usando string pura para evitar erros de não achar o arquivo .kv no celular
    KV = '''
ScreenManager:
    LoginScreen:
    ExplorarScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint_y: None
        height: self.minimum_height

        MDLabel:
            text: "VigiAA - Teste de APK!"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Primary"

        MDRaisedButton:
            text: "ENTRAR NO APP"
            pos_hint: {"center_x": .5}
            on_release: app.root.current = "explorar"

<ExplorarScreen>:
    name: "explorar"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Aba Explorar"
            anchor_title: "left"
            elevation: 2
        
        MDLabel:
            text: "Se você chegou aqui, o app não crashou!"
            halign: "center"

        MDRaisedButton:
            text: "Voltar para Login"
            pos_hint: {"center_x": .5}
            on_release: app.root.current = "login"
        
        Widget:
            # Espaçador
    '''

    class LoginScreen(Screen):
        pass

    class ExplorarScreen(Screen):
        pass

    class VigiAA(MDApp):
        def build(self):
            self.theme_cls.primary_palette = "Green"
            return Builder.load_string(KV)

    if __name__ == '__main__':
        VigiAA().run()
    # --- FIM DO CÓDIGO DO SEU APP ---

except Exception as e:
    # --- SE DER ERRO, A TELA PRETA DA MORTE APARECE COM O CULPADO ---
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.core.window import Window
    
    class ErrorApp(App):
        def build(self):
            Window.clearcolor = (0.1, 0.1, 0.1, 1) # Fundo cinza escuro
            msg_erro = traceback.format_exc()
            return Label(text=f"ERRO FATAL NO ANDROID:\n\n{msg_erro}", 
                         font_size='12sp', 
                         color=(1, 0.3, 0.3, 1), 
                         text_size=(Window.width * 0.9, None),
                         halign='left', valign='top')
            
    if __name__ == '__main__':
        ErrorApp().run()