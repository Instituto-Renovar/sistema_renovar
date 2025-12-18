import flet as ft
from core.colors import CORES

class Sidebar(ft.Container):
    def __init__(self, on_change_page, selected_index=0, page=None):
        super().__init__()
        self.on_change_page = on_change_page
        self.selected_index = selected_index
        self.page_ref = page 
        
        # Pega dados do usuário logado
        usuario = self.page_ref.session.get("usuario_logado") if self.page_ref else None
        nome_usuario = usuario.get('nome', 'Usuário') if usuario else "Visitante"
        funcao_usuario = usuario.get('funcao', 'Visitante') if usuario else ""
        
        # --- LÓGICA DE PERMISSÕES ---
        # 1. Tenta pegar a lista salva no banco
        permissoes = usuario.get('permissoes', []) if usuario else []
        
        # 2. "CHAVE MESTRA" (Correção do Problema):
        # Se a lista estiver vazia (usuário antigo) MAS ele for Administrador, libera tudo.
        if not permissoes and funcao_usuario == "Administrador":
             permissoes = ["dashboard", "workdesk", "classes", "frequency", "incubator", "settings"]

        self.width = 250
        self.bgcolor = CORES['roxo_brand']
        self.padding = 20
        self.alignment = ft.alignment.top_left
        
        # Definição dos Itens (Texto, Icone, Chave da Permissão)
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
                    ft.Icon(ft.Icons.SPA, color=CORES['ouro'], size=30),
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
            # Só mostra se tiver permissão
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
                    animate=ft.Animation(200, "easeOut"),
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
                        content=ft.Text(nome_usuario[0].upper(), weight="bold"),
                        bgcolor="white10", color="white", radius=18
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