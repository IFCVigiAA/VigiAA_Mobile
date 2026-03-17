import traceback
import os
import sys

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    from kivymd.app import MDApp
    from kivy.uix.screenmanager import ScreenManager

    from views.login_view import LoginScreen
    from views.home_view import HomeScreen
    from views.change_password_view import ChangePasswordScreen
    from views.forgot_password_view import ForgotPasswordScreen
    from views.register_view import RegisterScreen
    from views.forms.focus_form_view import FocusFormScreen
    from views.forms.case_form_view import CaseFormScreen

    class VigiAA(MDApp):
        def build(self):
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

            sm.current = 'login'

            return sm

    if __name__ == '__main__':
        VigiAA().run()

except Exception as e:
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.core.window import Window
    
    class ErrorApp(App):
        def build(self):
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
            msg_erro = traceback.format_exc()
            return Label(text=f"ERRO FATAL CAPTURADO:\n\n{msg_erro}", 
                         font_size='12sp', color=(1, 0.3, 0.3, 1), 
                         text_size=(Window.width * 0.9, None), halign='left', valign='top')
            
    if __name__ == '__main__':
        ErrorApp().run()