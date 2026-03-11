from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivymd.app import MDApp

# O Visual da Aba "Novo"
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
            font_size: "24sp"
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
            elevation: 2
            md_bg_color: 1, 1, 1, 1
            on_release: root.go_to_foco()

            # Imagem no topo do card
            FitImage:
                source: "assets/images/focos.jpg"
                size_hint_y: 0.55
                radius: [15, 15, 0, 0]

            # Área de texto e botão do card
            MDRelativeLayout:
                size_hint_y: 0.45
                
                MDBoxLayout:
                    orientation: "vertical"
                    padding: ["15dp", "10dp", "60dp", "10dp"] # Espaço na direita pro botão flutuar
                    spacing: "5dp"

                    MDLabel:
                        text: "Cadastrar novo foco"
                        font_size: "16sp"
                        bold: True
                        adaptive_height: True

                    MDLabel:
                        text: "Forneça informações sobre um local com possíveis focos do mosquito."
                        theme_text_color: "Hint"
                        font_size: "13sp"
                        adaptive_height: True
                        
                # Botão Redondo (+) flutuando em cima da borda
                MDFloatingActionButton:
                    icon: "plus"
                    md_bg_color: 0.22, 0.75, 0.94, 1 # Azul Ciano
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    elevation: 1
                    pos_hint: {"right": 0.95, "center_y": 0.5}
                    on_release: root.go_to_foco()

        # --- CARD 2: PACIENTE ---
        MDCard:
            orientation: "vertical"
            size_hint_y: None
            height: "260dp"
            radius: [15, 15, 15, 15]
            elevation: 2
            md_bg_color: 1, 1, 1, 1
            on_release: root.go_to_caso()

            # Imagem no topo do card
            FitImage:
                source: "assets/images/paciente.jpg"
                size_hint_y: 0.55
                radius: [15, 15, 0, 0]

            # Área de texto e botão do card
            MDRelativeLayout:
                size_hint_y: 0.45
                
                MDBoxLayout:
                    orientation: "vertical"
                    padding: ["15dp", "10dp", "60dp", "10dp"]
                    spacing: "5dp"

                    MDLabel:
                        text: "Cadastrar novo paciente"
                        font_size: "16sp"
                        bold: True
                        adaptive_height: True

                    MDLabel:
                        text: "Forneça informações necessárias para o cadastro de um paciente."
                        theme_text_color: "Hint"
                        font_size: "13sp"
                        adaptive_height: True
                        
                # Botão Redondo (+) flutuando em cima da borda
                MDFloatingActionButton:
                    icon: "plus"
                    md_bg_color: 0.22, 0.75, 0.94, 1 # Azul Ciano
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    elevation: 1
                    pos_hint: {"right": 0.95, "center_y": 0.5}
                    on_release: root.go_to_caso()

        # Espaçamento no fundo para o menu inferior não engolir o último card
        MDBoxLayout:
            size_hint_y: None
            height: "80dp"
'''
Builder.load_string(KV_NEW_TAB)

class NewTabContent(ScrollView):
    def go_to_foco(self):
        # Acha o maestro do app e manda mudar para a tela de Formulário de Foco
        MDApp.get_running_app().root.current = 'form_foco'

    def go_to_caso(self):
        # Acha o maestro do app e manda mudar para a tela de Formulário de Paciente
        MDApp.get_running_app().root.current = 'form_caso'