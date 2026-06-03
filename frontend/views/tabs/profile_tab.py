import certifi
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.app import MDApp
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
import requests
import threading
import config
import os
from kivy.utils import platform
import time  # <--- ADICIONE ESTE
from kivy.utils import platform  # <--- ADICIONE ESTE

store = JsonStore('sessao_app.json')

KV_PROFILE_TAB = '''
<ProfileField>:
    orientation: "horizontal"
    size_hint_y: None
    height: "50dp"
    size_hint_x: 1
    # Margem direita ajustada para 10dp para alinhar o botão exatamente com o fim da linha cinza
    padding: ["12dp", 0, "10dp", 0]
    spacing: "10dp"
    
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
        font_size: "14sp"
        pos_hint: {"center_y": .5}
        
    TextInput:
        id: field_input
        text: root.text_value
        readonly: True
        size_hint_x: 1 
        font_size: "15sp"
        foreground_color: (0, 0, 0, 1) if not self.readonly else (0.4, 0.4, 0.4, 1)
        background_color: 0, 0, 0, 0
        padding: [0, (self.height - self.line_height) / 2]
        multiline: False
        pos_hint: {"center_y": .5}
        cursor_color: 0.22, 0.75, 0.94, 1

    MDBoxLayout:
        size_hint: None, None
        height: "36dp"
        # Controle absoluto: 0dp se for email, 76dp para editar (2 botões + espaço) ou 36dp (só o lápis)
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
            # Força o bloqueio do tamanho físico da área de toque
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

Builder.load_string(KV_PROFILE_TAB)

class ActionRow(MDCard):
    text_label = StringProperty("")
    icon_name = StringProperty("chevron-right")
    text_color = ObjectProperty([0, 0, 0, 1])

class ProfileField(MDBoxLayout):
    label_text = StringProperty("")
    api_key = StringProperty("")
    text_value = StringProperty("Carregando...")
    is_email = BooleanProperty(False)
    callback_save = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_value = ""

    def start_edit(self):
        self.original_value = self.ids.field_input.text
        self.ids.field_input.readonly = False
        self.ids.field_input.focus = True
        self.ids.btn_edit.opacity = 0
        self.ids.btn_edit.disabled = True
        self.ids.btn_save.opacity = 1
        self.ids.btn_save.disabled = False
        self.ids.btn_cancel.opacity = 1
        self.ids.btn_cancel.disabled = False

    def cancel_edit(self):
        self.ids.field_input.text = self.original_value
        self._lock_field()

    def save_edit(self):
        if self.callback_save:
            self.callback_save(self.api_key, self.ids.field_input.text, self)

    def _lock_field(self):
        self.ids.field_input.readonly = True
        self.ids.field_input.focus = False
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True
        self.ids.btn_cancel.opacity = 0
        self.ids.btn_cancel.disabled = True
        if not self.is_email:
            self.ids.btn_edit.opacity = 1
            self.ids.btn_edit.disabled = False

class ProfileTabContent(ScrollView):
    avatar_source = StringProperty("https://cdn-icons-png.flaticon.com/512/149/149071.png")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields_refs = {}
        self.dialog = None
        Clock.schedule_once(self.setup_fields, 0)
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)

    @mainthread
    def refresh_data(self):
        # Limpa o cache da imagem para forçar o Kivy a baixar a nova
        from kivy.cache import Cache
        Cache.remove('kv.loader')
        Cache.remove('kv.image')
        
        for field in self.fields_refs.values():
            field.ids.field_input.text = "Carregando..."
        threading.Thread(target=self.load_user_data, daemon=True).start()

    def setup_fields(self, dt):
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

    def open_gallery(self):
        try:
            from plyer import filechooser
            filechooser.open_file(
                title="Escolha sua foto de perfil",
                filters=[("Imagens", "*.png", "*.jpg", "*.jpeg")],
                on_selection=self.process_selection
            )
        except:
            self.mostrar_aviso("Erro ao abrir galeria.")

    def process_selection(self, selection):
        if selection:
            path = selection[0]
            # No Android, o path costuma vir como 'content://...'
            threading.Thread(target=self._preparar_e_subir, args=(path,), daemon=True).start()

    def _preparar_e_subir(self, path):
        # 1. Faz a cópia para a pasta segura do app
        caminho_interno = self.copiar_para_pasta_app(path)
        
        if caminho_interno:
            print(f"VIGIAA DEBUG: Caminho interno: {caminho_interno}")
            
            # 2. LIMPEZA DE CACHE FORÇADA
            from kivy.cache import Cache
            Cache.remove('kv.image')
            Cache.remove('kv.loader')
            
            # 3. Atualiza a UI no Fio Principal
            @mainthread
            def atualizar_ui(dt):
                # Para exibir na "bolinha" (FitImage) no Android:
                prefixo = "file://" if platform == "android" else ""
                # caminho_interno deve ser o caminho puro: /data/user/0/...
                self.avatar_source = f"{prefixo}{caminho_interno}"
            
            Clock.schedule_once(atualizar_ui, 0.1)

            # --- AQUI ESTAVA O ERRO: Chamada para subir pro servidor ---
            # Agora que o arquivo está na pasta do app, chamamos o upload
            threading.Thread(target=self._worker_upload_avatar, args=(caminho_interno,), daemon=True).start()

    def copiar_para_pasta_app(self, uri_origem):
        """Abre o arquivo e salva na pasta do VigiAA sem depender de bibliotecas pesadas de URI"""
        from kivy.utils import platform
        from kivymd.app import MDApp
        import shutil
        import os
        import time

        app_folder = MDApp.get_running_app().user_data_dir
        # Garante um nome único para não usar cache velho
        dest_path = os.path.join(app_folder, f"perfil_{int(time.time())}.jpg")
        
        uri_str = str(uri_origem).replace("file://", "", 1)

        # 1. A BALA DE PRATA: Usar o Java NIO para ler o 'content://' nativamente
        if platform == 'android' and uri_str.startswith('content://'):
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Uri = autoclass('android.net.Uri')
                Paths = autoclass('java.nio.file.Paths')
                Files = autoclass('java.nio.file.Files')

                activity = PythonActivity.mActivity
                uri_obj = Uri.parse(uri_str)
                
                # Abre um túnel de dados direto com o sistema Android
                input_stream = activity.getContentResolver().openInputStream(uri_obj)
                dest_file = Paths.get(dest_path)
                
                # O Java faz a cópia em nível de sistema, ignorando o bloqueio do Python!
                Files.copy(input_stream, dest_file)
                input_stream.close()
                
                return dest_path
            except Exception as e:
                print(f"VIGIAA DEBUG: Falha no JNIUS NIO: {e}")
                pass # Se falhar, tenta o bloco debaixo

        # 2. Se for um caminho comum (PC ou Android antigo), tenta o shutil
        try:
            shutil.copy2(uri_str, dest_path)
            return dest_path
        except Exception as e:
            print(f"VIGIAA DEBUG ERROR: Falha total na cópia: {e}")
            return uri_str # Última esperança, devolve o original
            
    def garantir_arquivo_acessivel(self, original_path):
        """Copia a imagem para a pasta do app para que o Python consiga ler"""
        import shutil
        from kivy.app import App
        
        try:
            # Caminho da pasta interna do app
            app_folder = App.get_running_app().user_data_dir
            ext = original_path.split('.')[-1]
            dest_path = os.path.join(app_folder, f"temp_profile_upload.{ext}")
            
            # Se for um caminho 'content://', o Plyer já tentou converter, 
            # mas o shutil.copy2 garante que o binário seja movido para onde temos permissão.
            shutil.copy2(original_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"ERRO AO COPIAR ARQUIVO: {e}")
            return original_path # tenta o original se falhar

    def _worker_upload_avatar(self, file_path):
        session = store.get("session") if store.exists("session") else None
        token = session["token"] if session else None
        if not token: return
        
        try:
            url = f"{config.API_URL}/api/profile/"
            
            if not file_path or not os.path.exists(file_path):
                 self.mostrar_aviso("Erro: Arquivo de imagem não encontrado.")
                 return

            with open(file_path, 'rb') as f:
                # O empacotamento exato para o Django aceitar no Android
                files = {'photo': ('avatar_vigiaa.jpg', f, 'image/jpeg')}
                
                res = requests.patch(
                    url, 
                    headers={"Authorization": f"Bearer {token}"}, 
                    files=files, 
                    timeout=30,
                    verify=False # <-- DESLIGA O SSL PARA O UPLOAD NO ANDROID
                )
                
            if res.status_code == 200:
                self.mostrar_aviso("Foto atualizada com sucesso!")
                Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)
            else:
                self.mostrar_aviso(f"Erro do Servidor ao salvar: {res.status_code}")
                
        except Exception as e:
            # SE A THREAD QUEBRAR, MOSTRA O MOTIVO EXATO NA TELA!
            print(f"VIGIAA DEBUG: Erro detalhado no upload: {str(e)}")
            self.mostrar_aviso(f"Falha no upload: {str(e)[:40]}...")

    def load_user_data(self):
        token = store.get("session")["token"] if store.exists("session") else None
        if not token: return
        try:
            url = f"{config.API_URL}/api/profile/"
            res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                Clock.schedule_once(lambda dt: self.update_ui_fields(data), 0)
        except: pass

    @mainthread
    def update_ui_fields(self, data):
        import time # Import necessário para gerar o marcador de tempo
        
        # 1. Atualiza os campos de texto (Nome, Sobrenome, etc.)
        for key, field in self.fields_refs.items():
            if key in data:
                field.ids.field_input.text = str(data.get(key, ""))
        
        # 2. Atualiza a foto de perfil com "Cache Buster"
        if data.get("photo"):
            foto_url = data.get("photo")
            # Se a URL vier sem o domínio, anexe o config.API_URL
            if not foto_url.startswith('http'):
                foto_url = f"{config.API_URL}{foto_url}"
        
        # O Cache Buster (?t=...) é OBRIGATÓRIO para a foto atualizar ao voltar na tela
            self.avatar_source = f"{foto_url}?t={int(time.time())}"

        # 3. Esconde o botão de redefinir senha se for login social (Google/Facebook)
        if data.get("tem_senha") is False:
            self.ids.btn_redefinir_senha.opacity = 0
            self.ids.btn_redefinir_senha.disabled = True
            self.ids.btn_redefinir_senha.height = "0dp"
            self.ids.sep_redefinir_senha.height = "0dp"

    def salvar_na_api(self, api_key, novo_valor, field_instance):
        threading.Thread(target=self._worker_save, args=(api_key, novo_valor, field_instance), daemon=True).start()

    def _worker_save(self, api_key, novo_valor, field_instance):
        token = store.get("session")["token"]
        try:
            res = requests.patch(f"{config.API_URL}/api/profile/", json={api_key: novo_valor}, headers={"Authorization": f"Bearer {token}"})
            if res.status_code == 200:
                self.mostrar_aviso(f"{field_instance.label_text} atualizado!")
                Clock.schedule_once(lambda dt: field_instance._lock_field(), 0)
            else:
                Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)
        except:
            Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)

    def logout(self):
        app = MDApp.get_running_app()
        if store.exists("session"): store.delete("session")
        app.root.current = 'login'

    def go_to_reset_password(self):
        MDApp.get_running_app().root.current = 'change_password'

    def open_delete_dialog(self):
        self.dialog = MDDialog(
            title="Excluir Conta",
            text="Deseja desativar sua conta permanentemente?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Confirmar", text_color=(1, 0, 0, 1), on_release=self.delete_account_action)
            ],
        )
        self.dialog.open()

    def delete_account_action(self, *args):
        self.dialog.dismiss()
        threading.Thread(target=self._worker_delete, daemon=True).start()

    def _worker_delete(self):
        token = store.get("session")["token"]
        try:
            res = requests.delete(f"{config.API_URL}/api/delete-account/", headers={"Authorization": f"Bearer {token}"})
            if res.status_code == 200:
                self.mostrar_aviso("Conta excluída.")
                Clock.schedule_once(lambda dt: self.logout(), 0)
        except: pass

    @mainthread
    def mostrar_aviso(self, texto):
        MDSnackbar(MDLabel(text=texto, theme_text_color="Custom", text_color=(1,1,1,1))).open()