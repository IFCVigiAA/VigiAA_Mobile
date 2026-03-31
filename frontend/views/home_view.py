from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
# Importamos a classe para o Python conhecer, e pro KV importar
from views.tabs.home_tab import HomeTabContent
from views.tabs.new_tab import NewTabContent
from views.tabs.explore_tab import ExploreTabContent
from kivy.clock import mainthread

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
        from kivymd.app import MDApp
        from kivy.storage.jsonstore import JsonStore
        import threading
        
        app = MDApp.get_running_app()
        store = JsonStore('sessao_app.json')
        
        # 1. Puxa a chave
        token_seguro = getattr(app, "vigiaa_token", None)
        if not token_seguro and store.exists("session"):
            token_seguro = store.get("session")["token"]
            app.vigiaa_token = token_seguro 

        if token_seguro:
            # A NOVA REGRA: O Segurança só trabalha UMA VEZ por aplicativo aberto!
            if getattr(app, 'seguranca_ja_verificou', False):
                # Se já verificou hoje, deixa a detetive trabalhar em paz!
                return 
                
            # Se ainda não verificou, marca que verificou e manda o segurança ir olhar
            app.seguranca_ja_verificou = True
            print("VIGIAA DEBUG: [HOME] Primeira entrada. Segurança indo checar o token...")
            threading.Thread(target=self._seguranca_silencioso, args=(token_seguro,), daemon=True).start()
        else:
            print("VIGIAA DEBUG: [HOME FATAL] Cofre realmente vazio. Chutando pro login...")
            self._chutar_para_login()

    def _seguranca_silencioso(self, token):
        import requests
        import config 
        from kivy.clock import Clock
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # ATENÇÃO: Se você souber a rota correta para validar o token, troque aqui.
            url = f"{config.API_URL}/api/user/profile/" 
            
            res = requests.get(url, headers=headers, timeout=5)
            
            # O SEGURANÇA INTELIGENTE:
            if res.status_code in [401, 403]:
                # Token realmente inválido ou vencido -> EXPULSA!
                print(f"VIGIAA DEBUG: Segurança barrou! Token Inválido (Erro {res.status_code})")
                Clock.schedule_once(lambda dt: self._chutar_para_login(), 0)
                
            elif res.status_code == 404:
                # A URL está errada! O Django não achou essa rota.
                print("VIGIAA DEBUG: [ALERTA DESENVOLVEDOR] A rota da API não existe (Erro 404). O Token está salvo, mas a URL de checagem está errada!")
                # Não expulsamos o usuário, pois o erro é na rota, não no token dele.
                
            elif res.status_code in [200, 201]:
                print("VIGIAA DEBUG: Token validado com sucesso na porta da frente!")
                
        except Exception as e:
            # Sem internet ou servidor desligado -> Deixa passar (modo offline)
            print(f"VIGIAA DEBUG: Servidor inalcançável. Liberado offline. Erro: {e}")

    @mainthread
    def _chutar_para_login(self, *args):
        print("🚨🚨 ALARME: Fui expulsa pela função da HOME! 🚨🚨")
        from kivymd.app import MDApp
        from kivy.storage.jsonstore import JsonStore
        from kivymd.toast import toast
        
        app = MDApp.get_running_app()
        store = JsonStore('sessao_app.json')
        
        # Reseta as memórias do cérebro do app
        app.force_logout = True
        app.vigiaa_token = None
        app.seguranca_ja_verificou = False  # <--- ADICIONE ISTO AQUI
        
        if store.exists("session"):
            store.delete("session")
            
        app.root.current = 'login'
        toast("Sessão expirada. Faça login novamente.")