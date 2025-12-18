import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from components.custom_inputs import RenovarDropdown
from controllers.leads_controller import LeadsController
from controllers.course_controller import CourseController

def IncubatorView(page: ft.Page):
    leads_ctrl = LeadsController()
    course_ctrl = CourseController()
    
    leads_cache = []

    # --- Elementos do Topo ---
    opcoes_cursos = course_ctrl.buscar_cursos(apenas_nomes=True)
    opcoes_cursos.insert(0, "Todos")

    dd_filtro_curso = RenovarDropdown("Filtrar por Interesse", options=opcoes_cursos, width=300, value="Todos")

    # --- TABELA ---
    tabela = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Telefone", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Interesse (Curso)", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Turno", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Data Retorno", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Ação", size=12, color="#6B7280", weight="bold")),
        ],
        rows=[], heading_row_height=40, data_row_min_height=55, column_spacing=20, expand=True, divider_thickness=0,
    )

    def reativar_lead(lead):
        leads_ctrl.atualizar_lead(lead['id'], {'status': 'Novo'})
        page.snack_bar = ft.SnackBar(content=ft.Text(f"{lead.get('nome')} reativado!"), bgcolor="green"); page.snack_bar.open = True; page.update(); carregar_dados()

    def renderizar_tabela(lista):
        tabela.rows.clear()
        if not lista: page.update(); return

        for lead in lista:
            txt_data = lead.get('data_retorno', '-').split(" ")[0]
            tabela.rows.append(
                ft.DataRow(
                    color="#FEF2F2",
                    cells=[
                        ft.DataCell(ft.Row([ft.CircleAvatar(content=ft.Text(lead.get('nome','?')[0].upper(), size=11, color="white"), width=32, height=32, bgcolor="#EF4444"), ft.Text(lead.get('nome', 'Sem Nome'), size=13, weight="bold", color="#111827")], spacing=12)),
                        ft.DataCell(ft.Text(lead.get('telefone', ''), size=13, color="#4B5563")),
                        ft.DataCell(ft.Text(lead.get('interesse', '-'), size=13, weight="bold", color="#374151")),
                        ft.DataCell(ft.Container(content=ft.Text(lead.get('turno_interesse', '-'), size=11, color="#9A3412"), bgcolor="#FFEDD5", padding=5, border_radius=4)),
                        ft.DataCell(ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, size=14, color="grey"), ft.Text(txt_data, size=13, color="#4B5563")], spacing=5)),
                        ft.DataCell(ft.ElevatedButton("Reativar", icon=ft.Icons.RESTORE, color="white", bgcolor=CORES['ouro'], height=30, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=lambda e, l=lead: reativar_lead(l))),
                    ]
                )
            )
        page.update()

    def aplicar_filtro(e):
        curso = dd_filtro_curso.value
        if not curso or curso == "Todos": renderizar_tabela(leads_cache)
        else: renderizar_tabela([l for l in leads_cache if l.get('interesse') == curso])

    dd_filtro_curso.on_change = aplicar_filtro

    def carregar_dados():
        nonlocal leads_cache
        leads_cache = leads_ctrl.buscar_leads(filtro_status=['Incubadora', 'Em Espera'])
        leads_cache.sort(key=lambda x: x.get('data_retorno') or "9999")
        aplicar_filtro(None)

# CÓDIGO NOVO (Colar)
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        
        # Verifica se recebeu um NÚMERO (da Sidebar) ou BOTÃO (do Menu Mobile)
        if isinstance(e, int):
            idx = e
        else:
            idx = e.control.selected_index
            
        page.go(rotas[idx])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=4, page=page)

    topo = ft.Row([
        ft.Column([ft.Text("Incubadora de Leads", size=24, weight="bold", color="#31144A"), ft.Text("Gerencie contatos frios", size=13, color="#6B7280")]),
        ft.Container(expand=True),
        ft.Container(content=ft.Row([ft.Icon(ft.Icons.FILTER_LIST, color=CORES['roxo_brand']), dd_filtro_curso], spacing=10), bgcolor="white", padding=10, border_radius=10, border=ft.border.all(1, "#E5E7EB"))
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    content = ft.Row([sidebar, ft.Container(expand=True, bgcolor="#F3F4F6", padding=35, content=ft.Column([topo, ft.Container(height=20), ft.Container(bgcolor="white", border_radius=12, padding=25, expand=True, content=ft.Column([ft.Text("Lista de Espera", size=15, weight="bold", color="#1F2937"), ft.Divider(color="#F3F4F6"), ft.Column([tabela], scroll=ft.ScrollMode.AUTO, expand=True)]))]))], expand=True, spacing=0)

    carregar_dados()
    return ft.View("/incubator", [content], padding=0, bgcolor=CORES['fundo'])