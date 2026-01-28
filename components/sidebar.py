import flet as ft
from core.colors import CORES

class Sidebar(ft.Container):
    # Mudança Principal: 'page' agora é o primeiro argumento e é obrigatório.
    # Removemos 'on_change_page' pois o Sidebar agora sabe navegar sozinho.
    def __init__(self, page: ft.Page, selected_index=0):
        super().__init__()
        self.page_ref = page 
        self.selected_index = selected_index
        
        # --- LÓGICA DE SESSÃO (BLINDADA) ---
        # Como page é obrigatório, isso aqui nunca vai falhar
        nome_usuario = self.page_ref.session.get("user_name") or "Visitante"
        permissoes = self.page_ref.session.get("user_perms") or []
        funcao_usuario = "Visitante"

        # Define o cargo visualmente
        if "settings" in permissoes:
            funcao_usuario = "Administrador"
            # Admin vê tudo
            permissoes = ["dashboard", "workdesk", "classes", "frequency", "incubator", "settings"]
        elif nome_usuario != "Visitante":
            funcao_usuario = "Colaborador"

        # --- DESIGN ---
        self.width = 250
        self.bgcolor = CORES['roxo_brand']
        self.padding = 20
        
        # Definição dos Itens e suas ROTAS
        # Agora mapeamos: (Nome, Ícone, Permissão, Rota)
        todos_itens = [
            ("Dashboard", ft.Icons.DASHBOARD, "dashboard", "/dashboard"),
            ("Work Desk", ft.Icons.WORK_OUTLINE, "workdesk", "/workdesk"), # Verifique se sua rota é /workdesk ou /
            ("Turmas", ft.Icons.SCHOOL, "classes", "/classes"),
            ("Frequência", ft.Icons.ASSESSMENT_OUTLINED, "frequency", "/frequency"),
            ("Incubadora", ft.Icons.HOURGLASS_EMPTY, "incubator", "/incubator"),
            ("Configurações", ft.Icons.SETTINGS, "settings", "/settings"),
        ]

        self.content = ft.Column(expand=True)
        
        # Logo
        self.content.controls.append(
            ft.Column([
                ft.Row([
                    ft.Image(src="assets/logo_renovar_branca.png", width=40, height=40, fit=ft.ImageFit.CONTAIN), # Ajustei src para assets/ se necessário
                    ft.Column([
                        ft.Text("Instituto", color="white", weight="bold", size=16),
                        ft.Text("Renovar", color=CORES['ouro'], size=12)
                    ], spacing=0)
                ]),
                ft.Divider(color="white24", height=30),
            ])
        )

        # Gera os botões dinamicamente
        for i, (texto, icone, chave, rota) in enumerate(todos_itens):
            # Só mostra se tiver permissão
            if chave in permissoes:
                is_selected = (i == self.selected_index)
                
                # Botão com navegação embutida
                btn = ft.Container(
                    content=ft.Row([
                        ft.Icon(icone, color=CORES['ouro'] if is_selected else "white70"),
                        ft.Text(texto, color="white" if is_selected else "white70", weight="bold" if is_selected else "normal")
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    border_radius=10,
                    bgcolor="white10" if is_selected else "transparent",
                    # AQUI ESTÁ A MÁGICA: Navega direto pela rota
                    on_click=lambda e, r=rota: self.page_ref.go(r),
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
        self.page_ref.session.clear()
        self.page_ref.go("/")