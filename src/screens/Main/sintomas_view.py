from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.app import MDApp
# Importa o degradê que você criou na Home para manter o padrão visual
from views.home_view import HorizontalGradientLayout

KV_SINTOMAS = '''
# --- COMPONENTE REUTILIZÁVEL PARA OS CARDS ---
<SintomaCard@MDCard>:
    image: ""
    text: ""
    orientation: "vertical"
    size_hint_y: None
    height: "130dp"
    radius: [15, 15, 15, 15]
    padding: "5dp"
    spacing: "2dp" # Diminuímos o espaçamento entre imagem e texto
    elevation: 1
    md_bg_color: 1, 1, 1, 1

    FitImage:
        source: root.image
        radius: [10, 10, 10, 10]
        # AGORA A IMAGEM OCUPA 80% DO CARD
        size_hint_y: 0.8 

    MDLabel:
        text: root.text
        halign: "center"
        valign: "center"
        font_size: "10sp"
        theme_text_color: "Primary"
        # O TEXTO FICA COM OS 20% RESTANTES
        size_hint_y: 0.2 
        text_size: self.width, None

<SintomasView>:
    md_bg_color: 1, 1, 1, 1
    orientation: "vertical"

    # --- CABEÇALHO DEGRADÊ PADRÃO DO VIGIAA ---
    HorizontalGradientLayout:
        size_hint_y: None   
        height: "80dp" 
        padding: ["5dp", "0dp", "15dp", "0dp"]

        MDBoxLayout:
            orientation: "horizontal"
            adaptive_height: True
            pos_hint: {"center_y": .5}
            md_bg_color: 0, 0, 0, 0 

            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1 # Ícone preto para contrastar com o degradê claro
                pos_hint: {"center_y": .5}
                on_release: root.go_back()

            MDLabel:
                text: "Sintomas"
                font_size: "22sp"
                bold: True
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1 # Texto preto
                valign: "center"
                halign: "left"
                padding_x: "10dp"
                
            Widget: # Empurra o título e o botão para a esquerda
    # ------------------------------------------

    ScrollView:
        do_scroll_x: False
        
        MDBoxLayout:
            orientation: "vertical"
            padding: "15dp"
            spacing: "20dp"
            adaptive_height: True

            # --- BOX INFORMATIVO (AZUL CLARO) ---
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: "15dp"
                radius: [15, 15, 15, 15]
                md_bg_color: 0.88, 0.97, 0.98, 1
                
                MDLabel:
                    text: "Ao sentir alguns desses sintomas, procure uma Unidade de Saúde e não tome remédio por conta própria."
                    font_size: "13sp"
                    bold: True
                    adaptive_height: True

            # --- SEÇÃO 1: PRINCIPAIS SINTOMAS ---
            MDLabel:
                text: "Principais sintomas da Dengue:"
                bold: True
                font_size: "16sp"
                adaptive_height: True

            MDGridLayout:
                cols: 3
                spacing: "10dp"
                adaptive_height: True

                SintomaCard:
                    image: "assets/images/termometro.png" 
                    text: "Febre"
                SintomaCard:
                    image: "assets/images/dores.jpeg"
                    text: "Dores no corpo e/ ou articulações"
                SintomaCard:
                    image: "assets/images/enjoo.jpg"
                    text: "Enjoo e/ou dores na barriga"
                SintomaCard:
                    image: "assets/images/dor-cabeca.jpg"
                    text: "Dor de cabeça e/ou atrás dos olhos"
                SintomaCard:
                    image: "assets/images/manchas.jpeg"
                    text: "Manchas vermelhas na pele"
                SintomaCard:
                    image: "assets/images/fraqueza.png"
                    text: "Fraqueza, cansaço e falta de energia"

            # --- SEÇÃO 2: SINAIS DE ALERTA ---
            MDLabel:
                text: "Sinais de alerta:"
                bold: True
                font_size: "16sp"
                adaptive_height: True

            MDGridLayout:
                cols: 3
                spacing: "10dp"
                adaptive_height: True

                SintomaCard:
                    image: "assets/images/cansaco.jpg"
                    text: "Cansaço intenso"
                SintomaCard:
                    image: "assets/images/dor-barriga.jpg"
                    text: "Dor forte na barriga"
                SintomaCard:
                    image: "assets/images/respirar.jpg"
                    text: "Dificuldade para respirar"
                SintomaCard:
                    image: "assets/images/vomitos.jpg"
                    text: "Vômitos"
                SintomaCard:
                    image: "assets/images/tontura.png"
                    text: "Tontura / sensação de desmaio"
                SintomaCard:
                    image: "assets/images/sangramento.jpg"
                    text: "Sangramento no nariz, gengiva e/ou fezes"

            # Espaçamento no final para a Bottom Navigation não cobrir o conteúdo
            Widget:
                size_hint_y: None
                height: "80dp"
'''

Builder.load_string(KV_SINTOMAS)

class SintomasView(MDBoxLayout):
    def go_back(self):
        # Obtém a instância do app e volta para a tela principal (home)
        app = MDApp.get_running_app()
        app.root.current = 'home'