from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.list import OneLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

KV_HOME_TAB = '''
<StatCard@MDCard>:
    orientation: "vertical"
    padding: ["15dp", "5dp", "15dp", "15dp"]
    spacing: "2dp"
    radius: [10, 10, 10, 10]
    elevation: 1
    shadow_color: 0, 0, 0, 0.1
    md_bg_color: 1, 1, 1, 1
    title: ""
    value: ""
    subtext: ""
    
    MDLabel:
        text: root.title
        font_size: "14sp"
        bold: True
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        halign: "left"
        font_size: "15sp"
        
    MDLabel:
        text: root.value
        font_size: "28sp"
        bold: True
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        halign: "left"
        font_size: "30sp"

<ChartCard@MDCard>:
    orientation: "vertical"
    padding: "20dp"
    spacing: "10dp"
    radius: [10, 10, 10, 10]
    elevation: 1
    shadow_color: 0, 0, 0, 0.1
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
    text: root.year_text
    font_size: "14sp"
    bold: True
    size_hint: None, None
    size: "80dp", "40dp"
    radius: [20, 20, 20, 20]
    md_bg_color: (0, 0, 0, 1) if root.is_selected else (0.9, 0.9, 0.9, 1)
    theme_text_color: "Custom"
    text_color: (1, 1, 1, 1) if root.is_selected else (0, 0, 0, 1)
    on_release: root.on_click()

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
                id: card_confirmados    
                title: "Casos confirmados"
                value: "Carregando..."

            StatCard:
                id: card_suspeitas    
                title: "Suspeitas de dengue"
                value: "Carregando..."
        
        # espaço para o mapa
        ChartCard:
            title: "Mapa com dados de Dengue e Aedes aegypti"
            image_src: "assets/images/mapaexemplo.png"        
        
        # Gráficos
        ChartCard:
            title: "Casos confirmados por mês"
            image_src: "assets/images/grafico1.png"

        ChartCard:
            title: "Proporção de focos por tipo de atividade"
            image_src: "assets/images/grafico2.png"
'''

Builder.load_string(KV_HOME_TAB)


class YearButton(MDFillRoundFlatButton):
    is_selected = BooleanProperty(False)
    year_text = StringProperty("")
    callback = ObjectProperty(None)
    
    def on_click(self, *args):
        if self.callback:
            self.callback(self)


# class HomeTabContent(ScrollView):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.year_buttons = []
#         Clock.schedule_once(self.populate_years, 0)
#         Clock.schedule_once(lambda dt: self.carregar_dados_api(), 0.1)

#     def populate_years(self, dt):
#         anos = ["2026", "2025", "2024"]
#         if "year_container" in self.ids:
#             self.ids.year_container.clear_widgets()
#             for i, ano in enumerate(anos):
#                 btn = YearButton(year_text=ano, is_selected=(i == 0), callback=self.change_year)
#                 self.year_buttons.append(btn)
#                 self.ids.year_container.add_widget(btn)

#     def change_year(self, clicked_btn):
#         for btn in self.year_buttons:
#             btn.is_selected = False
#         clicked_btn.is_selected = True
#         print(f"[DEBUG] Ano selecionado: {clicked_btn.year_text}")
#         self.carregar_dados_api()

#     def carregar_dados_api(self):
#         url = "https://froglike-cataleya-quirkily.ngrok-free.dev/api/estatisticas/"
        
#         # Cabeçalhos necessários para ignorar o bloqueio de aviso do Ngrok
#         headers = {
#             'ngrok-skip-browser-warning': 'true',
#             'Content-Type': 'application/json'
#         }

#         UrlRequest(
#             url,
#             on_success=self._on_dados_sucesso,
#             on_failure=self._on_dados_erro,
#             on_error=self._on_dados_erro,
#             req_headers=headers,
#             timeout=10,
#         )

#     def _on_dados_sucesso(self, request, result):
#         print(f"[DEBUG] Resposta completa da API: {result}")
        
#         # Extrai os dados do JSON com segurança
#         resumo = result.get("resumo", {}) if isinstance(result, dict) else {}
#         total_confirmados = resumo.get("total_casos_positivos", result.get("confirmados", 0) if isinstance(result, dict) else 0)
#         total_suspeitas = resumo.get("total_casos_suspeitos", result.get("suspeitas", 0) if isinstance(result, dict) else 0)

#         print(f"[DEBUG] Confirmados: {total_confirmados} | Suspeitas: {total_suspeitas}")

#         if "card_confirmados" in self.ids:
#             self.ids.card_confirmados.value = str(total_confirmados)
#         if "card_suspeitas" in self.ids:
#             self.ids.card_suspeitas.value = str(total_suspeitas)

#     def _on_dados_erro(self, request, error):
#         status = getattr(request, 'resp_status', 'Desconhecido')
#         print(f"[DEBUG] Erro na requisição API: (Status {status})")
#         if "card_confirmados" in self.ids:
#             self.ids.card_confirmados.value = "Erro"
#         if "card_suspeitas" in self.ids:
#             self.ids.card_suspeitas.value = "Erro"
class HomeTabContent(ScrollView):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.year_buttons = []
    self.cache_estatisticas = {}
    Clock.schedule_once(self.populate_years, 0)
    # Carrega os dados iniciais do ano de 2026 por padrão
    Clock.schedule_once(lambda dt: self.carregar_dados_api(ano='2026'), 0.1)

  def populate_years(self, dt):
    anos = ['2026', '2025', '2024']
    if 'year_container' in self.ids:
      self.ids.year_container.clear_widgets()
      for i, ano in enumerate(anos):
        btn = YearButton(
            year_text=ano, is_selected=(i == 0), callback=self.change_year
        )
        self.year_buttons.append(btn)
        self.ids.year_container.add_widget(btn)

  def change_year(self, clicked_btn):
    for btn in self.year_buttons:
      btn.is_selected = False
    clicked_btn.is_selected = True
    print(f'[DEBUG] Ano selecionado: {clicked_btn.year_text}')

    # Envia o ano do botão clicado para a função da API
    self.carregar_dados_api(ano=clicked_btn.year_text)

#   def carregar_dados_api(self, ano=None):
#     url = 'https://froglike-cataleya-quirkily.ngrok-free.dev/api/estatisticas/'

#     # Se um ano for passado, monta a URL com o parâmetro ?ano=
#     if ano:
#       url = f'{url}?ano={ano}'

#     print(f'[DEBUG] Requisitando URL: {url}')

#     headers = {
#         'ngrok-skip-browser-warning': 'true',
#         'Content-Type': 'application/json',
#     }

#     UrlRequest(
#         url,
#         on_success=self._on_dados_sucesso,
#         on_failure=self._on_dados_erro,
#         on_error=self._on_dados_erro,
#         req_headers=headers,
#         timeout=10,
#     )
  def carregar_dados_api(self, ano=None):
    chave_cache = str(ano) if ano else 'todos'

    # 1. SE JÁ EXISTE NO CACHE: exibe na hora e CANCELA a requisição HTTP
    if chave_cache in self.cache_estatisticas:
        print(f"[CACHE] Usando dados salvos do ano: {chave_cache}")
        self._atualizar_cards(self.cache_estatisticas[chave_cache])
        return

    # 2. SE NÃO EXISTE: mostra "..." nos cards enquanto busca na API
    if "card_confirmados" in self.ids:
        self.ids.card_confirmados.value = "..."
    if "card_suspeitas" in self.ids:
        self.ids.card_suspeitas.value = "..."

    url = "https://froglike-cataleya-quirkily.ngrok-free.dev/api/estatisticas/"
    if ano:
        url = f"{url}?ano={ano}"

    headers = {
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json'
    }

    # 3. Usa um 'lambda' para passar o chave_cache ao _on_dados_sucesso
    UrlRequest(
        url,
        on_success=lambda req, result: self._on_dados_sucesso(result, chave_cache),
        on_failure=self._on_dados_erro,
        on_error=self._on_dados_erro,
        req_headers=headers,
        timeout=10,
    )

  def _on_dados_sucesso(self, result, chave_cache):
    self.cache_estatisticas[chave_cache] = result
    self._atualizar_cards(result)

    resumo = result.get('resumo', {}) if isinstance(result, dict) else {}
    total_confirmados = resumo.get(
        'total_casos_positivos',
        result.get('confirmados', 0) if isinstance(result, dict) else 0,
    )
    total_suspeitas = resumo.get(
        'total_casos_suspeitos',
        result.get('suspeitas', 0) if isinstance(result, dict) else 0,
    )

    print(
        f'[DEBUG] Confirmados: {total_confirmados} | Suspeitas:'
        f' {total_suspeitas}'
    )

  def _atualizar_cards(self, result):
    resumo = result.get("resumo", {}) if isinstance(result, dict) else {}
    total_confirmados = resumo.get("total_casos_positivos", 0)
    total_suspeitas = resumo.get("total_casos_suspeitos", 0)

    if "card_confirmados" in self.ids:
        self.ids.card_confirmados.value = str(total_confirmados)
    if "card_suspeitas" in self.ids:
        self.ids.card_suspeitas.value = str(total_suspeitas)
  
  def _on_dados_erro(self, request, error):
    status = getattr(request, 'resp_status', 'Desconhecido')
    print(f'[DEBUG] Erro na requisição API: (Status {status})')
    if 'card_confirmados' in self.ids:
      self.ids.card_confirmados.value = 'Erro'
    if 'card_suspeitas' in self.ids:
      self.ids.card_suspeitas.value = 'Erro'
    