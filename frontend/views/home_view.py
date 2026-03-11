from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
# Importamos a classe para o Python conhecer, e pro KV importar
from views.tabs.home_tab import HomeTabContent
from views.tabs.new_tab import NewTabContent
from views.tabs.explore_tab import ExploreTabContent

KV_HOME_VIEW = '''
# A MAGIA DO KIVY PARA MODULARIZAÇÃO:
#:import HomeTabContent views.tabs.home_tab.HomeTabContent
#:import ProfileTabContent views.tabs.profile_tab.ProfileTabContent

<HomeScreen>:
    md_bg_color: 0.96, 0.96, 0.96, 1

    MDBoxLayout:
        orientation: "vertical"

        # 1. O HEADER (Cabeçalho superior)
        MDBoxLayout:
            size_hint_y: None   
            height: "60dp"
            padding: ["15dp", "0dp", "15dp", "0dp"]
            md_bg_color: 0.22, 0.75, 0.94, 1  # Cor #39BFEF
            elevation: 2

            Image:
                source: "assets/images/logo-sem-fundo.png"
                size_hint: None, None
                size: "40dp", "40dp"
                pos_hint: {"center_y": .5}

            MDLabel:
                text: "VigiAA"
                font_size: "22sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                valign: "center"
                padding_x: "10dp"

            MDIconButton:
                icon: "bell-outline"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                pos_hint: {"center_y": .5}

        # 2. A NAVEGAÇÃO INFERIOR
        MDBottomNavigation:
            id: bottom_nav
            selected_color_background: 0, 0, 0, 0
            text_color_active: 0.22, 0.75, 0.94, 1  # Azul ciano quando selecionado

            # ABA 1: INÍCIO
            MDBottomNavigationItem:
                name: 'tab_home'
                text: 'Início'
                icon: 'home'
                
                # INJETAMOS O ARQUIVO EXTERNO AQUI (Lego)
                HomeTabContent:

            # ABA 2: NOVO
            MDBottomNavigationItem:
                name: 'tab_new'
                text: 'Novo'
                icon: 'plus-circle-outline'
                
                # INJETAMOS OS NOSSOS CARTÕES AQUI
                NewTabContent:

            # ABA EXPLORAR (Pode ser a Aba 3 no seu código)
            MDBottomNavigationItem:
                name: 'tab_explore'
                text: 'Explorar'
                icon: 'compass'

                # INJETAMOS A NOSSA ABA NOVA AQUI
                ExploreTabContent:

            # ABA 4: PERFIL
            MDBottomNavigationItem:
                name: 'tab_profile'
                text: 'Perfil'
                icon: 'account'
                on_tab_release: profile_tab.refresh_data()

                ProfileTabContent:
                    id: profile_tab
'''
Builder.load_string(KV_HOME_VIEW)

class HomeScreen(MDScreen):
    def on_pre_enter(self, *args):
        # 1. Força o aplicativo a voltar para a primeira aba (Início)
        self.ids.bottom_nav.switch_tab('tab_home')
        
        # 2. Manda a aba de perfil carregar os dados silenciosamente no fundo
        if 'profile_tab' in self.ids:
            self.ids.profile_tab.refresh_data()