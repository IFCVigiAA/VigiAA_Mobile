from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

from views.login_view import LoginScreen
from views.home_view import HomeScreen
from views.change_password_view import ChangePasswordScreen
from views.register_view import RegisterScreen
from views.forgot_password_view import ForgotPasswordScreen
from views.tabs.new_tab import NewTabContent

class VigiAAScreenManager(ScreenManager):
    pass

class VigiAAApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Cyan"
        sm = VigiAAScreenManager()
        
        # Coloque a home primeiro na lista para testar direto nela!
        sm.add_widget(HomeScreen(name='home')) 
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChangePasswordScreen(name='change_password'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ForgotPasswordScreen(name='forgot_password'))
        
        return sm

if __name__ == "__main__":
    VigiAAApp().run()