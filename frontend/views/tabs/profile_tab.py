from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.clock import mainthread, Clock
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
import requests
import threading
import config

store = JsonStore('sessao_app.json')

KV_PROFILE_TAB = '''
<ProfileField>:
    orientation: "horizontal"
    adaptive_height: True
    size_hint_x: 1
    padding: ["8dp", "8dp", "8dp", "8dp"]
    spacing: "10dp"
    
    MDLabel:
        text: root.label_text
        bold: True
        size_hint_x: 0.28
        font_size: "14sp"
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1
        halign: "left"
        
    MDTextField:
        id: field_input
        text: root.text_value
        readonly: True
        size_hint_x: 0.57
        font_size: "15sp"
        text_color_normal: 0.3, 0.3, 0.3, 1
        line_color_normal: 0, 0, 0, 0
        multiline: False
        
    MDBoxLayout:
        size_hint_x: 0.15
        adaptive_width: True
        spacing: "2dp"
        pos_hint: {"center_y": .5}
        
        MDIconButton:
            id: btn_edit
            icon: "pencil-outline"
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
        padding: ["12dp", "10dp", "12dp", "20dp"]
        spacing: "10dp"
        adaptive_height: True

        # AVATAR CENTRALIZADO COM ANCHOR (Segurança total contra desalinhamento)
        AnchorLayout:
            anchor_x: "center"
            size_hint_y: None
            height: "120dp"
            padding: [0, "10dp", 0, "10dp"]

            MDCard:
                size_hint: None, None
                size: "100dp", "100dp"
                radius: [50, 50, 50, 50]
                md_bg_color: 0.95, 0.95, 0.95, 1
                elevation: 0
                
                MDIcon:
                    icon: "account"
                    font_size: "60sp"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.75, 0.94, 1
                    pos_hint: {"center_x": .5, "center_y": .5}

        # SWITCH DE EXIBIÇÃO (Recuperado!)
        MDBoxLayout:
            adaptive_height: True
            padding: ["4dp", "10dp", "4dp", "10dp"]
            size_hint_x: 1
            
            MDLabel:
                text: "Modo de exibição"
                bold: True
                font_size: "16sp"
                size_hint_x: 0.8
            
            MDSwitch:
                active: False
                pos_hint: {"center_y": .5}
                thumb_color_active: 0.22, 0.75, 0.94, 1
                track_color_active: 0.22, 0.75, 0.94, 0.5

        MDSeparator:

        # DADOS DO USUÁRIO
        MDBoxLayout:
            id: fields_container
            orientation: "vertical"
            adaptive_height: True
            spacing: "2dp"
            size_hint_x: 1

        # BOTÕES DE AÇÃO (Recuperados!)
        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: "2dp"
            padding: ["0dp", "10dp", "0dp", "0dp"]
            size_hint_x: 1

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
        self.ids.field_input.text_color_normal = (0, 0, 0, 1)
        self.ids.field_input.line_color_normal = (0.5, 0.5, 0.5, 1)
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
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)

    @mainthread
    def refresh_data(self):
        for field in self.fields_refs.values():
            field.text_value = "Carregando..."
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
            field = ProfileField(
                label_text=c["label"], 
                api_key=c["key"], 
                is_email=c["email"],
                callback_save=self.salvar_na_api
            )
            self.fields_refs[c["key"]] = field
            self.ids.fields_container.add_widget(field)

    def load_user_data(self):
        app = MDApp.get_running_app()
        token = getattr(app, "vigiaa_token", None)
        if not token and store.exists("session"):
            token = store.get("session")["token"]
            
        if not token: return
            
        try:
            url = f"{config.API_URL}/api/profile/"
            res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                Clock.schedule_once(lambda dt: self.update_ui_fields(data), 0)
            elif res.status_code in [401, 403]:
                Clock.schedule_once(lambda dt: self.logout(), 0)
        except:
            pass

    @mainthread
    def update_ui_fields(self, data):
        for key, field in self.fields_refs.items():
            if key in data:
                val = data.get(key, "")
                field.text_value = val
                field.ids.field_input.text = val

        if data.get("tem_senha") is False:
            self.ids.btn_redefinir_senha.opacity = 0
            self.ids.btn_redefinir_senha.disabled = True
            self.ids.btn_redefinir_senha.height = "0dp" 
            self.ids.sep_redefinir_senha.height = "0dp"

    def salvar_na_api(self, api_key, novo_valor, field_instance):
        threading.Thread(target=self._worker_save, args=(api_key, novo_valor, field_instance), daemon=True).start()

    def _worker_save(self, api_key, novo_valor, field_instance):
        if not store.exists("session"): return
        token = store.get("session")["token"]
        
        try:
            res = requests.patch(
                f"{config.API_URL}/api/profile/",
                json={api_key: novo_valor},
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code == 200:
                self.mostrar_aviso(f"{field_instance.label_text} atualizado!")
                Clock.schedule_once(lambda dt: field_instance._lock_field(), 0)
            else:
                self.mostrar_aviso("Erro ao salvar.")
                Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)
        except:
            self.mostrar_aviso("Erro de conexão.")
            Clock.schedule_once(lambda dt: field_instance.cancel_edit(), 0)

    def logout(self):
        app = MDApp.get_running_app()
        if store.exists("session"): store.delete("session")
        if store.exists("current_case"): store.delete("current_case")
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
        if not store.exists("session"): return
        token = store.get("session")["token"]
        try:
            res = requests.delete(f"{config.API_URL}/api/delete-account/", headers={"Authorization": f"Bearer {token}"})
            if res.status_code == 200:
                self.mostrar_aviso("Conta excluída.")
                Clock.schedule_once(lambda dt: self.logout(), 0)
        except:
            pass

    @mainthread
    def mostrar_aviso(self, texto):
        MDSnackbar(MDLabel(text=texto, theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()