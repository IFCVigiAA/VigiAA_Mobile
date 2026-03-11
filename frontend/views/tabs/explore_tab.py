from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import BooleanProperty

# O Visual da Aba "Explorar"
KV_EXPLORE_TAB = '''
<ExploreTabContent>:
    md_bg_color: 1, 1, 1, 1

    ScrollView:
        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "25dp"
            adaptive_height: True

            # 1. Banner do Topo
            MDCard:
                size_hint_y: None
                height: "180dp"
                radius: [15, 15, 15, 15]
                elevation: 2
                
                FitImage:
                    source: "assets/images/banner1.jpeg"
                    radius: [15, 15, 15, 15]

            # 2. Caixa de Texto Azul (Informativo da Dengue)
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: "20dp"
                spacing: "5dp"
                radius: [15, 15, 15, 15]
                md_bg_color: 0.88, 0.97, 0.98, 1 # Azul claro (#E0F7FA)

                MDLabel:
                    id: text_description
                    text: "A dengue é uma arbovirose causada por vírus transmitidos principalmente pelo mosquito Aedes aegypti. Os principais sintomas são febre alta, erupções cutâneas e dores musculares e articulares. Em casos graves, pode haver hemorragia profusa e choque, podendo ser fatal. O tratamento inclui ingestão de líquidos e analgésicos."
                    font_size: "15sp"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.28, 0.31, 1 # Cinza Escuro (#37474F)
                    # Lógica para mostrar tudo ou apenas 3 linhas
                    shorten: not root.is_expanded
                    shorten_from: "right"
                    max_lines: 3 if not root.is_expanded else 0
                    adaptive_height: True

                MDTextButton:
                    id: btn_read_more
                    text: "ler mais..." if not root.is_expanded else "ler menos"
                    theme_text_color: "Custom"
                    text_color: 0, 0.47, 0.71, 1 # Azul link (#0077B6)
                    font_size: "14sp"
                    on_release: root.toggle_read_more()

            # 3. Lista de Acesso Rápido
            MDList:
                id: list_container
                spacing: "10dp"

                # Item 1: Sintomas
                TwoLineAvatarIconListItem:
                    text: "Sintomas"
                    secondary_text: "Conheça os sinais"
                    on_release: root.go_to_route('sintomas')
                    
                    IconLeftWidget:
                        # Usando um FitImage no lugar de um ícone genérico
                        FitImage:
                            source: "assets/images/termometro.jpg"
                            radius: [30, 30, 30, 30] # Deixa a imagem redondinha
                            
                    IconRightWidget:
                        icon: "chevron-right"

                # Item 2: Prevenção
                TwoLineAvatarIconListItem:
                    text: "Conheça as formas de prevenção"
                    secondary_text: "Saiba como se proteger"
                    on_release: root.go_to_route('prevencao')
                    
                    IconLeftWidget:
                        FitImage:
                            source: "assets/images/mosquito_proibido.png"
                            radius: [30, 30, 30, 30]
                            
                    IconRightWidget:
                        icon: "chevron-right"

                # Item 3: Campanhas
                TwoLineAvatarIconListItem:
                    text: "Campanhas"
                    secondary_text: "Ações da prefeitura"
                    on_release: root.go_to_route('campanhas')
                    
                    IconLeftWidget:
                        FitImage:
                            source: "assets/images/agentes.jpeg"
                            radius: [30, 30, 30, 30]
                            
                    IconRightWidget:
                        icon: "chevron-right"

            # Espaçamento no fundo para o menu inferior não engolir o último item
            MDBoxLayout:
                size_hint_y: None
                height: "80dp"
'''
Builder.load_string(KV_EXPLORE_TAB)

class ExploreTabContent(MDBoxLayout):
    # Controla o botão "ler mais"
    is_expanded = BooleanProperty(False)

    def toggle_read_more(self):
        self.is_expanded = not self.is_expanded

    def go_to_route(self, route_name):
        # Aqui você vai plugar as futuras telas de informações
        # Exemplo: MDApp.get_running_app().root.current = route_name
        print(f"Navegando para a rota: {route_name}")