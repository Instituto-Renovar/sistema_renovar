import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from controllers.leads_controller import LeadsController
from controllers.class_controller import ClassController

def DashboardView(page: ft.Page):
    leads_ctrl = LeadsController()
    class_ctrl = ClassController()

    # --- DADOS REAIS ---
    total_leads = len(leads_ctrl.buscar_leads())
    total_matriculados = len(leads_ctrl.buscar_leads(filtro_status="Matriculado"))
    total_incubadora = len(leads_ctrl.buscar_leads(filtro_status="Incubadora"))
    total_atrasados = leads_ctrl.contar_atrasados()

    # --- COMPONENTES ---
    def card_kpi(titulo, valor, cor, icone):
        return ft.Container(
            width=220, height=120, bgcolor="white", border_radius=12, padding=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black"), offset=ft.Offset(0, 4)),
            content=ft.Row([
                ft.Column([
                    ft.Text(titulo, size=12, color="#9CA3AF", weight="bold"),
                    ft.Text(str(valor), size=32, weight="bold", color="#31144A"),
                    ft.Text("+12% este mês", size=11, color="#10B981", weight="bold")
                ], spacing=2),
                ft.Container(content=ft.Icon(icone, color="white", size=24), bgcolor=cor, padding=12, border_radius=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    # Gráfico de Pizza (Simulado com dados reais de contagem)
    # Para simplificar, vamos contar as origens dos leads
    leads = leads_ctrl.buscar_leads()
    origem_counts = {"Instagram": 0, "Google": 0, "Indicação": 0, "Passante": 0}
    for l in leads:
        origem = l.get('origem', 'Passante')
        if origem in origem_counts: origem_counts[origem] += 1
    
    # Seções do Gráfico
    sections = [
        ft.PieChartSection(value=origem_counts["Instagram"] or 1, color="#E1306C", title="", radius=60),
        ft.PieChartSection(value=origem_counts["Google"] or 1, color="#F4B400", title="", radius=60),
        ft.PieChartSection(value=origem_counts["Indicação"] or 1, color="#A0AEC0", title="", radius=60),
        ft.PieChartSection(value=origem_counts.get("Passante", 0) or 1, color="#31144A", title="", radius=60),
    ]

    grafico_origem = ft.Container(
        bgcolor="white", border_radius=12, padding=30, expand=True,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black")),
        content=ft.Row([
            ft.Column([
                ft.Text("Origem dos Leads", size=16, weight="bold", color="#374151"),
                ft.Container(height=20),
                ft.PieChart(sections=sections, sections_space=2, center_space_radius=40, height=200)
            ], expand=True),
            ft.Column([
                ft.Row([ft.Container(width=10, height=10, bgcolor="#E1306C", border_radius=2), ft.Text("Instagram", size=12, color="grey")]),
                ft.Row([ft.Container(width=10, height=10, bgcolor="#F4B400", border_radius=2), ft.Text("Google", size=12, color="grey")]),
                ft.Row([ft.Container(width=10, height=10, bgcolor="#A0AEC0", border_radius=2), ft.Text("Indicação", size=12, color="grey")]),
            ], spacing=10)
        ])
    )

    acoes_rapidas = ft.Container(
        bgcolor="white", border_radius=12, padding=30, width=300,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black")),
        content=ft.Column([
            ft.Text("Ações Rápidas", size=16, weight="bold", color="#374151"),
            ft.Container(height=15),
            ft.ElevatedButton("Novo Cadastro", icon=ft.Icons.ADD, bgcolor="#D97706", color="white", height=45, width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=lambda e: page.go("/workdesk")),
            ft.Container(height=5),
            ft.OutlinedButton("Ver Relatórios", icon=ft.Icons.BAR_CHART, icon_color="#31144A", style=ft.ButtonStyle(color="#31144A", shape=ft.RoundedRectangleBorder(radius=8)), height=45, width=float("inf"))
        ])
    )

    # --- LAYOUT ---
# CÓDIGO NOVO (Colar)
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        
        # Verifica se recebeu um NÚMERO (da Sidebar) ou BOTÃO (do Menu Mobile)
        if isinstance(e, int):
            idx = e
        else:
            idx = e.control.selected_index
            
        page.go(rotas[idx])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=0, page=page)

    content = ft.Row([
        sidebar,
        ft.Container(
            expand=True, bgcolor="#F3F4F6", padding=35,
            content=ft.Column([
                ft.Text("Visão Geral", size=28, weight="bold", color="#31144A", font_family="Jost"),
                ft.Text("Acompanhe os principais indicadores do instituto", size=14, color="#6B7280"),
                ft.Container(height=30),
                ft.Row([
                    card_kpi("Leads Ativos", total_leads, "#3B82F6", ft.Icons.PEOPLE),
                    card_kpi("Alunos Matriculados", total_matriculados, "#10B981", ft.Icons.SCHOOL),
                    card_kpi("Na Incubadora", total_incubadora, "#F59E0B", ft.Icons.HOURGLASS_EMPTY),
                    card_kpi("Atenção / Atrasados", total_atrasados, "#EF4444", ft.Icons.WARNING_AMBER),
                ], spacing=20),
                ft.Container(height=30),
                ft.Row([grafico_origem, ft.Container(width=20), acoes_rapidas], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ], expand=True, spacing=0)

    return ft.View("/dashboard", [content], padding=0, bgcolor=CORES['fundo'])