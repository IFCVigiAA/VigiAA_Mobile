import flet as ft
from views.tabs.home_tab import get_home_tab
from views.tabs.new_tab import get_new_tab
from views.tabs.explore_tab import get_explore_tab
from views.tabs.profile_tab import get_profile_tab

def create_main_view(page: ft.Page):
    
    saved_tab_index = page.client_storage.get("selected_tab_index")
    initial_index = saved_tab_index if saved_tab_index is not None else 0
    page.client_storage.remove("selected_tab_index")

    # --- HEADER ATUALIZADO (SEM O NÚMERO 2) ---
    def get_custom_header():
        return ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=["#39BFEF", "#65F4A6"] 
            ),
            padding=ft.padding.only(left=20, right=20, top=40, bottom=20),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Image(
                        src="logo-sem-fundo.png", 
                        height=40, 
                        fit=ft.ImageFit.CONTAIN
                    ),
    
                    ft.Text(
                        "VigiAA", 
                        size=22, 
                        weight="bold", 
                        color="#1a1a1a",
                        font_family="Roboto"
                    ),
                    
                    # Apenas o ícone limpo agora
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_OUTLINED, 
                        icon_color="black",
                        icon_size=28,
                        on_click=lambda _: print("Notificações")
                    )
                ]
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, "black"),
                offset=ft.Offset(0, 2),
            )
        )

    view_home = get_home_tab(page)
    view_add = get_new_tab()
    view_explore = get_explore_tab()
    view_profile = get_profile_tab(page) 

    my_tabs = [view_home, view_add, view_explore, view_profile]
    body_component = ft.Container(content=my_tabs[initial_index], expand=True)

    def change_tab(e):
        index = e.control.selected_index
        body_component.content = my_tabs[index]
        body_component.update()

    return ft.View(
        route="/",
        controls=[
            get_custom_header(),
            body_component,
            
            ft.NavigationBar(
                bgcolor="#39BFEF", 
                indicator_color=ft.Colors.TRANSPARENT,
                selected_index=initial_index,
                on_change=change_tab,
                label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_HIDE,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label=""),
                    ft.NavigationBarDestination(icon=ft.Icons.ADD_BOX_OUTLINED, selected_icon=ft.Icons.ADD_BOX, label=""),
                    ft.NavigationBarDestination(icon=ft.Icons.EXPLORE_OUTLINED, selected_icon=ft.Icons.EXPLORE, label=""),
                    ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label=""),
                ]
            )
        ],
        padding=0,
        bgcolor="#F5F5F5"
    )