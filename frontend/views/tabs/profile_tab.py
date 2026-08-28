# ==============================================================================
# IMPORTS E CONFIGURAÇÕES DE DEPENDÊNCIAS
# ==============================================================================
import os
import shutil
import time
import threading
import requests

from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy.cache import Cache

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar

import config

# Armazenamento local da sessão do usuário em formato JSON
store = JsonStore('sessao_app.json')


# ==============================================================================
# GERENCIAMENTO DE ESTADO E CARREGAMENTO DO PERFIL
# ==============================================================================
class ProfileViewCheck(MDScreen):
    """
    Classe de tela utilitária para controle de estado e carregamento lazily (sob demanda)
    dos dados do perfil a partir da API Django.
    """
    profile_carregado = False

    def carregar_perfil_api(self, force_reload=False):
        if self.profile_carregado and not force_reload:
            return
        # Envia a requisição para o background
        threading.Thread(target=self._worker_carregar_perfil, daemon=True).start()

    def _worker_carregar_perfil(self):
        app = MDApp.get_running_app()
        api_url = getattr(config, 'API_URL', getattr(app, 'api_base_url', ''))
        headers = {'Authorization': f'Bearer {app.user_token}'}
        url = f"{api_url}/api/profile/"

        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                dados = response.json()
                # Retorna para a thread principal apenas para atualizar a UI
                Clock.schedule_once(lambda dt: self._aplicar_dados_ui(dados), 0)
            else:
                print(f"VIGIAA DEBUG: Falha ao buscar perfil: Status {response.status_code}")
        except Exception as e:
            print(f"VIGIAA DEBUG: Erro de conexão ao buscar perfil: {e}")

    def _aplicar_dados_ui(self, dados):
        self.preencher_campos_ui(dados)
        self.profile_carregado = True
        print("VIGIAA DEBUG: Perfil carregado com sucesso.")

    def preencher_campos_ui(self, dados):
        """Preenche e atualiza a interface gráfica com os dados retornados do servidor."""
        if 'txt_nome' in self.ids:
            self.ids.txt_nome.text = dados.get('first_name', '')
            self.ids.txt_sobrenome.text = dados.get('last_name', '')
            self.ids.txt_username.text = dados.get('username', '')
            self.ids.txt_email.text = dados.get('email', '')
        
        if dados.get('foto_url') and 'avatar_user' in self.ids:
            # Previne cache de imagem antigos utilizando timestamp na URL
            self.ids.avatar_user.source = f"{dados['foto_url']}?t={int(time.time())}"


# ==============================================================================
# DECLARAÇÃO DA INTERFACE GRÁFICA (KV LANG)
# ==============================================================================
KV_PROFILE_TAB = '''
<ProfileField>:
    orientation: "horizontal"
    size_hint_y: None
    height: "50dp"
    size_hint_x: 1
    padding: ["12dp", 0, "10dp", 0]
    spacing: "10dp"
    
    # Linha divisória inferior
    canvas.before:
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        Line:
            points: self.x + dp(10), self.y, self.width - dp(10), self.y
            width: 1

    MDLabel:
        text: root.label_text
        bold: True
        size_hint_x: None
        width: "80dp"
        font_size: "12sp"
        pos_hint: {"center_y": .5}
        
    TextInput:
        id: field_input
        text: root.text_value
        readonly: True
        size_hint_x: 1 
        font_size: "12sp"
        foreground_color: (0, 0, 0, 1) if not self.readonly else (0.4, 0.4, 0.4, 1)
        background_color: 0, 0, 0, 0
        padding: [0, (self.height - self.line_height) / 2]
        multiline: False
        pos_hint: {"center_y": .5}
        cursor_color: 0.22, 0.75, 0.94, 1
        # IMPORTANTE PARA O CELULAR:
        # Garante que o teclado saiba que é um campo de texto simples de linha única
        write_tab: False 
        # Dispara o salvamento se o usuário clicar no botão de confirmação/enter do teclado do celular
        on_text_validate: root.save_edit()
        # Gerencia a perda de foco (caso toque fora ou feche o teclado pelo botão nativo)
        on_focus: root.on_input_focus(self, self.focus)

    # Container de Ações (Editar, Salvar, Cancelar)
    MDBoxLayout:
        size_hint: None, None
        height: "36dp"
        width: "0dp" if root.is_email else ("76dp" if btn_save.opacity > 0 else "36dp")
        pos_hint: {"center_y": .5}
        spacing: "4dp"
        
        MDIconButton:
            id: btn_edit
            icon: "pencil-outline"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            opacity: 1 if not root.is_email and btn_save.opacity == 0 else 0
            disabled: root.is_email or btn_save.opacity > 0
            pos_hint: {"center_y": .5}
            on_release: root.start_edit()
            size_hint: None, None
            size: ("36dp", "36dp") if self.opacity > 0 else ("0dp", "0dp")
            
        MDIconButton:
            id: btn_save
            icon: "check"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 0, 0.7, 0, 1
            opacity: 0
            disabled: True
            pos_hint: {"center_y": .5}
            on_release: root.save_edit()
            size_hint: None, None
            size: ("36dp", "36dp") if self.opacity > 0 else ("0dp", "0dp")
            
        MDIconButton:
            id: btn_cancel
            icon: "close"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
            opacity: 0
            disabled: True
            pos_hint: {"center_y": .5}
            on_release: root.cancel_edit()
            size_hint: None, None
            size: ("36dp", "36dp") if self.opacity > 0 else ("0dp", "0dp")
            
<ActionRow@MDCard>:
    size_hint_y: None
    height: "56dp"
    size_hint_x: 1
    elevation: 0
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True
    padding: ["12dp", "0dp", "12dp", "0dp"]
    
    text_label: ""
    icon_name: "chevron-right"
    text_color: 0, 0, 0, 1
    
    MDLabel:
        text: root.text_label
        bold: True
        font_size: "16sp"
        theme_text_color: "Custom"
        text_color: root.text_color
        halign: "left"
        
    MDIcon:
        icon: root.icon_name
        theme_text_color: "Custom"
        text_color: root.text_color
        pos_hint: {"center_y": .5}

<ProfileTabContent>:
    md_bg_color: 1, 1, 1, 1
    MDBoxLayout:
        orientation: "vertical"
        size_hint_x: 1
        padding: ["5dp", "20dp", "5dp", "20dp"]
        spacing: "12dp"
        adaptive_height: True

        # --- ÁREA DA FOTO COM CÂMERA ---
        AnchorLayout:
            anchor_x: "center"
            size_hint_y: None
            height: "130dp"
            
            MDFloatLayout:
                size_hint: None, None
                size: "110dp", "110dp"
                
                MDCard:
                    size_hint: None, None
                    size: "110dp", "110dp"
                    radius: [55,]
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    elevation: 0
                    pos_hint: {"center_x": .5, "center_y": .5}
                    clip_to_bounds: True
                    
                    FitImage:
                        id: avatar_image
                        source: root.avatar_source
                        radius: [55,]

                MDIconButton:
                    icon: "camera"
                    md_bg_color: 0.22, 0.75, 0.94, 1
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    size_hint: None, None
                    size: "36dp", "36dp"
                    pos_hint: {"center_x": .85, "center_y": .15}
                    on_release: root.open_gallery()

        # DADOS DO USUÁRIO
        MDBoxLayout:
            id: fields_container
            orientation: "vertical"
            adaptive_height: True
            size_hint_x: 1
            spacing: "2dp"

        # BOTÕES DE AÇÃO
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            size_hint_x: 1
            padding: ["10dp", "20dp", "10dp", "0dp"]
            spacing: "5dp"

            ActionRow:
                id: btn_redefinir_senha
                text_label: "Redefinir senha"
                icon_name: "key-outline"
                on_release: root.go_to_reset_password()

            MDSeparator:
                id: sep_redefinir_senha
                height: "1dp"

            ActionRow:
                text_label: "Sair da conta"
                icon_name: "logout"
                on_release: root.logout()

            MDSeparator:
                height: "1dp"

            ActionRow:
                text_label: "Excluir conta"
                icon_name: "delete-forever-outline"
                text_color: 1, 0, 0, 1
                on_release: root.open_delete_dialog()
'''

# Carrega a definição do KV Lang na memória do Kivy
Builder.load_string(KV_PROFILE_TAB)


# ==============================================================================
# COMPONENTES REUTILIZÁVEIS DA UI
# ==============================================================================
class ActionRow(MDCard):
    """Componente de linha clicável reutilizável para ações (Sair, Excluir, Redefinir Senha)."""
    text_label = StringProperty("")
    icon_name = StringProperty("chevron-right")
    text_color = ObjectProperty([0, 0, 0, 1])


class ProfileField(MDBoxLayout):
    """Componente customizado para exibição e edição inline de cada campo do perfil."""
    label_text = StringProperty("")
    api_key = StringProperty("")
    text_value = StringProperty("Carregando...")
    is_email = BooleanProperty(False)
    callback_save = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_value = ""
        self._is_saving_or_canceling = False

    def start_edit(self):
        """Habilita a edição do campo de texto e força a exibição do teclado."""
        self.original_value = self.ids.field_input.text
        self._is_saving_or_canceling = False
        
        # 1. Libera a edição e atualiza a visibilidade dos botões de ação
        self.ids.field_input.readonly = False
        self.ids.btn_edit.opacity = 0
        self.ids.btn_edit.disabled = True
        self.ids.btn_save.opacity = 1
        self.ids.btn_save.disabled = False
        self.ids.btn_cancel.opacity = 1
        self.ids.btn_cancel.disabled = False

        # 2. Ativa o foco com o ATRASO CRÍTICO PARA MOBILE
        # Substituímos a ativação direta por um Clock.schedule_once
        Clock.schedule_once(lambda dt: setattr(self.ids.field_input, 'focus', True), 0.15)

    def cancel_edit(self):
        """Restaura o valor original e bloqueia o campo."""
        self._is_saving_or_canceling = True
        self.ids.field_input.text = self.original_value
        self._lock_field()

    def save_edit(self):
        """Dispara a gravação do novo valor através do callback cadastrado."""
        if self._is_saving_or_canceling:
            return
        if self.ids.field_input.focus:
            self.ids.field_input.focus = False
        if self.callback_save:
            self.callback_save(self.api_key, self.ids.field_input.text, self)

    def on_input_focus(self, instance, value):
        """Método chamado quando o TextInput ganha ou perde o foco."""
        if not value and not self.ids.field_input.readonly and not self._is_saving_or_canceling:
            Clock.schedule_once(lambda dt: self._check_auto_save(), 0.1)

    def _check_auto_save(self):
        """Verifica se deve salvar ou cancelar ao perder o foco."""
        if not self.ids.field_input.readonly and not self._is_saving_or_canceling:
            if self.ids.field_input.text != self.original_value:
                self.save_edit()
            else:
                self.cancel_edit()

    def _lock_field(self):
        """Retorna o campo ao estado somente leitura."""
        self.ids.field_input.readonly = True
        self.ids.field_input.focus = False
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True
        self.ids.btn_cancel.opacity = 0
        self.ids.btn_cancel.disabled = True
        if not self.is_email:
            self.ids.btn_edit.opacity = 1
            self.ids.btn_edit.disabled = False


# ==============================================================================
# CLASSE PRINCIPAL DO CONTEÚDO DA ABA PERFIL
# ==============================================================================
class ProfileTabContent(ScrollView):
    """Controlador principal da aba de Perfil do Usuário."""
    avatar_source = StringProperty("https://cdn-icons-png.flaticon.com/512/149/149071.png")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields_refs = {}
        self.dialog = None
        Clock.schedule_once(self.setup_fields, 0)
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)

    def _get_api_url(self):
        """Retorna a URL base da API configurada no projeto."""
        app = MDApp.get_running_app()
        return getattr(config, 'API_URL', getattr(app, 'api_base_url', ''))

    def _get_access_token(self):
        """Recupera o token JWT armazenado na sessão local."""
        if not store.exists("session"):
            return None
        session = store.get("session")
        token_data = session.get("token")
        if isinstance(token_data, dict):
            return token_data.get("access")
        elif isinstance(token_data, str):
            return token_data
        return None

    @mainthread
    def refresh_data(self):
        """Limpa caches de imagem e reinicia a busca dos dados no servidor."""
        Cache.remove('kv.loader')
        Cache.remove('kv.image')
        
        for field in self.fields_refs.values():
            field.ids.field_input.text = "Carregando..."
        threading.Thread(target=self.load_user_data, daemon=True).start()

    def setup_fields(self, dt):
        """Instancia e adiciona dinamicamente os campos do perfil na interface."""
        self.ids.fields_container.clear_widgets()
        config_campos = [
            {"label": "Nome", "key": "first_name", "email": False},
            {"label": "Sobrenome", "key": "last_name", "email": False},
            {"label": "Usuário", "key": "username", "email": False},
            {"label": "Email", "key": "email", "email": True},
        ]
        for c in config_campos:
            field = ProfileField(label_text=c["label"], api_key=c["key"], is_email=c["email"], callback_save=self.salvar_na_api)
            self.fields_refs[c["key"]] = field
            self.ids.fields_container.add_widget(field)

    # --------------------------------------------------------------------------
    # GERENCIAMENTO E UPLOAD DA FOTO DE PERFIL
    # --------------------------------------------------------------------------
    def open_gallery(self):
        """Abre a galeria garantindo as permissões necessárias no Android."""
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions(
                    [Permission.READ_EXTERNAL_STORAGE, Permission.READ_MEDIA_IMAGES],
                    self._callback_permissao_galeria
                )
                return
            except Exception as e:
                print(f"VIGIAA DEBUG: Erro ao solicitar permissões: {e}")

        self._abrir_filechooser()

    def _callback_permissao_galeria(self, permissions, grants):
        """Callback executado após o usuário responder ao alerta de permissão."""
        if any(grants):
            self._abrir_filechooser()
        else:
            self.mostrar_aviso("Permissão negada para acessar a galeria.")

    def _abrir_filechooser(self):
        """Abre o seletor de arquivos nativo do Plyer."""
        try:
            from plyer import filechooser
            filechooser.open_file(
                title="Escolha sua foto de perfil",
                filters=[("Imagens", "*.png", "*.jpg", "*.jpeg")],
                on_selection=self.process_selection
            )
        except Exception as e:
            self.mostrar_aviso("Erro ao abrir galeria.")

    def process_selection(self, selection):
        """Processa a imagem selecionada copiando-a na thread principal antes do upload."""
        if selection:
            path = selection[0]
            
            # Copia o arquivo no fluxo principal para evitar erros de JVM/Thread no Android
            caminho_interno = self.garantir_arquivo_acessivel(path)
            
            if caminho_interno:
                Cache.remove('kv.image')
                Cache.remove('kv.loader')
                
                # Deixe apenas o caminho real do arquivo
                prefixo = "file://" if platform == "android" else ""
                self.avatar_source = f"{prefixo}{caminho_interno}"
                
                # Dispara APENAS a requisição de upload em segundo plano
                threading.Thread(target=self._worker_upload_avatar, args=(caminho_interno,), daemon=True).start()
            else:
                self.mostrar_aviso("Não foi possível acessar a imagem selecionada.")

    def garantir_arquivo_acessivel(self, original_path):
        """
        Copia a imagem para o diretório privado do aplicativo.
        Utiliza Java Streams nativas no Android para evitar falhas de conversão de tipos com Pyjnius.
        """
        if not original_path:
            return None

        uri_str = str(original_path)
        app_folder = MDApp.get_running_app().user_data_dir

        # Define a extensão do arquivo
        ext = "png"
        if "." in uri_str and "/" not in uri_str.split(".")[-1]:
            ext_candidata = uri_str.split(".")[-1].lower()
            if len(ext_candidata) <= 4:
                ext = ext_candidata

        dest_path = os.path.join(app_folder, f"temp_profile_{int(time.time())}.{ext}")

        # 1. Tratamento para Android e URIs "content://"
        if platform == "android" and uri_str.startswith("content://"):
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Uri = autoclass("android.net.Uri")
                FileOutputStream = autoclass("java.io.FileOutputStream")
                File = autoclass("java.io.File")

                context = PythonActivity.mActivity
                content_resolver = context.getContentResolver()
                input_stream = content_resolver.openInputStream(Uri.parse(uri_str))
                output_stream = FileOutputStream(File(dest_path))

                # Tenta copiar via FileUtils (Android 10+ / API 29+)
                try:
                    FileUtils = autoclass("android.os.FileUtils")
                    FileUtils.copy(input_stream, output_stream)
                except Exception:
                    # Fallback com buffer Java nativo para versões legadas do Android
                    from jnius import jarray, c_byte
                    buffer = jarray('b')(1024 * 64) # 'b' representa byte no Java
                    while True:
                        bytes_read = input_stream.read(buffer)
                        if bytes_read == -1:
                            break
                        output_stream.write(buffer, 0, bytes_read)

                input_stream.close()
                output_stream.close()
                print(f"VIGIAA DEBUG: Foto copiada com sucesso via Java Streams -> {dest_path}")
                return dest_path
            except Exception as e:
                print(f"VIGIAA DEBUG ERROR: ContentResolver falhou: {e}")

        # 2. Tratamento para Desktop / arquivos físicos com 'file://' ou caminho direto
        try:
            clean_path = uri_str.replace("file://", "")
            if os.path.exists(clean_path):
                shutil.copy2(clean_path, dest_path)
                print(f"VIGIAA DEBUG: Foto copiada via shutil -> {dest_path}")
                return dest_path
        except Exception as e:
            print(f"VIGIAA DEBUG ERROR: shutil falhou: {e}")

        return None

    def _preparar_e_subir(self, path):
        """Prepara o arquivo e inicia a thread de upload para o servidor."""
        caminho_interno = self.garantir_arquivo_acessivel(path)
        
        if caminho_interno:
            print(f"VIGIAA DEBUG: Caminho copiado com sucesso: {caminho_interno}")
            
            Cache.remove('kv.image')
            Cache.remove('kv.loader')
            
            @mainthread
            def atualizar_ui(dt):
                prefixo = "file://" if platform == "android" else ""
                self.avatar_source = f"{prefixo}{caminho_interno}"
            Clock.schedule_once(atualizar_ui, 0.1)

            threading.Thread(target=self._worker_upload_avatar, args=(caminho_interno,), daemon=True).start()
        else:
            self.mostrar_aviso("Falha ao carregar a imagem da galeria.")

    def _worker_upload_avatar(self, file_path):
        """Worker em segundo plano para envio multipart/form-data da foto ao backend."""
        access_token = self._get_access_token()
        if not access_token:
            self.mostrar_aviso("Token de acesso não encontrado.")
            return

        try:
            url = f"{self._get_api_url()}/api/profile/"
            
            if not file_path or not os.path.exists(file_path):
                self.mostrar_aviso("Erro interno ao ler arquivo gerado.")
                return

            headers = {
                "Authorization": f"Bearer {access_token.strip()}",
                "ngrok-skip-browser-warning": "true",
                "User-Agent": "KivyApp"
            }

            with open(file_path, 'rb') as f:
                files = {'photo': ('avatar_vigiaa.png', f, 'image/png')}
                res = requests.patch(
                    url, 
                    headers=headers, 
                    files=files, 
                    timeout=30,
                    verify=False
                )
                
            if res.status_code == 200:
                self.mostrar_aviso("Foto atualizada com sucesso!")
                Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)
            else:
                print(f"VIGIAA DEBUG: Erro no upload ({res.status_code}): {res.text}")
                self.mostrar_aviso(f"Erro no servidor: {res.status_code}")
                
        except Exception as e:
            print(f"VIGIAA DEBUG: Erro no upload: {str(e)}")
            self.mostrar_aviso(f"Erro de conexão: {str(e)[:25]}")


    # --------------------------------------------------------------------------
    # REQUISIÇÕES E ATUALIZAÇÕES DOS DADOS DE TEXTO
    # --------------------------------------------------------------------------
    def load_user_data(self):
        """Thread worker para busca dos dados cadastrais do perfil."""
        access_token = self._get_access_token()
        if not access_token:
            print("VIGIAA DEBUG: [ERRO] Token de acesso não encontrado na sessão.")
            return

        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "KivyApp"
        }

        try:
            url = f"{self._get_api_url()}/api/profile/"
            print(f"VIGIAA DEBUG: Enviando requisição de perfil para -> {url}")
            
            res = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if res.status_code == 200:
                data = res.json()
                print("VIGIAA DEBUG: Dados do perfil recebidos com sucesso!")
                Clock.schedule_once(lambda dt: self.update_ui_fields(data), 0)
            else:
                print(f"VIGIAA DEBUG: Erro da API -> {res.text[:150]}")
                
        except Exception as e:
            print(f"VIGIAA DEBUG: Exceção na requisição -> {e}")

    @mainthread
    def update_ui_fields(self, data):
        """Atualiza a interface principal com as informações retornadas pela API."""
        for key, field in self.fields_refs.items():
            if key in data:
                field.ids.field_input.text = str(data.get(key, ""))
        
        if data.get("photo"):
            foto_url = data.get("photo")
            if not foto_url.startswith('http'):
                foto_url = f"{self._get_api_url()}{foto_url}"
        
            self.avatar_source = f"{foto_url}?t={int(time.time())}"

        # Se o usuário se cadastrou por OAuth (ex: Google) e não tem senha local, esconde a opção
        if data.get("tem_senha") is False:
            self.ids.btn_redefinir_senha.opacity = 0
            self.ids.btn_redefinir_senha.disabled = True
            self.ids.btn_redefinir_senha.height = "0dp"
            self.ids.sep_redefinir_senha.height = "0dp"

    def salvar_na_api(self, api_key, novo_valor, field_instance):
        """Inicia a thread de alteração de um campo específico."""
        threading.Thread(target=self._worker_save, args=(api_key, novo_valor, field_instance), daemon=True).start()

    def _worker_save(self, api_key, novo_valor, field_instance):
        """Worker em segundo plano para envio do PATCH de alteração do campo."""
        access_token = self._get_access_token()
        if not access_token:
            Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)
            return

        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "KivyApp"
        }
        try:
            url = f"{self._get_api_url()}/api/profile/"
            res = requests.patch(url, json={api_key: novo_valor}, headers=headers, verify=False)
            if res.status_code == 200:
                self.mostrar_aviso(f"{field_instance.label_text} atualizado!")
                Clock.schedule_once(lambda dt: field_instance._lock_field(), 0)
            else:
                Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)
        except Exception:
            Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)

    # --------------------------------------------------------------------------
    # NAVEGAÇÃO E SESSÃO DO USUÁRIO
    # --------------------------------------------------------------------------
    def logout(self):
        """Encerra a sessão atual, limpa a store local e retorna à tela de login."""
        app = MDApp.get_running_app()
        if store.exists("session"):
            store.delete("session")
        app.root.current = 'login'

    def go_to_reset_password(self):
        """Redireciona para a tela de alteração de senha."""
        MDApp.get_running_app().root.current = 'change_password'

    def open_delete_dialog(self):
        """Exibe o diálogo de confirmação para exclusão permanente da conta."""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Excluir Conta",
                text="Deseja desativar sua conta permanentemente? Esta ação não pode ser desfeita.",
                buttons=[
                    MDFlatButton(
                        text="Cancelar", 
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Confirmar", 
                        text_color=(1, 0, 0, 1), 
                        on_release=self.delete_account_action
                    )
                ],
            )
        self.dialog.open()

    def delete_account_action(self, *args):
        """Handler da confirmação do diálogo de exclusão."""
        if self.dialog:
            self.dialog.dismiss()
        threading.Thread(target=self._worker_delete, daemon=True).start()

    def _worker_delete(self):
        """Worker em segundo plano para envio da requisição DELETE da conta."""
        access_token = self._get_access_token()
        if not access_token:
            return

        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "KivyApp"
        }
        try:
            url = f"{self._get_api_url()}/api/delete-account/"
            res = requests.delete(url, headers=headers, verify=False)
            if res.status_code == 200:
                self.mostrar_aviso("Conta excluída.")
                Clock.schedule_once(lambda dt: self.logout(), 0)
        except Exception:
            pass

    @mainthread
    def mostrar_aviso(self, texto):
        """Exibe uma mensagem rápida na tela através de um MDSnackbar."""
        MDSnackbar(MDLabel(text=texto, theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()