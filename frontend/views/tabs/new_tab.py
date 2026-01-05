import flet as ft

def get_new_tab():
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ADD_A_PHOTO, size=80, color="#39BFEF"),
                ft.Text("Nova Ocorrência", size=24, weight="bold"),
                ft.ElevatedButton("Reportar Foco", bgcolor="#39BFEF", color="white")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center, expand=True
    )