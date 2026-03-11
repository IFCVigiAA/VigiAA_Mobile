from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock

# O visual exclusivo do conteúdo da Aba Início
KV_HOME_TAB = '''
<StatCard@MDCard>:
    orientation: "vertical"
    padding: "15dp"
    spacing: "2dp"
    radius: [10, 10, 10, 10]
    elevation: 1
    shadow_color: 0, 0, 0, 0.1  # <-- SOMBRA SUAVE
    md_bg_color: 1, 1, 1, 1
    title: ""
    value: ""
    subtext: ""
    
    MDLabel:
        text: root.title
        font_size: "13sp"
        bold: True
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        halign: "left"  # <-- ALINHADO À ESQUERDA
        
    MDLabel:
        text: root.value
        font_size: "26sp"
        bold: True
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        halign: "left"  # <-- ALINHADO À ESQUERDA
        
    MDLabel:
        text: root.subtext
        font_size: "11sp"
        theme_text_color: "Custom"
        text_color: 0.5, 0.5, 0.5, 1
        halign: "left"  # <-- ALINHADO À ESQUERDA

<ChartCard@MDCard>:
    orientation: "vertical"
    padding: "20dp"
    spacing: "10dp"
    radius: [10, 10, 10, 10]
    elevation: 1
    shadow_color: 0, 0, 0, 0.1  # <-- SOMBRA SUAVE
    md_bg_color: 1, 1, 1, 1
    title: ""
    image_src: ""
    size_hint_y: None
    height: "280dp"

    MDLabel:
        text: root.title
        font_size: "16sp"
        bold: True
        adaptive_height: True
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1

    Image:
        source: root.image_src
        allow_stretch: True
        keep_ratio: True

<YearButton>:
    size_hint: None, None
    size: "80dp", "40dp"
    radius: [20, 20, 20, 20]
    elevation: 1 if not root.is_selected else 0
    shadow_color: 0, 0, 0, 0.1  # <-- SOMBRA SUAVE
    md_bg_color: (0, 0, 0, 1) if root.is_selected else (1, 1, 1, 1)
    
    MDLabel:
        text: root.year_text
        halign: "center"
        valign: "center"
        bold: True
        theme_text_color: "Custom"
        text_color: (1, 1, 1, 1) if root.is_selected else (0, 0, 0, 1)

<HomeTabContent>:
    do_scroll_x: False
    do_scroll_y: True

    MDBoxLayout:
        orientation: "vertical"
        padding: "15dp"
        spacing: "15dp"
        adaptive_height: True

        # Filtro de Anos (Scroll Horizontal)
        ScrollView:
            size_hint_y: None
            height: "50dp"
            do_scroll_x: True
            do_scroll_y: False
            bar_width: 0
            
            MDBoxLayout:
                id: year_container
                orientation: "horizontal"
                adaptive_width: True
                spacing: "10dp"
                padding: ["0dp", "5dp", "0dp", "5dp"]

        # Cards de Estatísticas
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "100dp"
            spacing: "10dp"

            StatCard:
                title: "Casos confirmados"
                value: "457"
                subtext: "+20 este mês"

            StatCard:
                title: "Suspeitas de dengue"
                value: "2,405"
                subtext: "+300 este mês"

        # Gráficos
        ChartCard:
            title: "Casos confirmados por mês"
            image_src: "assets/images/grafico1.png" 

        ChartCard:
            title: "Proporção de focos por tipo"
            image_src: "assets/images/grafico2.png"
'''
Builder.load_string(KV_HOME_TAB)

class YearButton(MDCard):
    is_selected = BooleanProperty(False)
    year_text = StringProperty("")
    callback = ObjectProperty(None) # Guarda a função que deve ser ativada ao clicar
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=self.on_click)
        
    def on_click(self, *args):
        if self.callback:
            self.callback(self)

# Este é o container principal que a HomeView vai importar
class HomeTabContent(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.year_buttons = []
        # Espera o visual carregar e preenche os botões
        Clock.schedule_once(self.populate_years, 0)

    def populate_years(self, dt):
        anos = ["2025", "2024", "2023"]
        for i, ano in enumerate(anos):
            # Passa a função 'change_year' de forma limpa, sem usar 'parent.parent...'
            btn = YearButton(year_text=ano, is_selected=(i == 0), callback=self.change_year)
            self.year_buttons.append(btn)
            self.ids.year_container.add_widget(btn)

    def change_year(self, clicked_btn):
        for btn in self.year_buttons:
            btn.is_selected = False
        clicked_btn.is_selected = True
        print(f"Ano selecionado: {clicked_btn.year_text}")