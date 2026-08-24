from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.fitimage import FitImage
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.factory import Factory
from kivymd.app import MDApp

# Textos formatados
LINK_COLOR = "0077B6"
SHORT_INFO_TEXT = f"A [b]dengue[/b] é uma arbovirose... [ref=more][color={LINK_COLOR}]ler mais...[/color][/ref]"
FULL_INFO_TEXT = f"A [b]dengue[/b] é uma arbovirose causada por um vírus transmitido pelo mosquito Aedes aegypti. [ref=less][color={LINK_COLOR}]ler menos[/color][/ref]"

Factory.register('MDSwiper', cls=MDSwiper)
Factory.register('MDSwiperItem', cls=MDSwiperItem)

KV_EXPLORE_TAB = '''
<ExploreTabContent>:
    md_bg_color: 1, 1, 1, 1
    orientation: "vertical"

    ScrollView:
        do_scroll_x: False
        MDBoxLayout:
            orientation: "vertical"
            padding: "15dp"
            spacing: "20dp"
            adaptive_height: True

            # --- CARROSSEL COM BORDAS ARREDONDADAS E RESPIRO LATERAL ---
            MDRelativeLayout:
                size_hint_y: None
                height: "180dp"
                
                # Container visual que corta as bordas perfeitamente em todas as pontas
                MDBoxLayout:
                    size_hint: 1, 1
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    radius: [20, 20, 20, 20]
                    clip_to_bounds: True
                    md_bg_color: 1, 1, 1, 1

                    MDSwiper:
                        id: swiper
                        size_hint: 1, 1
                        
                        width_mult: 1

                        # --- SLIDE 1 ---
                        MDSwiperItem:
                            
                            
                            MDRelativeLayout:
                                size_hint: 1, 1
                                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                    
                                FitImage:
                                    source: "assets/images/banner1.jpeg"
                                    size_hint: 0.95, 1
                                    radius: [20, 20, 20, 20]
                                    
                                    
                                MDBoxLayout:
                                    size_hint: 0.95, None
                                    height: "50dp"
                                    
                                    md_bg_color: 0, 0, 0, 0.6
                                    radius: [0, 0, 20, 20]
                                    padding: ["15dp", 0, 0, 0]
                                        
                                    MDLabel:
                                        text: "O mosquito não descansa!"
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1
                                        bold: True

                        # --- SLIDE 2 ---
                        MDSwiperItem:
                            
                            MDBoxLayout:
                                padding: ["-30dp", 0, "30dp", 0]

                                MDRelativeLayout:
                                    size_hint: 1, 1
                                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

                                    FitImage:
                                        source: "assets/images/agentes.jpeg"
                                        size_hint: 0.95, 1
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        radius: [20, 20, 20, 20]

                                    MDBoxLayout:
                                        size_hint: 0.95,None
                                        height: "50dp"
                                        pos_hint: {"center_x": 0.5, "y": 0}
                                        md_bg_color: 0, 0, 0, 0.6
                                        radius: [0, 0, 20, 20]
                                        padding: ["15dp", 0, 0, 0]
                                        
                                        MDLabel:
                                            text: "Agentes em combate"
                                            theme_text_color: "Custom"
                                            text_color: 1, 1, 1, 1
                                            bold: True

                # --- SETAS LATERAIS (FORA DO BOX PARA EVITAR ERRO DE CLIP) ---
                MDIconButton:
                    icon: "chevron-left"
                    pos_hint: {"left": 0.01, "center_y": .5}
                    on_release: swiper.swipe_left()

                MDIconButton:
                    icon: "chevron-right"
                    pos_hint: {"right": 0.99, "center_y": .5}
                    on_release: swiper.swipe_right()

            # --- BOX INFORMATIVO ---
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: "15dp"
                radius: [15, 15, 15, 15]
                md_bg_color: 0.88, 0.97, 0.98, 1
                MDLabel:
                    text: root.info_text
                    markup: True
                    adaptive_height: True
                    on_ref_press: root.process_info_link_press(args[1])

            # --- LISTA ---
            MDList:
                padding: 0
                spacing: "5dp"

                # Item: Sintomas
                TwoLineAvatarIconListItem:
                    text: "Sintomas"
                    secondary_text: "Conheça os sinais"
                    on_release: root.go_to_route('sintomas')
                    IconLeftWidget:
                        icon: "thermometer"
                    IconRightWidget:
                        icon: "chevron-right"

                # Item: Prevenção
                TwoLineAvatarIconListItem:
                    text: "Prevenção"
                    secondary_text: "Conheça as formas de evitar"
                    on_release: root.go_to_route('prevencao')
                    IconLeftWidget:
                        icon: "shield-check-outline"
                    IconRightWidget:
                        icon: "chevron-right"

                # Item: Campanhas
                TwoLineAvatarIconListItem:
                    text: "Campanhas"
                    secondary_text: "Fique por dentro das ações"
                    on_release: root.go_to_route('campanhas')
                    IconLeftWidget:
                        icon: "bullhorn-outline"
                    IconRightWidget:
                        icon: "chevron-right"

            Widget:
                size_hint_y: None
                height: "80dp"
'''

Builder.load_string(KV_EXPLORE_TAB)

class ExploreTabContent(MDBoxLayout):
    is_expanded = BooleanProperty(False)
    info_text = StringProperty(SHORT_INFO_TEXT)

    def process_info_link_press(self, ref_name):
        if ref_name == "more":
            self.info_text = FULL_INFO_TEXT
            self.is_expanded = True
        else:
            self.info_text = SHORT_INFO_TEXT
            self.is_expanded = False

    def go_to_route(self, route):
        print(f"DEBUG: Navegando para: {route}")
        app = MDApp.get_running_app()

        if route == 'sintomas':
            app.root.current = 'sintomas_screen'
            
        elif route == 'prevencao':
            print("Navegar para prevenção (Ainda não implementado)")
            
        elif route == 'campanhas':
            print("Navegar para campanhas (Ainda não implementado)")