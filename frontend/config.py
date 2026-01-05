import flet as ft

try:
    ICONS = ft.Icons
except AttributeError:
    ICONS = ft.icons

# O link exato do seu Ngrok apontando para a API
API_URL = "https://unreconciled-unverdant-tess.ngrok-free.dev"