import flet as ft

def get_explore_tab():
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.EXPLORE, size=80, color="#39BFEF"),
                ft.Text("Explorar", size=24, weight="bold"),
                ft.Text("Mapa e estatísticas aqui", color="grey"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center, expand=True
    )