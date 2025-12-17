import flet as ft
from core.colors import CORES

class Sidebar(ft.Container):
    def __init__(self, on_change_page, selected_index=0):
        super().__init__()
        self.on_change = on_change_page
        self.selected_index = selected_index
        self.width = 250
        self.bgcolor = CORES['roxo_brand']
        self.padding = 20
        
        self.content = ft.Column([
            # 1. Logo
            ft.Row([
                ft.Image(src="logo_renovar.png", width=40, height=40, fit=ft.ImageFit.CONTAIN),
                ft.Column([
                    ft.Text("Instituto", color="white", weight="bold", size=16),
                    ft.Text("Renovar", color=CORES['ouro'], size=12)
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(color="white24", height=30),
            
            # 2. Menu Items
            self.criar_botao_menu("Dashboard", ft.Icons.DASHBOARD_OUTLINED, 0),
            self.criar_botao_menu("Work Desk", ft.Icons.WORK_OUTLINE, 1),
            self.criar_botao_menu("Turmas", ft.Icons.SCHOOL_OUTLINED, 2),
            self.criar_botao_menu("Frequência", ft.Icons.ASSESSMENT_OUTLINED, 3), # <--- NOVO
            self.criar_botao_menu("Incubadora", ft.Icons.HOURGLASS_EMPTY, 4),
            self.criar_botao_menu("Configurações", ft.Icons.SETTINGS_OUTLINED, 5),
            
            ft.Container(expand=True),
            
            # 3. Rodapé
            ft.Row([
                ft.CircleAvatar(bgcolor=CORES['roxo_accent'], content=ft.Text("FR", color="white", size=12)),
                ft.Column([
                    ft.Text("Francisco Renovar", color="white", size=12, weight="bold"),
                    ft.Text("Admin", color="grey", size=10)
                ], spacing=0)
            ])
        ])

    def criar_botao_menu(self, texto, icone, index):
        ativo = (self.selected_index == index)
        cor_icone = CORES['ouro'] if ativo else "white54"
        cor_texto = "white" if ativo else "white54"
        bg_color = CORES['roxo_accent'] if ativo else "transparent"
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, color=cor_icone, size=20),
                ft.Text(texto, color=cor_texto, size=14, weight=ft.FontWeight.W_600)
            ]),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border_radius=10,
            bgcolor=bg_color,
            on_click=lambda e: self.navegar(index),
            ink=True
        )

    def navegar(self, index):
        e = ft.ControlEvent(target=self, name="change", data=str(index), control=self, page=self.page)
        e.control.selected_index = index 
        self.on_change(e)