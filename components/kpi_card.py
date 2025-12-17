import flet as ft
from core.colors import CORES

class KPICard(ft.Container):
    def __init__(self, titulo, valor, icone, cor_fundo_icone, variacao=None):
        super().__init__()
        # Estilo do Card (Idêntico à imagem)
        self.expand = True
        self.bgcolor = CORES['surface'] # Branco
        self.border_radius = 12
        self.padding = 20
        self.shadow = ft.BoxShadow(
            blur_radius=15, 
            color=ft.Colors.with_opacity(0.08, "black"),
            offset=ft.Offset(0, 4)
        )
        
        # Conteúdo
        self.content = ft.Row([
            # Lado Esquerdo: Textos
            ft.Column([
                ft.Text(titulo, size=12, color="grey", weight="bold"),
                ft.Text(str(valor), size=28, weight="bold", color=CORES['texto']),
                # Variação (ex: +12% vs mês anterior)
                ft.Text(variacao, size=10, color="green" if "+" in str(variacao) else "red") if variacao else ft.Container()
            ], spacing=2, expand=True),
            
            # Lado Direito: Ícone com fundo quadrado arredondado
            ft.Container(
                content=ft.Icon(icone, color="white", size=24),
                bgcolor=cor_fundo_icone,
                width=45, height=45,
                border_radius=12,
                alignment=ft.alignment.center
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)