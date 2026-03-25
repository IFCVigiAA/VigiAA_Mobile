from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
import requests
import threading
import config

store = JsonStore('vigiaa_storage.json')

KV_PROFILE_TAB = '''
<ProfileField>:
    orientation: "horizontal"
    adaptive_height: True
    padding: ["0dp", "5dp", "0dp", "5dp"]
    
    MDLabel:
        text: root.label_text
        bold: True
        size_hint_x: 0.35
        font_size: "14sp"
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        
    MDTextField:
        id: field_input
        text: root.text_value
        readonly: True
        size_hint_x: 0.45
        font_size: "14sp"
        text_color_normal: 0.5, 0.5, 0.5, 1  # Cinza quando bloqueado
        line_color_normal: 0, 0, 0, 0        # Sem linha quando bloqueado
        
    MDBoxLayout:
        size_hint_x: 0.2
        adaptive_width: True
        spacing: "2dp"
        
        MDIconButton:
            id: btn_edit
            icon: "pencil"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            opacity: 0 if root.is_email else 1
            disabled: root.is_email
            on_release: root.start_edit()
            
        MDIconButton:
            id: btn_save
            icon: "check"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 0, 0.7, 0, 1
            opacity: 0
            disabled: True
            on_release: root.save_edit()
            
        MDIconButton:
            id: btn_cancel
            icon: "close"
            icon_size: "20sp"
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
            opacity: 0
            disabled: True
            on_release: root.cancel_edit()

<ActionRow@MDCard>:
    size_hint_y: None
    height: "50dp"
    elevation: 0
    md_bg_color: 1, 1, 1, 1
    ripple_behavior: True
    padding: ["10dp", "0dp", "10dp", "0dp"]
    
    text_label: ""
    icon_name: "chevron-right"
    text_color: 0, 0, 0, 1
    
    MDLabel:
        text: root.text_label
        bold: True
        font_size: "16sp"
        theme_text_color: "Custom"
        text_color: root.text_color
        
    MDIcon:
        icon: root.icon_name
        theme_text_color: "Custom"
        text_color: root.text_color
        pos_hint: {"center_y": .5}

<ProfileTabContent>:
    md_bg_color: 1, 1, 1, 1

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "10dp"
        adaptive_height: True

        # AVATAR
        MDFloatLayout:
            size_hint_y: None
            height: "100dp"
            
            MDCard:
                size_hint: None, None
                size: "80dp", "80dp"
                pos_hint: {"center_x": .5, "center_y": .5}
                radius: [40, 40, 40, 40]
                md_bg_color: 0.9, 0.9, 0.9, 1
                elevation: 0
                
                MDIcon:
                    icon: "account"
                    font_size: "50sp"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1
                    pos_hint: {"center_x": .5, "center_y": .5}

        # SWITCH DE EXIBIÇÃO
        MDBoxLayout:
            adaptive_height: True
            padding: ["0dp", "10dp", "0dp", "10dp"]
            
            MDLabel:
                text: "Modo de exibição"
                bold: True
                font_size: "16sp"
            
            MDSwitch:
                active: False
                pos_hint: {"center_y": .5}
                icon_active: "check"
                thumb_color_active: 0.22, 0.75, 0.94, 1
                track_color_active: 0.22, 0.75, 0.94, 0.5

        MDSeparator:

        # DADOS DO USUÁRIO
        MDBoxLayout:
            id: fields_container
            orientation: "vertical"
            adaptive_height: True
            spacing: "5dp"

        # BOTÕES DE AÇÃO
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: "5dp"
            padding: ["0dp", "10dp", "0dp", "0dp"]

            ActionRow:
                id: btn_redefinir_senha
                text_label: "Redefinir senha"
                icon_name: "chevron-right"
                on_release: root.go_to_reset_password()

            MDSeparator:
                id: sep_redefinir_senha

            ActionRow:
                text_label: "Sair da conta"
                icon_name: "logout"
                on_release: root.logout()

            MDSeparator:

            ActionRow:
                text_label: "Excluir conta"
                icon_name: "delete-forever"
                text_color: 1, 0, 0, 1
                on_release: root.open_delete_dialog()
'''
Builder.load_string(KV_PROFILE_TAB)

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
        self.ids.field_input.text_color_normal = (0, 0, 0, 1) # Fica preto
        self.ids.field_input.line_color_normal = (0.5, 0.5, 0.5, 1) # Mostra a linha
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
            # Chama a função lá na tela principal para ir na internet
            self.callback_save(self.api_key, self.ids.field_input.text, self)

    def _lock_field(self):
        self.ids.field_input.readonly = True
        self.ids.field_input.text_color_normal = (0.5, 0.5, 0.5, 1)
        self.ids.field_input.line_color_normal = (0, 0, 0, 0)
        self.ids.field_input.focus = False
        
        self.ids.btn_edit.opacity = 1
        self.ids.btn_edit.disabled = False
        self.ids.btn_save.opacity = 0
        self.ids.btn_save.disabled = True
        self.ids.btn_cancel.opacity = 0
        self.ids.btn_cancel.disabled = True


class ProfileTabContent(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields_refs = {}
        self.dialog = None
        Clock.schedule_once(self.setup_fields, 0)
        # Trocamos a chamada antiga por essa nova que pode ser repetida:
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)

    @mainthread
    def refresh_data(self):
        # Volta tudo para 'Carregando...' visualmente
        for field in self.fields_refs.values():
            field.text_value = "Carregando..."
            field.ids.field_input.text = "Carregando..."
            
        # Manda a thread buscar os dados novos na internet
        threading.Thread(target=self.load_user_data).start()

    def setup_fields(self, dt):
        config_campos = [
            {"label": "Nome", "key": "first_name", "email": False},
            {"label": "Sobrenome", "key": "last_name", "email": False},
            {"label": "Usuário", "key": "username", "email": False},
            {"label": "Email", "key": "email", "email": True},
        ]
        
        for c in config_campos:
            field = ProfileField(
                label_text=c["label"], 
                api_key=c["key"], 
                is_email=c["email"],
                callback_save=self.salvar_na_api
            )
            self.fields_refs[c["key"]] = field
            self.ids.fields_container.add_widget(field)

    def load_user_data(self):
        store = JsonStore('vigiaa_storage.json')
        if not store.exists("session"): return
        token = store.get("session")["token"]
        
        try:
            res = requests.get(f"{config.API_URL}/api/profile/", headers={"Authorization": f"Bearer {token}"})
            if res.status_code == 200:
                data = res.json()
                self.update_ui_fields(data)
        except Exception as ex:
            print(f"Erro ao carregar perfil: {ex}")

    @mainthread
    def update_ui_fields(self, data):
        print("DADOS DA API:", data)
        for key, field in self.fields_refs.items():
            if key in data:
                field.text_value = data.get(key, "")
                field.ids.field_input.text = data.get(key, "")

            if data.get("tem_senha") is False:
                self.ids.btn_redefinir_senha.opacity = 0
                self.ids.btn_redefinir_senha.disabled = True
                self.ids.btn_redefinir_senha.height = "0dp" 
                
                self.ids.sep_redefinir_senha.opacity = 0
                self.ids.sep_redefinir_senha.height = "0dp"

    def salvar_na_api(self, api_key, novo_valor, field_instance):
        threading.Thread(target=self._worker_save, args=(api_key, novo_valor, field_instance)).start()

    def _worker_save(self, api_key, novo_valor, field_instance):
        store = JsonStore('vigiaa_storage.json')
        if not store.exists("session"): return
        token = store.get("session")["token"]
        
        try:
            res = requests.patch(
                f"{config.API_URL}/api/profile/",
                json={api_key: novo_valor},
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code == 200:
                self.mostrar_aviso(f"{field_instance.label_text} atualizado com sucesso!")
                Clock.schedule_once(lambda dt: field_instance._lock_field(), 0)
            else:
                self.mostrar_aviso("Erro ao salvar dados.")
                Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)
        except Exception as e:
            self.mostrar_aviso(f"Erro de conexão: {e}")
            Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)

    # --- AÇÕES DA CONTA ---
    def logout(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        # A TRAVA MESTRA: Avisa o app inteiro que estamos forçando a saída!
        app.force_logout = True 

        # Apaga os arquivos (O seu código perfeito continua aqui)
        if store.exists("session"):
            store.delete("session")

        if store.exists("current_case"):
            store.delete("current_case")
            
        # --- A FAXINA ---
        for field in self.fields_refs.values():
            field.text_value = "Carregando..."
            field.ids.field_input.text = "Carregando..."
            
        if 'btn_redefinir_senha' in self.ids:
            self.ids.btn_redefinir_senha.opacity = 1
            self.ids.btn_redefinir_senha.disabled = False
            self.ids.btn_redefinir_senha.height = "50dp"
            self.ids.sep_redefinir_senha.opacity = 1
            self.ids.sep_redefinir_senha.height = "1dp"

        app.root.current = 'login'

    def go_to_reset_password(self):
        MDApp.get_running_app().root.current = 'change_password'

    def open_delete_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Excluir Conta",
                text="Tem certeza? Isso desativará sua conta permanentemente.",
                buttons=[
                    MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="Sim, Excluir", text_color=(1, 0, 0, 1), on_release=self.delete_account_action)
                ],
            )
        self.dialog.open()

    def delete_account_action(self, *args):
        self.dialog.dismiss()
        threading.Thread(target=self._worker_delete).start()

    def _worker_delete(self):
        store = JsonStore('vigiaa_storage.json')
        if not store.exists("session"): return
        token = store.get("session")["token"]
        try:
            res = requests.delete(f"{config.API_URL}/api/delete-account/", headers={"Authorization": f"Bearer {token}"})
            if res.status_code == 200:
                self.mostrar_aviso("Conta desativada com sucesso.")
                Clock.schedule_once(lambda dt: self.logout(), 0)
            else:
                self.mostrar_aviso("Erro ao desativar conta.")
        except Exception as e:
            self.mostrar_aviso("Sem conexão com a internet.")

    @mainthread
    def mostrar_aviso(self, texto):
        MDSnackbar(
            MDLabel(
                text=texto,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1) # Letra branca para ficar visível no fundo escuro
            )
        ).open()