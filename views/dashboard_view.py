import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from controllers.leads_controller import LeadsController
from controllers.class_controller import ClassController

# --- CACHE GLOBAL PARA O DASHBOARD ---
# Guarda os dados para não baixar de novo se o usuário só trocou de aba
dashboard_cache = {
    "dados": None,
    "timestamp": 0
}

def DashboardView(page: ft.Page):
    leads_ctrl = LeadsController()
    class_ctrl = ClassController()

    # --- DADOS REAIS (COM CACHE) ---
    todos_leads = []
    
    try:
        # Se já temos dados no cache, usamos eles!
        if dashboard_cache["dados"] is not None:
            print("⚡ Usando cache do Dashboard (0 leituras)")
            todos_leads = dashboard_cache["dados"]
        else:
            print("🌐 Baixando dados para o Dashboard...")
            # Aqui ainda baixamos tudo, pois precisamos contar origens e status variados
            # Futuramente, podemos migrar para um documento de estatísticas dedicado
            todos_leads = leads_ctrl.buscar_leads()
            dashboard_cache["dados"] = todos_leads # Salva no cache
        
        total_leads = len(todos_leads)
        
        # Processamento em Memória (Rápido e Grátis)
        total_matriculados = 0
        total_incubadora = 0
        for l in todos_leads:
            st = l.get('status')
            if st == 'Matriculado': total_matriculados += 1
            if st == 'Incubadora': total_incubadora += 1
            
        # Atrasados já é otimizado no controller (só busca ativos)
        # Mas para economizar mais, podemos contar na memória se já baixamos tudo
        # Como baixamos "todos_leads" acima (que inclui tudo), podemos contar aqui mesmo!
        # Isso economiza a chamada do contar_atrasados() que iria no banco de novo.
        
        import datetime
        agora = datetime.datetime.now()
        total_atrasados = 0
        
        for l in todos_leads:
            # Lógica de atraso replicada em memória
            st = l.get('status')
            if st in ['Novo', 'Em Contato']: # Só conta ativos
                data_str = l.get('data_retorno')
                if data_str:
                    try:
                        d = datetime.datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                        if d < agora: total_atrasados += 1
                    except: pass

    except Exception as e:
        print(f"Erro ao carregar KPIs: {e}")
        total_leads = 0; total_matriculados = 0; total_incubadora = 0; total_atrasados = 0
        todos_leads = []

    # --- COMPONENTES VISUAIS ---
    def card_kpi(titulo, valor, cor, icone):
        return ft.Container(
            width=220, height=120, bgcolor="white", border_radius=12, padding=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black"), offset=ft.Offset(0, 4)),
            content=ft.Row([
                ft.Column([
                    ft.Text(titulo, size=12, color="#9CA3AF", weight="bold"),
                    ft.Text(str(valor), size=32, weight="bold", color="#31144A"),
                    ft.Text("Cache Ativo", size=11, color="#10B981", weight="bold")
                ], spacing=2),
                ft.Container(content=ft.Icon(icone, color="white", size=24), bgcolor=cor, padding=12, border_radius=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    # --- CONTAGEM DE ORIGEM ---
    origem_counts = {"Instagram": 0, "Google": 0, "Indicação": 0, "Passante": 0}
    for l in todos_leads:
        origem = l.get('origem', 'Passante')
        if origem in origem_counts: 
            origem_counts[origem] += 1
        else:
            origem_counts[origem] = 1

    def item_origem(nome, qtd, total, cor):
        porcentagem = (qtd / total) if total > 0 else 0
        return ft.Column([
            ft.Row([ft.Text(nome, size=12, weight="bold"), ft.Text(f"{qtd}", size=12)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=porcentagem, color=cor, bgcolor="#F3F4F6", height=8, border_radius=4)
        ], spacing=5)

    grafico_origem = ft.Container(
        bgcolor="white", border_radius=12, padding=30, expand=True,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black")),
        content=ft.Column([
            ft.Text("Origem dos Leads", size=16, weight="bold", color="#374151"),
            ft.Container(height=20),
            item_origem("Instagram", origem_counts.get("Instagram", 0), total_leads, "#E1306C"),
            item_origem("Google", origem_counts.get("Google", 0), total_leads, "#F4B400"),
            item_origem("Indicação", origem_counts.get("Indicação", 0), total_leads, "#A0AEC0"),
            item_origem("Passante/Outros", origem_counts.get("Passante", 0), total_leads, "#31144A"),
        ], spacing=15)
    )

    acoes_rapidas = ft.Container(
        bgcolor="white", border_radius=12, padding=30, width=300,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.06, "black")),
        content=ft.Column([
            ft.Text("Ações Rápidas", size=16, weight="bold", color="#374151"),
            ft.Container(height=15),
            ft.ElevatedButton("Novo Cadastro", icon=ft.Icons.ADD, bgcolor="#D97706", color="white", height=45, width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=lambda e: page.go("/workdesk")),
            ft.Container(height=5),
            
            # Botão para Atualizar Cache Manualmente
            ft.OutlinedButton("Atualizar Dados", icon=ft.Icons.REFRESH, icon_color="#31144A", 
                              style=ft.ButtonStyle(color="#31144A", shape=ft.RoundedRectangleBorder(radius=8)), 
                              height=45, width=float("inf"),
                              on_click=lambda e: atualizar_dados_manual(e))
        ])
    )

    def atualizar_dados_manual(e):
        dashboard_cache["dados"] = None # Limpa cache
        page.go("/dashboard") # Recarrega

    # --- NAVEGAÇÃO ---
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        if isinstance(e, int): idx = e
        else: idx = e.control.selected_index
        page.go(rotas[idx])

    sidebar = Sidebar(page, selected_index=0)

    # --- MONTAGEM DA TELA ---
    content = ft.Row([
        sidebar,
        ft.Container(
            expand=True, bgcolor="#F3F4F6", padding=35,
            content=ft.Column([
                ft.Text("Visão Geral", size=28, weight="bold", color="#31144A", font_family="Jost"),
                ft.Text("Acompanhe os principais indicadores do instituto", size=14, color="#6B7280"),
                ft.Container(height=30),
                # Linha de KPIs
                ft.Row([
                    card_kpi("Leads Ativos", total_leads, "#3B82F6", ft.Icons.PEOPLE),
                    card_kpi("Matriculados", total_matriculados, "#10B981", ft.Icons.SCHOOL),
                    card_kpi("Incubadora", total_incubadora, "#F59E0B", ft.Icons.HOURGLASS_EMPTY),
                    card_kpi("Atrasados", total_atrasados, "#EF4444", ft.Icons.WARNING_AMBER),
                ], spacing=20, scroll=ft.ScrollMode.ALWAYS),
                ft.Container(height=30),
                # Linha inferior
                ft.Row([grafico_origem, ft.Container(width=20), acoes_rapidas], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
            ], scroll=ft.ScrollMode.AUTO)
        )
    ], expand=True, spacing=0)

    return ft.View(
        route="/dashboard", 
        controls=[content], 
        padding=0, 
        bgcolor=CORES['fundo'],
        scroll=None 
    )