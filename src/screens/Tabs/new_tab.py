from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.metrics import dp

KV_NEW_TAB = '''
<NewTabContent>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        adaptive_height: True

        MDLabel:
            text: "Cadastro"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1
            adaptive_height: True

        # --- CARD 1: FOCO DE DENGUE ---
        MDCard:
            orientation: "vertical"
            size_hint_y: None
            height: "260dp"
            radius: [15, 15, 15, 15]
            elevation: 1
            md_bg_color: 1, 1, 1, 1
            on_release: root.go_to_foco()

            FitImage:
                source: "assets/images/focos.jpg"
                size_hint_y: 0.55
                radius: [15, 15, 0, 0]

            MDRelativeLayout:
                size_hint_y: 0.45
                
                # Bloco de Texto CENTRALIZADO VERTICALMENTE
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    pos_hint: {"center_y": .5}
                    padding: ["15dp", "0dp", "80dp", "0dp"]
                    spacing: "2dp"

                    MDLabel:
                        text: "Cadastrar novo foco"
                        font_size: "17sp"
                        bold: True
                        adaptive_height: True

                    MDLabel:
                        text: "Forneça informações sobre focos do mosquito."
                        theme_text_color: "Secondary"
                        font_size: "13sp"
                        adaptive_height: True
                        
                # A BOLA AZUL PERFEITA (+)
                MDIconButton:
                    icon: "plus"
                    user_font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    size_hint: None, None
                    size: "50dp", "50dp"
                    # O segredo da bola: radius é a metade da altura
                    radius: [25, 25, 25, 25] 
                    pos_hint: {"right": 0.96, "center_y": 0.5}
                    on_release: root.go_to_foco()

        # --- CARD 2: PACIENTE ---
        MDCard:
            orientation: "vertical"
            size_hint_y: None
            height: "260dp"
            radius: [15, 15, 15, 15]
            elevation: 1
            md_bg_color: 1, 1, 1, 1
            on_release: root.go_to_caso()

            FitImage:
                source: "assets/images/paciente.jpg"
                size_hint_y: 0.55
                radius: [15, 15, 0, 0]

            MDRelativeLayout:
                size_hint_y: 0.45
                
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    pos_hint: {"center_y": .5}
                    padding: ["15dp", "0dp", "80dp", "0dp"]
                    spacing: "2dp"

                    MDLabel:
                        text: "Cadastrar novo paciente"
                        font_size: "17sp"
                        bold: True
                        adaptive_height: True

                    MDLabel:
                        text: "Forneça informações para o cadastro de um paciente."
                        theme_text_color: "Secondary"
                        font_size: "13sp"
                        adaptive_height: True
                        
                MDIconButton:
                    icon: "plus"
                    user_font_size: "24sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    size_hint: None, None
                    size: "50dp", "50dp"
                    radius: [25, 25, 25, 25]
                    pos_hint: {"right": 0.96, "center_y": 0.5}
                    on_release: root.go_to_caso()

        Widget:
            size_hint_y: None
            height: "100dp"
'''

Builder.load_string(KV_NEW_TAB)

class NewTabContent(ScrollView):
    def go_to_foco(self):
        MDApp.get_running_app().root.current = 'form_foco'

    def go_to_caso(self):
        MDApp.get_running_app().root.current = 'form_caso'