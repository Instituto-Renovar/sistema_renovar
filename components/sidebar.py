import flet as ft
from core.colors import CORES

class Sidebar(ft.Container):
    def __init__(self, on_change_page, selected_index=0, page=None):
        super().__init__()
        self.on_change_page = on_change_page
        self.selected_index = selected_index
        self.page_ref = page 
        
        # --- CORREÇÃO DE LEITURA (A única mudança técnica) ---
        # Buscamos direto da sessão onde o Login salvou
        nome_usuario = "Visitante"
        permissoes = []
        funcao_usuario = ""

        if self.page_ref:
            nome_usuario = self.page_ref.session.get("user_name") or "Visitante"
            permissoes = self.page_ref.session.get("user_perms") or []
            
            # Define o cargo visualmente
            if "settings" in permissoes:
                funcao_usuario = "Administrador"
                # Se é admin, forçamos a lista completa de permissões para liberar tudo
                permissoes = ["dashboard", "workdesk", "classes", "frequency", "incubator", "settings"]
            elif nome_usuario != "Visitante":
                funcao_usuario = "Colaborador"

        # --- DAQUI PARA BAIXO É 100% SEU DESIGN ORIGINAL ---
        self.width = 250
        self.bgcolor = CORES['roxo_brand']
        self.padding = 20
        
        # Definição dos Itens
        todos_itens = [
            ("Dashboard", ft.Icons.DASHBOARD, "dashboard"),
            ("Work Desk", ft.Icons.WORK_OUTLINE, "workdesk"),
            ("Turmas", ft.Icons.SCHOOL, "classes"),
            ("Frequência", ft.Icons.ASSESSMENT_OUTLINED, "frequency"),
            ("Incubadora", ft.Icons.HOURGLASS_EMPTY, "incubator"),
            ("Configurações", ft.Icons.SETTINGS, "settings"),
        ]

        self.content = ft.Column(expand=True)
        
        # Logo
        self.content.controls.append(
            ft.Column([
                ft.Row([
                    ft.Image(src="logo_renovar_branca.png", width=40, height=40, fit=ft.ImageFit.CONTAIN),
                    ft.Column([
                        ft.Text("Instituto", color="white", weight="bold", size=16),
                        ft.Text("Renovar", color=CORES['ouro'], size=12)
                    ], spacing=0)
                ]),
                ft.Divider(color="white24", height=30),
            ])
        )

        # Gera os botões dinamicamente
        for i, (texto, icone, chave) in enumerate(todos_itens):
            # Só mostra se tiver permissão (ou se for admin liberado acima)
            if chave in permissoes:
                is_selected = (i == self.selected_index)
                
                btn = ft.Container(
                    content=ft.Row([
                        ft.Icon(icone, color=CORES['ouro'] if is_selected else "white70"),
                        ft.Text(texto, color="white" if is_selected else "white70", weight="bold" if is_selected else "normal")
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    border_radius=10,
                    bgcolor="white10" if is_selected else "transparent",
                    on_click=lambda e, idx=i: self.on_change_page(idx),
                    ink=True
                )
                self.content.controls.append(btn)

        # Espaçador
        self.content.controls.append(ft.Container(expand=True))

        # Rodapé com Nome
        self.content.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.CircleAvatar(
                        content=ft.Text(nome_usuario[0].upper(), weight="bold", color=CORES['roxo_brand']),
                        bgcolor=CORES['ouro'], 
                        radius=18
                    ),
                    ft.Column([
                        ft.Text(nome_usuario, color="white", weight="bold", size=12, width=120, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(funcao_usuario, color="white54", size=10)
                    ], spacing=0, expand=True),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color="white54", tooltip="Sair", on_click=self.logout)
                ]),
                padding=ft.padding.only(top=10),
                border=ft.border.only(top=ft.BorderSide(1, "white12"))
            )
        )

    def logout(self, e):
        if self.page_ref:
            self.page_ref.session.clear()
            self.page_ref.go("/")