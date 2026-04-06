from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.list import OneLineListItem
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from plyer import filechooser
import requests
import threading
import unicodedata
from urllib.parse import quote
import os
import config
from plyer import gps
from kivy.utils import platform
from plyer import filechooser, camera
from kivy.app import App
import time
from kivy.properties import StringProperty


if platform == 'android':
    from android.permissions import request_permissions, Permission

store = JsonStore('sessao_app.json')

KV_FOCUS_FORM = '''
<ImageCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: "80dp"  # <-- TRAVA DE ALTURA: O Kivy não pode mais esmagar o cartão!
    spacing: "10dp"
    padding: "5dp"
    
    # AQUI ESTÁ A SUA FOTO REAL:
    Image:
        source: root.image_path
        size_hint: None, None
        size: "70dp", "70dp" # <-- Tamanho exato da miniatura
        allow_stretch: True
        keep_ratio: False    # <-- Preenche o quadrado ignorando bordas vazias
        
    MDBoxLayout:
        orientation: "vertical"
        pos_hint: {"center_y": .5}
        MDLabel:
            text: root.image_name
            font_style: "Caption"
            bold: True
            shorten: True
            shorten_from: "right"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1
        MDLabel:
            text: "Imagem Anexada"
            font_style: "Caption"
            theme_text_color: "Hint"
            
    MDIconButton:
        icon: "delete-outline"
        theme_text_color: "Error"
        pos_hint: {"center_y": .5}
        on_release: app.root.get_screen('form_foco').remove_image(root.image_path)

<FocusFormScreen>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"
        
        # --- Styled Top Bar (Fundo branco, texto e ícone pretos centralizados) ---
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1 # Fundo branco verbatim
            padding: ["10dp", "0dp", "10dp", "0dp"]
            spacing: "10dp"
            pos_hint: {"top": 1}
            
            # Adiciona linha separadora fina no fundo do header verbatim
            canvas.after:
                Color:
                    rgb: 0.8, 0.8, 0.8 # Cinza separador verbatim
                Line:
                    points: self.x, self.y, self.width, self.y
                    width: 1.1 # Thinner line like design

            MDIconButton:
                icon: "arrow-left" # Match design back arrow icon verbatim
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1 # Preto design color verbatim
                pos_hint: {"center_y": .5}
                on_release: root.go_back()

            MDLabel:
                text: "Focos de mosquitos" # Match design title text verbatim
                font_size: "20sp"
                bold: True
                halign: "center" # Centralizado design position verbatim
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1 # Preto design color verbatim
                pos_hint: {"center_y": .5}

            # Spacer para o truque de centralização verbatim design trick
            Widget:
                size_hint_x: None
                width: "48dp"

        # --- Main form contents in ScrollView (fills space between header and anchored bottom button) ---
        ScrollView:
            id: scroller
            MDBoxLayout:
                id: main_scrolling_content
                orientation: "vertical"
                md_bg_color: 1, 1, 1, 1
                padding: ["20dp", "20dp", "20dp", "20dp"] # Padding contents verbatim
                spacing: "5dp" # Tight spacing like design verbatim
                adaptive_height: True

                # --- GPS Button (Filled Blue, rounded corners, centered icon/text) ---
                # Usando especializado FillRoundFlatIconButton para ripple safety de botão arredondado preenchido
                MDFillRoundFlatIconButton:
                    id: btn_gps
                    text: "Capturar localização pelo GPS" # Match design text verbatim
                    icon: "map-marker-outline" # Match design map marker icon verbatim
                    md_bg_color: 0.22, 0.75, 0.94, 1 # Design light blue color verbatim
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1 # White verbatim
                    icon_color: 1, 1, 1, 1 # White verbatim
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.9 # Full width look, slightly smaller than screen width verbatim design look
                    radius: [15, 15, 15, 15] # Rounded corner style verbatim
                    # Retained logic from before
                    on_release: root.start_location()

                # Corrigido typo: marcos -> marcados (verbatim design color hint)
                MDLabel:
                    text: "Campos marcados com * são obrigatórios"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)

                # --- FORM ROWS (Tabular Style, explicit styling verbatim to match unstyled transparent looks design_2) ---
                # Utilizando BoxLayouts customizados e TextInputs transparentes para obter o visual tabular design verbatim
                
                # CEP Row
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "CEP"
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed label width on left design verbatim
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_cep
                        hint_text: "Digite o CEP" # design hint text verbatim
                        input_filter: "int"
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2] # Center vertically
                        on_text: root.on_cep_change(self.text)

                # Município Row (Read-only input acting like dropdown)
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "MUNICÍPIO[color=#FF0000]*[/color]" # Red asterisk verbatim
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed width design verbatim
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_city
                        hint_text: "Selecione a cidade" # design hint text verbatim
                        readonly: True # Act like dropdown
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2] # Center vertically
                        # retained logic
                        on_focus: if self.focus: root.open_city_menu()
                    MDIconButton:
                        icon: "chevron-down" # design dropdown arrow verbatim
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1 # design color hint verbatim
                        pos_hint: {"center_y": .5}
                        on_release: root.open_city_menu()

                # Bairro Row (Read-only input acting like dropdown)
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "BAIRRO[color=#FF0000]*[/color]" # Red asterisk verbatim
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed width design verbatim
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_neighborhood
                        hint_text: "Selecione o bairro" # design hint text verbatim
                        readonly: True # Act like dropdown
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2] # Center vertically
                        # retained logic
                        on_focus: if self.focus: root.open_neighborhood_menu()
                    MDIconButton:
                        icon: "chevron-down" # design dropdown arrow verbatim
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.6, 1 # design color hint verbatim
                        pos_hint: {"center_y": .5}
                        on_release: root.open_neighborhood_menu()

                # Rua Row (Input with search icon)
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "RUA[color=#FF0000]*[/color]" # Red asterisk verbatim
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed width design verbatim
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_street
                        hint_text: "Digite o nome da rua" # design hint text verbatim
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2] # Center vertically
                        on_text_validate: root.search_address_by_name()
                    MDIconButton:
                        id: btn_search_street
                        icon: "magnify" # design magnify search icon verbatim
                        theme_text_color: "Custom"
                        text_color: 0.22, 0.75, 0.94, 1 # design color verbatim
                        pos_hint: {"center_y": .5}
                        on_release: root.search_address_by_name()

                # Número Row (Input)
                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "NÚMERO[color=#FF0000]*[/color]" # Red asterisk verbatim
                        markup: True
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed width design verbatim
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_number
                        hint_text: "Digite o número" # design hint text verbatim
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, (self.height - self.line_height) / 2] # Center vertically

                # Descrição Row (Multiline Input)
                BoxLayout:
                    orientation: "horizontal"
                    adaptive_height: True
                    size_hint_y: None
                    height: "80dp" # Gives space for multiline hint verbatim design look
                    padding: [0, "10dp", 0, "10dp"] # Spacing vertically verbatim design look
                    MDLabel:
                        text: "DESCRIÇÃO" # design label verbatim
                        bold: True
                        size_hint_x: None
                        width: "120dp" # Fixed width design verbatim
                        pos_hint: {"top": 1} # Align to top of description block
                        theme_text_color: "Primary"
                    TextInput:
                        id: tf_description
                        hint_text: "Descreva a situação do local. Obs: não se identifique de nenhuma forma" # design multiline hint text verbatim
                        multiline: True
                        # Custom transparent look design verbatim
                        hint_text_color: 0.6, 0.6, 0.6, 1
                        foreground_color: 0, 0, 0, 1
                        background_normal: ""
                        background_color: 0, 0, 0, 0
                        padding: [0, "10dp"] # Center vertically within its space

                # --- IMAGENS SECTION ---
                MDLabel:
                    text: "IMAGENS"
                    bold: True
                    theme_text_color: "Primary"
                    font_style: "Button"
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(10)

                # A Estratégia WhatsApp: Dois botões separados, CENTRALIZADOS
                MDBoxLayout:
                    orientation: "horizontal"
                    adaptive_height: True
                    spacing: "15dp"
                    padding: ["10dp", "0dp", "10dp", "0dp"] # Spacing on sides for perfect center of the row

                    # Botão da Galeria (Nativo) - Totalmente Centralizado verbatim design looks
                    MDCard:
                        size_hint: None, None
                        size: "80dp", "80dp"
                        md_bg_color: 0.9, 0.9, 0.9, 1
                        radius: [15, 15, 15, 15]
                        ripple_behavior: True
                        elevation: 0
                        on_release: root.open_gallery()
                        
                        # USAMOS RELATIVE LAYOUT PARA ALINHAMENTO ABSOLUTO verbatim looks
                        MDRelativeLayout:
                            
                            MDIcon:
                                icon: "image-multiple-outline"
                                theme_text_color: "Custom"
                                text_color: 0.3, 0.3, 0.3, 1
                                font_size: "32sp"
                                halign: "center"
                                # CENTRO X E Y verbatim design look
                                pos_hint: {"center_x": .5, "center_y": .6} 
                            MDLabel:
                                text: "Galeria"
                                font_style: "Caption"
                                theme_text_color: "Hint"
                                halign: "center"
                                # CENTRO X, LEVEMENTE ABAIXO DO ÍCONE verbatim design look
                                pos_hint: {"center_x": .5, "center_y": .3}

                    # Botão da Câmera (Nativo) - Totalmente Centralizado verbatim design looks
                    MDCard:
                        size_hint: None, None
                        size: "80dp", "80dp"
                        md_bg_color: 0.9, 0.9, 0.9, 1
                        radius: [15, 15, 15, 15]
                        ripple_behavior: True
                        elevation: 0
                        on_release: root.open_camera()
                        
                        # USAMOS RELATIVE LAYOUT PARA ALINHAMENTO ABSOLUTO verbatim looks
                        MDRelativeLayout:
                            
                            MDIcon:
                                icon: "camera-outline"
                                theme_text_color: "Custom"
                                text_color: 0.3, 0.3, 0.3, 1
                                font_size: "32sp"
                                halign: "center"
                                # CENTRO X E Y verbatim design look
                                pos_hint: {"center_x": .5, "center_y": .6}
                            MDLabel:
                                text: "Câmera"
                                font_style: "Caption"
                                theme_text_color: "Hint"
                                halign: "center"
                                # CENTRO X, LEVEMENTE ABAIXO DO ÍCONE verbatim design look
                                pos_hint: {"center_x": .5, "center_y": .3}

                # Container for added images
                MDBoxLayout:
                    id: images_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: "10dp"

        # --- Anchored Bottom Submit Button Region (Anchored style look design verbatim) ---
        # anchors the button at the very bottom of the screen verbatim design look
        AnchorLayout:
            anchor_x: "center"
            anchor_y: "bottom"
            size_hint_y: None
            height: "80dp" # Space to anchor button at bottom comfortably design look verbatim design look
            padding: ["15dp", "0dp", "15dp", "15dp"] # Padding around anchored button for full width design look verbatim

            # Styled full-width filled blue button verbatim design look image_2.png
            # Standard FillRoundFlatButton style used for ripple safety but styled light blue
            MDFillRoundFlatButton:
                id: btn_submit
                text: "CADASTRAR" # Match design text verbatim design look
                font_size: "18sp"
                bold: True # Make bold text matching design look
                md_bg_color: 0.22, 0.75, 0.94, 1 # Standard light blue design color
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1 # White
                size_hint_x: 1 # Standard filled blue button full width anchored style
                height: "56dp"
                # Ripple safety standard
                radius: [15, 15, 15, 15] # Rounded corner style verbatim design look image_2.png
                on_release: root.submit_form()
'''

Builder.load_string(KV_FOCUS_FORM)

class ImageCard(MDBoxLayout):
    image_path = StringProperty("")
    image_name = StringProperty("")

class FocusFormScreen(MDScreen):
    neighborhoods_db = {
        "Camboriú": ["Areias", "Braço", "Caetés", "Cedro", "Centro", "Conde Vila Verde", "João da Costa", "Lídia Duarte", "Macacos", "Monte Alegre", "Rio do Meio", "Rio Pequeno", "Santa Regina", "São Francisco de Assis", "Tabuleiro", "Várzea do Ranchinho", "Vila Conceição"], 
        "Balneário Camboriú": ["Ariribá", "Barra", "Centro", "Das Nações", "Dos Estados", "Estaleirinho", "Estaleiro", "Iate Clube", "Jardim Parque Bandeirantes", "Laranjeiras", "Municípios", "Nova Esperança", "Pioneiros", "Praia dos Amores", "São Judas Tadeu", "Taquaras", "Vila Real"]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_files = []
        self.gps_address_data = {}
        self.menu_cities = None
        self.menu_neighborhoods = None
        self.gps_dialog = None
        self.manual_dialog = None
        self.success_dialog = None

    def on_pre_enter(self, *args):
        self.selected_files.clear()
        self.gps_address_data.clear()
        self.update_images_display()
        self.ids.tf_cep.text = ""
        self.ids.tf_city.text = ""
        self.ids.tf_neighborhood.text = ""
        self.ids.tf_neighborhood.disabled = True
        self.ids.tf_street.text = ""
        self.ids.tf_number.text = ""
        self.ids.tf_description.text = ""
        self.ids.btn_gps.text = "Capturar localização (GPS/Rede)"
        self.ids.btn_gps.icon = "map-marker"

    def go_back(self):
        self.manager.current = 'home'
        self.manager.get_screen('home').ids.bottom_nav.switch_tab('tab_new')

    def open_city_menu(self):
        menu_items = [
            {"viewclass": "OneLineListItem", "text": city, "on_release": lambda x=city: self.set_city(x)}
            for city in self.neighborhoods_db.keys()
        ]
        self.menu_cities = MDDropdownMenu(caller=self.ids.tf_city, items=menu_items, width_mult=4)
        self.menu_cities.open()

    def set_city(self, text_item):
        self.ids.tf_city.text = text_item
        self.ids.tf_neighborhood.disabled = False
        self.ids.tf_neighborhood.text = ""
        self.menu_cities.dismiss()

    def open_neighborhood_menu(self):
        city = self.ids.tf_city.text
        if city in self.neighborhoods_db:
            menu_items = [
                {"viewclass": "OneLineListItem", "text": bairro, "on_release": lambda x=bairro: self.set_neighborhood(x)}
                for bairro in self.neighborhoods_db[city]
            ]
            self.menu_neighborhoods = MDDropdownMenu(caller=self.ids.tf_neighborhood, items=menu_items, width_mult=4)
            self.menu_neighborhoods.open()

    def set_neighborhood(self, text_item):
        self.ids.tf_neighborhood.text = text_item
        self.menu_neighborhoods.dismiss()

    def normalize_string(self, s):
        if not s: return ""
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

    @mainthread
    def mostrar_aviso(self, texto, cor="blue"):
        from kivymd.toast import toast
        toast(texto)

    @mainthread
    def fill_address_fields(self, data):
        city_api = data.get("localidade") or ""
        city_clean = self.normalize_string(city_api)
        target_city = None
        
        if "balneario" in city_clean and "camboriu" in city_clean: target_city = "Balneário Camboriú"
        elif "camboriu" in city_clean and "balneario" not in city_clean: target_city = "Camboriú"
        
        if target_city:
            self.ids.tf_city.text = target_city
            self.ids.tf_neighborhood.disabled = False
            if target_city in self.neighborhoods_db:
                opts = self.neighborhoods_db[target_city]
                b = data.get("bairro")
                if b:
                    if b not in opts: opts.append(b); opts.sort()
                    self.ids.tf_neighborhood.text = b
            self.ids.tf_street.text = data.get("logradouro", "")
            self.ids.tf_cep.text = data.get("cep", "").replace("-", "")
            if data.get("numero"): self.ids.tf_number.text = data.get("numero")
        else:
            self.ids.tf_city.text = ""
            self.ids.tf_neighborhood.text = ""
            self.ids.tf_neighborhood.disabled = True
            self.ids.tf_street.text = ""
            self.ids.tf_number.text = ""
            self.ids.tf_cep.text = ""
            self.mostrar_aviso(f"Serviço indisponível em {city_api}", "red")

    def on_cep_change(self, text):
        cep = text.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            threading.Thread(target=self._worker_search_cep, args=(cep,), daemon=True).start()

    def _worker_search_cep(self, cep):
        try:
            res = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
            if "erro" not in res:
                self.fill_address_fields(res)
        except: pass

    def search_address_by_name(self):
        city = self.ids.tf_city.text
        street = self.ids.tf_street.text
        if not city or len(street) < 3:
            self.mostrar_aviso("Selecione a cidade e digite 3 letras da rua.", "orange")
            return
            
        self.ids.btn_search_street.icon = "timer-sand"
        threading.Thread(target=self._worker_search_street, args=(city, street), daemon=True).start()

    def _worker_search_street(self, city, street):
        try:
            url = f"https://viacep.com.br/ws/SC/{quote(city)}/{quote(street)}/json/"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0: 
                    Clock.schedule_once(lambda dt: self.open_manual_modal(data), 0)
                else: 
                    self.mostrar_aviso("Rua não encontrada.", "orange")
            else:
                self.mostrar_aviso(f"Erro do ViaCEP: {res.status_code}", "red")
        except Exception: 
            self.mostrar_aviso("Erro na busca da rua.", "red")
            
        Clock.schedule_once(lambda dt: self._reset_search_icon(), 0)

    @mainthread
    def _reset_search_icon(self):
        self.ids.btn_search_street.icon = "magnify"

    @mainthread
    def open_manual_modal(self, address_list):
        from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
        from kivy.uix.scrollview import ScrollView
        
        content = ScrollView(size_hint_y=None, height=dp(300))
        box = MDBoxLayout(orientation='vertical', adaptive_height=True)
        for addr in address_list:
            item = TwoLineIconListItem(
                text=addr.get("logradouro", ""),
                secondary_text=f"{addr.get('bairro', '')} - CEP: {addr.get('cep', '')}",
                on_release=lambda x, a=addr: self.select_address_manual(a)
            )
            item.add_widget(IconLeftWidget(icon="map-marker"))
            box.add_widget(item)
        content.add_widget(box)

        self.manual_dialog = MDDialog(
            title="Selecione a Rua",
            type="custom",
            content_cls=content,
            buttons=[MDFlatButton(text="Fechar", radius=[8, 8, 8, 8], on_release=lambda x: self.manual_dialog.dismiss())]
        )
        self.manual_dialog.open()

    def select_address_manual(self, addr_data):
        if self.manual_dialog: self.manual_dialog.dismiss()
        self.fill_address_fields(addr_data)

    def start_location(self):
        print("VIGIAA DEBUG: =========================================")
        print("VIGIAA DEBUG: [1] BOTÃO PRESSIONADO - Iniciando busca")
        self.ids.btn_gps.text = "Pedindo permissão..."
        self.ids.btn_gps.icon = "crosshairs-gps"
        self.ids.btn_gps.disabled = True

        if platform == 'android':
            print("VIGIAA DEBUG: [1.1] Plataforma Android detectada. Solicitando permissões...")
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION], self._on_permissions_result)
        else:
            print("VIGIAA DEBUG: [1.2] PC detectado. Indo para IP.")
            self.mostrar_aviso("Teste no PC: Usando IP.")
            self._reset_gps_btn()

    def _on_permissions_result(self, permissions, grants):
        print(f"VIGIAA DEBUG: [2] Resposta das permissões: {grants}")
        # A MÁGICA: O Android devolve no fundo, mas nós jogamos a execução para o Fio Principal!
        Clock.schedule_once(lambda dt: self._safe_gps_start(grants), 0)

    # Nova função que roda com segurança na Main Thread
    def _safe_gps_start(self, grants):
        # Aceita se PELO MENOS UMA das permissões (Fina ou Grossa) foi dada
        if any(grants): 
            try:
                print("VIGIAA DEBUG: [3] Permissões OK. Configurando o Plyer GPS...")
                gps.configure(on_location=self._on_gps_location, on_status=self._on_gps_status)
                
                print("VIGIAA DEBUG: [4] Dando o comando gps.start...")
                gps.start(minTime=1000, minDistance=1) 
                
                self.gps_tempo = 40 
                self.ids.btn_gps.text = f"Buscando satélite ({self.gps_tempo}s)..."
                self.gps_event = Clock.schedule_interval(self._gps_countdown, 1)
                
            except Exception as e:
                print(f"VIGIAA DEBUG: [ERRO CRÍTICO] Falha ao iniciar antena: {e}")
                self.mostrar_aviso(f"Erro no sensor: {e}", "red")
                self._reset_gps_btn()
        else:
            print("VIGIAA DEBUG: [ERRO] Usuário negou a permissão.")
            self.mostrar_aviso("Você precisa permitir o uso do GPS!", "red")
            self._reset_gps_btn()

    @mainthread
    def _gps_countdown(self, dt):
        self.gps_tempo -= 1
        if self.gps_tempo % 5 == 0:
            print(f"VIGIAA DEBUG: [TIMER] Satélite ainda não respondeu. Tempo restante: {self.gps_tempo}s")
            
        if self.gps_tempo > 0:
            self.ids.btn_gps.text = f"Buscando satélite ({self.gps_tempo}s)..."
        else:
            print("VIGIAA DEBUG: [6] O TEMPO ACABOU! O Satélite não enviou coordenadas. Cancelando cronômetro.")
            self.gps_event.cancel()
            self._gps_escape_memory(None)

    @mainthread
    def _on_gps_location(self, **kwargs):
        if hasattr(self, 'gps_event'):
            self.gps_event.cancel()
            
        # O SEGREDO: Atrasar o stop do GPS em 0.5s para o Android não engasgar e fechar o app!
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: gps.stop(), 0.5) 
        
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        
        self.ids.btn_gps.text = "Coordenada Capturada!"
        self.ids.btn_gps.icon = "check"
        
        threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Satélite GPS Nativo"), daemon=True).start()

    @mainthread
    def _on_gps_status(self, stype, status):
        print(f"VIGIAA DEBUG: [STATUS DO HARDWARE] Tipo: {stype} | Status: {status}")

    @mainthread
    def _gps_escape_memory(self, dt):
        print("VIGIAA DEBUG: [7] Iniciando plano de fuga: Memória PyJnius.")
        if self.ids.btn_gps.text.startswith("Buscando"):
            print("VIGIAA DEBUG: [7.1] Parando antena travada do Plyer.")
            gps.stop()
            self.ids.btn_gps.text = "Lendo memória..."
            
            print("VIGIAA DEBUG: [7.2] Chamando _get_last_known_location_android()")
            lat, lon = self._get_last_known_location_android()
            
            if lat and lon:
                print(f"VIGIAA DEBUG: [7.3] Memória encontrada! Lat: {lat}, Lon: {lon}")
                self.ids.btn_gps.text = "Coordenada da Memória!"
                self.ids.btn_gps.icon = "check"
                threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Memória do Android"), daemon=True).start()
            else:
                print("VIGIAA DEBUG: [7.4] A memória também estava vazia. Fim da linha.")
                self.mostrar_aviso("Memória vazia. Tente ir para um local mais aberto.", "red")
                self._reset_gps_btn()

    def _get_last_known_location_android(self):
        try:
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            LocationManager = autoclass('android.location.LocationManager')
            
            activity = PythonActivity.mActivity
            lm = activity.getSystemService(Context.LOCATION_SERVICE)
            
            # MUDANÇA: Tenta o GPS (Satélite de ALTA precisão) PRIMEIRO!
            loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)
            
            if not loc:
                # Se estiver vazio, tenta a Rede (Antena de celular/Wi-Fi de BAIXA precisão)
                loc = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
                
            if loc:
                return loc.getLatitude(), loc.getLongitude()
        except Exception as e:
            print(f"VIGIAA DEBUG: [JNIUS ERRO] {e}")
            
        return None, None

    @mainthread
    def _on_gps_location(self, **kwargs):
        # 4. Se o satélite for rápido, cancelamos a busca na memória e usamos o satélite!
        if hasattr(self, 'gps_event'):
            self.gps_event.cancel()
        gps.stop() 
        
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        
        self.ids.btn_gps.text = "Coordenada Capturada!"
        self.ids.btn_gps.icon = "check"
        
        threading.Thread(target=self._worker_get_address_from_coords, args=(lat, lon, "Satélite GPS Nativo"), daemon=True).start()

    @mainthread
    def _on_gps_status(self, stype, status):
        pass
        

    def _worker_ip_location(self):
        try:
            res = requests.get("http://ip-api.com/json/", timeout=5)
            if res.status_code == 200:
                data = res.json()
                self._worker_get_address_from_coords(data.get('lat'), data.get('lon'), "Internet (Aproximado)")
                return
        except: pass
        self.mostrar_aviso("Erro de conexão.", "red")
        Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    def _worker_get_address_from_coords(self, lat, lon, source="Rede"):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            res = requests.get(url, headers={'User-Agent': 'VigiAA/1.0'}).json()
            addr = res.get("address", {})
            self.gps_address_data.clear()
            self.gps_address_data["lat"] = str(lat)
            self.gps_address_data["lon"] = str(lon) 
            self.gps_address_data["localidade"] = addr.get("city") or addr.get("town") or addr.get("municipality")
            self.gps_address_data["bairro"] = addr.get("suburb") or addr.get("neighbourhood")
            self.gps_address_data["logradouro"] = addr.get("road")
            self.gps_address_data["cep"] = addr.get("postcode")
            self.gps_address_data["numero"] = addr.get("house_number")
            Clock.schedule_once(lambda dt: self.open_gps_modal(source), 0)
        except:
            self.mostrar_aviso("Erro ao traduzir endereço.", "red")
            Clock.schedule_once(lambda dt: self._reset_gps_btn(), 0)

    @mainthread
    def _reset_gps_btn(self): 
        self.ids.btn_gps.text = "Capturar localização (GPS/Rede)"
        self.ids.btn_gps.icon = "map-marker"
        self.ids.btn_gps.disabled = False

    @mainthread
    def open_gps_modal(self, source):
        self.ids.btn_gps.text = "Localização Encontrada!"
        self.ids.btn_gps.icon = "check"
        self.ids.btn_gps.disabled = False
        
        rua = self.gps_address_data.get("logradouro") or "Rua não detectada"
        bairro = self.gps_address_data.get("bairro") or "Bairro não detectado"
        cidade = self.gps_address_data.get("localidade") or "Cidade não detectada"
        texto_dialog = f"[b]Rua:[/b] {rua}\n[b]Bairro:[/b] {bairro}\n[b]Cidade:[/b] {cidade}\n\n[i]Fonte: {source}[/i]"
        
        self.gps_dialog = MDDialog(
            title="Confirme os Dados:",
            text=texto_dialog,
            buttons=[
                MDFlatButton(text="Cancelar", text_color=(1,0,0,1), on_release=lambda x: self.gps_dialog.dismiss()),
                MDFlatButton(text="Confirmar", text_color=(0.22, 0.75, 0.94, 1), on_release=self.confirm_gps_fill)
            ]
        )
        self.gps_dialog.open()

    def confirm_gps_fill(self, instance):
        self.gps_dialog.dismiss()
        self.fill_address_fields(self.gps_address_data)

    def open_gallery(self):
        """Abre o seletor nativo de arquivos do Android (Galeria)"""
        try:
            filechooser.open_file(on_selection=self._handle_selection, filters=[("Images", "*.png", "*.jpg", "*.jpeg")])
        except Exception as e:
            self.mostrar_aviso("Permissão de galeria negada ou indisponível.", "red")

    def open_camera(self):
        """Pede permissão e abre a câmera nativa do Android"""
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # Pede a trindade de permissões: Câmera + Ler + Escrever na memória
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], self._on_camera_permissions)
        else:
            self.mostrar_aviso("A câmera nativa só funciona no celular.")

    def _on_camera_permissions(self, permissions, grants):
        # Jogamos a execução da câmera para o Fio Principal!
        Clock.schedule_once(lambda dt: self._safe_camera_start(permissions, grants), 0)

    # Nova função que roda com segurança
    # Nova função que roda com segurança
    def _safe_camera_start(self, permissions, grants):
        from android.permissions import Permission
        from plyer import camera
        
        perms_dict = dict(zip(permissions, grants))
        
        if perms_dict.get(Permission.CAMERA, False):
            try:
                # A MÁGICA DO ANDROID MODERNO: Passamos filename=None!
                camera.take_picture(filename=None, on_complete=self._on_camera_success)
            except Exception as e:
                self.mostrar_aviso(f"Erro ao ligar a lente: {e}", "red")
        else:
            self.mostrar_aviso("Permissão de câmera negada!", "red")

    def _safe_camera_start(self, permissions, grants):
        from android.permissions import Permission
        from plyer import camera
        import os
        import time
        
        perms_dict = dict(zip(permissions, grants))
        
        if perms_dict.get(Permission.CAMERA, False):
            try:
                from kivy.utils import platform
                if platform == 'android':
                    from jnius import autoclass
                    
                    # 1. A BALA DE PRATA (Libera a passagem do caminho)
                    StrictMode = autoclass('android.os.StrictMode')
                    VmPolicyBuilder = autoclass('android.os.StrictMode$VmPolicy$Builder')
                    StrictMode.setVmPolicy(VmPolicyBuilder().build())
                    
                    # 2. O NOVO ENDEREÇO DA FOTO (Pasta Pública de Imagens do Android)
                    Environment = autoclass('android.os.Environment')
                    pasta_fotos = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
                else:
                    # Se for teste no PC, usa a pasta normal do app
                    from kivy.app import App
                    pasta_fotos = App.get_running_app().user_data_dir

                # Montamos o caminho final
                nome_arquivo = f"foco_{int(time.time())}.jpg"
                self.caminho_foto_temp = os.path.join(pasta_fotos, nome_arquivo)
                
                # Chamamos a câmera!
                camera.take_picture(filename=self.caminho_foto_temp, on_complete=self._on_camera_success)
                
            except Exception as e:
                self.mostrar_aviso(f"Erro ao ligar a lente: {e}", "red")
        else:
            self.mostrar_aviso("Permissão de câmera negada!", "red")

    @mainthread
    def _on_camera_success(self, filepath=None):
        """Quando o usuário clica no 'OK' da câmera, a foto cai aqui"""
        # O Android pode não devolver o filepath, então puxamos o caminho que nós mesmos criamos
        caminho_final = filepath if filepath else getattr(self, 'caminho_foto_temp', None)
        
        if caminho_final and os.path.exists(caminho_final):
            if caminho_final not in self.selected_files:
                self.selected_files.append(caminho_final)
                self.update_images_display()
        else:
            self.mostrar_aviso("Foto cancelada ou não salva.", "orange")

    # Mantemos o seu _handle_selection original intacto!
    def _handle_selection(self, selection):
        if selection:
            for path in selection:
                if path not in self.selected_files:
                    self.selected_files.append(path)
            Clock.schedule_once(lambda dt: self.update_images_display(), 0)

   
    def remove_image(self, path):
        if path in self.selected_files:
            self.selected_files.remove(path)
            self.update_images_display()

    @mainthread
    def update_images_display(self):
        self.ids.images_container.clear_widgets()
        for path in self.selected_files:
            nome_arquivo = os.path.basename(path)
            
            # --- O AJUSTE PARA A FOTO APARECER ---
            caminho_para_exibir = path
            if platform == 'android':
                # No Android, adicionamos 'file://' no início do caminho
                caminho_para_exibir = "file://" + path
            
            card = ImageCard(image_path=caminho_para_exibir, image_name=nome_arquivo)
            self.ids.images_container.add_widget(card)

    def submit_form(self):
        if not store.exists("session"):
            self.manager.current = 'login'
            return
            
        token = store.get("session")["token"]
        cidade = self.ids.tf_city.text
        bairro = self.ids.tf_neighborhood.text
        rua = self.ids.tf_street.text
        numero = self.ids.tf_number.text
        
        if not all([cidade, bairro, rua, numero]):
            self.mostrar_aviso("Preencha os campos obrigatórios (*)", "red")
            return
            
        self.ids.btn_submit.text = "Enviando..."
        self.ids.btn_submit.disabled = True
        threading.Thread(target=self._worker_submit, args=(token,), daemon=True).start()

    def _worker_submit(self, token):
        try:
            data = {
                "cep": self.ids.tf_cep.text, 
                "city": self.ids.tf_city.text, 
                "neighborhood": self.ids.tf_neighborhood.text, 
                "street": self.ids.tf_street.text, 
                "number": self.ids.tf_number.text, 
                "description": self.ids.tf_description.text, 
                "latitude": self.gps_address_data.get("lat", "-27.000"), 
                "longitude": self.gps_address_data.get("lon", "-48.000")
            }
            
            files = []
            file_handles = []
            for path in self.selected_files:
                f = open(path, 'rb')
                file_handles.append(f)
                files.append(('uploaded_images', (os.path.basename(path), f, 'image/jpeg')))
                
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(f"{config.API_URL}/api/report-focus/", data=data, files=files, headers=headers)
            
            for f in file_handles: f.close()
            
            if res.status_code in [200, 201]: 
                Clock.schedule_once(lambda dt: self.open_success_modal(), 0)
            else: 
                self.mostrar_aviso(f"Erro no servidor. Código: {res.status_code}", "red")
                
        except Exception as ex: 
            self.mostrar_aviso("Erro de comunicação com o sistema.", "red")
            
        Clock.schedule_once(lambda dt: self._reset_submit_btn(), 0)

    @mainthread
    def _reset_submit_btn(self):
        self.ids.btn_submit.text = "CADASTRAR FOCO"
        self.ids.btn_submit.disabled = False

    @mainthread
    def open_success_modal(self):
        self.success_dialog = MDDialog(
            title="Sucesso!",
            text="Foco de dengue cadastrado com sucesso!",
            buttons=[
                MDFlatButton(text="OK", text_color=(1,1,1,1), md_bg_color=(0, 0.7, 0, 1), radius=[8, 8, 8, 8], on_release=self.close_success_modal)
            ]
        )
        self.success_dialog.open()

    def close_success_modal(self, instance):
        self.success_dialog.dismiss()
        self.go_back()