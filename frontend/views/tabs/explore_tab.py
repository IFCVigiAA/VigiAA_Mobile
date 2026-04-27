from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.fitimage import FitImage
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.factory import Factory

# Textos formatados
LINK_COLOR = "0077B6"
SHORT_INFO_TEXT = f"A [b]dengue[/b] é uma arbovirose... [ref=more][color={LINK_COLOR}]ler mais...[/color][/ref]"
FULL_INFO_TEXT = f"A [b]dengue[/b] é uma arbovirose causada pelo mosquito Aedes aegypti. [ref=less][color={LINK_COLOR}]ler menos[/color][/ref]"

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

            # --- CARROSSEL COM DESIGN AJUSTADO ---
            MDRelativeLayout:
                size_hint_y: None
                height: "180dp"
                
                MDCard:
                    size_hint: 1, 1
                    radius: [20, 20, 20, 20]
                    elevation: 1
                    padding: 0
                    clip_to_bounds: True # Corta o conteúdo na curva
                    md_bg_color: 1, 1, 1, 1

                    MDSwiper:
                        id: swiper
                        size_hint: 1, 1
                        width_mult: 1
                        items_spacing: 0
                        show_pagination: True
                        radius: [20, 20, 20, 20]

                        # --- SLIDE 1 ---
                        MDSwiperItem:
                            size_hint: 1, 1
                            MDRelativeLayout:
                                FitImage:
                                    source: "assets/images/banner1.jpeg"
                                    size_hint: 1, 1
                                    radius: [20, 20, 20, 20]
                                
                                MDBoxLayout:
                                    size_hint_y: None
                                    height: "50dp"
                                    pos_hint: {"bottom": 0}
                                    md_bg_color: 0, 0, 0, 0.6
                                    # Acompanha o radius inferior do card
                                    radius: [0, 0, 20, 20] 
                                    padding: ["60dp", 0, "10dp", 0] 
                                    
                                    MDLabel:
                                        text: "O mosquito não descansa!"
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1
                                        bold: True
                                        halign: "left"
                                        valign: "center"
                                        text_size: self.size

                        # --- SLIDE 2 ---
                        MDSwiperItem:
                            size_hint: 1, 1
                            MDRelativeLayout:
                                FitImage:
                                    source: "assets/images/agentes.jpeg"
                                    size_hint: 1, 1
                                    radius: [20, 20, 20, 20]
                                
                                MDBoxLayout:
                                    size_hint_y: None
                                    height: "50dp"
                                    pos_hint: {"bottom": 0}
                                    md_bg_color: 0, 0, 0, 0.6
                                    # Acompanha o radius inferior do card
                                    radius: [0, 0, 20, 20]
                                    # Texto ainda mais para a direita para segurança total
                                    padding: ["60dp", 0, "10dp", 0]
                                    
                                    MDLabel:
                                        text: "Agentes em combate"
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1
                                        bold: True
                                        halign: "left"
                                        valign: "center"
                                        text_size: self.size

                # SETAS LATERAIS
                MDIconButton:
                    icon: "chevron-left"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    md_bg_color: 0, 0, 0, 0.3
                    pos_hint: {"left": 0, "center_y": .5}
                    on_release: swiper.swipe_left()

                MDIconButton:
                    icon: "chevron-right"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    md_bg_color: 0, 0, 0, 0.3
                    pos_hint: {"right": 1, "center_y": .5}
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
                TwoLineAvatarIconListItem:
                    text: "Sintomas"
                    secondary_text: "Conheça os sinais"
                    on_release: root.go_to_route('sintomas')
                    IconLeftWidget:
                        icon: "thermometer"
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