import traceback
import os
import sys
import textwrap
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore

# O store continua aqui em cima
store = JsonStore('sessao_app.json')

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    from kivy.uix.screenmanager import ScreenManager
    from kivy.lang import Builder

    # --- A VERDADEIRA VACINA ANTI-CRASH ---
    vacina_kv = textwrap.dedent('''
        <MDDropdownMenu>:
            radius: [8, 8, 8, 8]
            
        <OverFlowMenu>:
            radius: [8, 8, 8, 8]
    ''')
    Builder.load_string(vacina_kv)
    # --------------------------------------

    from views.login_view import LoginScreen
    from views.home_view import HomeScreen
    from views.change_password_view import ChangePasswordScreen
    from views.forgot_password_view import ForgotPasswordScreen
    from views.register_view import RegisterScreen
    from views.forms.focus_form_view import FocusFormScreen
    from views.forms.case_form_view import CaseFormScreen
    from views.forms.positive_case_form_view import PositiveCaseFormScreen

    class VigiAA(MDApp):
        def build(self):
            # --- TRAVA DE REINSTALAÇÃO (LIMPEZA DE CACHE) ---
            # Caminho para um arquivo oculto que indica que o app já rodou
            flag_file = os.path.join(self.user_data_dir, '.instalação_confirmada')
            
            if not os.path.exists(flag_file):
                # Se o arquivo não existe, é a primeira vez que roda após instalar
                store.clear()  # Limpa qualquer sessão restaurada pelo Google Backup
                # Cria o arquivo para as próximas aberturas
                with open(flag_file, 'w') as f:
                    f.write('confirmado')
                print("VIGIAA DEBUG: Instalação limpa detectada. Sessão resetada.")
            # -----------------------------------------------

            self.theme_cls.primary_palette = "Green"
            self.theme_cls.theme_style = "Light"

            sm = ScreenManager()
            sm.add_widget(LoginScreen(name='login'))
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(ChangePasswordScreen(name='change_password'))
            sm.add_widget(ForgotPasswordScreen(name='forgot_password'))
            sm.add_widget(RegisterScreen(name='register'))
            sm.add_widget(FocusFormScreen(name='form_foco'))
            sm.add_widget(CaseFormScreen(name='form_caso'))
            sm.add_widget(PositiveCaseFormScreen(name='form_caso_positivo'))

            sm.current = 'login'
            return sm

    if __name__ == '__main__':
        VigiAA().run()

except Exception as e:
    from kivy.uix.label import Label
    from kivy.core.window import Window
    
    class ErrorApp(MDApp):
        def build(self):
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
            msg_erro = traceback.format_exc()
            return Label(text=f"ERRO FATAL CAPTURADO:\n\n{msg_erro}", 
                         font_size='12sp', color=(1, 0.3, 0.3, 1), 
                         text_size=(Window.width * 0.9, None), halign='left', valign='top')
            
    if __name__ == '__main__':
        ErrorApp().run()