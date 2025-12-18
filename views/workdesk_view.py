import flet as ft
from core.colors import CORES
from core.utils import formatar_telefone
from components.sidebar import Sidebar
from components.custom_inputs import RenovarTextField, RenovarDropdown
# Controllers
from controllers.leads_controller import LeadsController
from controllers.course_controller import CourseController
from controllers.class_controller import ClassController
import datetime

def WorkDeskView(page: ft.Page):
    leads_ctrl = LeadsController()
    course_ctrl = CourseController()
    class_ctrl = ClassController()
    
    leads_cache = []

    # --- Elementos de Notificação ---
    bolinha_notificacao = ft.Container(
        content=ft.Text("0", size=10, color="white", weight="bold"),
        width=16, height=16, bgcolor="red", border_radius=8, alignment=ft.alignment.center,
        visible=False
    )

    def atualizar_notificacoes(inicial=False):
        qtd_atrasados = leads_ctrl.contar_atrasados()
        if qtd_atrasados > 0:
            bolinha_notificacao.content.value = str(qtd_atrasados)
            bolinha_notificacao.visible = True
        else:
            bolinha_notificacao.visible = False
        if not inicial: bolinha_notificacao.update()

    # --- INPUTS DO NOVO LEAD ---
    txt_nome_novo = RenovarTextField("Nome completo")
    txt_tel_novo = RenovarTextField("Telefone", on_change=formatar_telefone)
    dd_origem_novo = RenovarDropdown("Origem", options=["Instagram", "Google", "Indicação", "Passante"], width=150)
    chk_cab_novo = ft.Checkbox(label="Já é cabeleireiro(a)?", active_color=CORES['ouro'], label_style=ft.TextStyle(size=12, color="grey"))
    
    def salvar_lead(e):
        if not txt_tel_novo.value: return
        dados = {
            "nome": txt_nome_novo.value, "telefone": txt_tel_novo.value, 
            "origem": dd_origem_novo.value, "is_cabeleireira": chk_cab_novo.value, "status": "Novo"
        }
        leads_ctrl.criar_lead(dados)
        txt_nome_novo.value = ""; txt_tel_novo.value = ""; dd_origem_novo.value = None; chk_cab_novo.value = False
        page.snack_bar = ft.SnackBar(ft.Text("Lead Salvo!"), bgcolor="green"); page.snack_bar.open=True
        carregar_dados()

    btn_salvar_novo = ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar_lead)

    # --- MODAL DE EDIÇÃO ---
    def abrir_modal_edicao(lead):
        lista_cursos = course_ctrl.buscar_cursos(apenas_nomes=True) 
        raw_turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
        opcoes_turmas = [f"{t.get('curso')} - {t.get('nome_turma')}" for t in raw_turmas]

        m_nome = RenovarTextField("Nome", value=lead.get('nome'))
        m_tel = RenovarTextField("Telefone", value=lead.get('telefone'), on_change=formatar_telefone)
        m_origem = RenovarDropdown("Origem", options=["Instagram", "Google", "Indicação", "Passante"], value=lead.get('origem'))
        status_options = ["Novo", "Em Contato", "Matriculado", "Incubadora", "Desistente"]
        m_status = RenovarDropdown("Status", options=status_options, value=lead.get('status') or "Novo")
        m_interesse = RenovarDropdown("Curso de Interesse", options=lista_cursos, value=lead.get('interesse'))
        m_turma = RenovarDropdown("Selecionar Turma", options=opcoes_turmas, value=lead.get('turma_vinculada'), visible=False)
        m_turno = RenovarDropdown("Turno Preferido", options=["Manhã", "Tarde", "Noite"], value=lead.get('turno_interesse'), visible=False)
        txt_data_visual = RenovarTextField("Data e Hora", value=lead.get('data_retorno') or "", read_only=True, suffix_icon=ft.Icons.CALENDAR_TODAY)
        m_obs = RenovarTextField("Observações", value="", multiline=True, height=80)

        def verificar_status_campos(e=None):
            st = m_status.value
            m_turma.visible = (st == "Matriculado")
            m_turno.visible = (st == "Incubadora" or st == "Em Espera")
            if e is not None: dlg_modal.update()

        m_status.on_change = verificar_status_campos
        verificar_status_campos(e=None)

        def salvar_alteracoes(e):
            st = m_status.value
            dados_upd = {
                "nome": m_nome.value, "telefone": m_tel.value, "origem": m_origem.value,
                "status": m_status.value, "interesse": m_interesse.value,
                "turma_vinculada": m_turma.value if st == "Matriculado" else None,
                "turno_interesse": m_turno.value if st in ["Incubadora", "Em Espera"] else None,
                "data_retorno": txt_data_visual.value if txt_data_visual.value else None
            }
            leads_ctrl.atualizar_lead(lead['id'], dados_upd)
            page.close(dlg_modal)
            page.snack_bar = ft.SnackBar(ft.Text("Atualizado!"), bgcolor="green"); page.snack_bar.open = True
            carregar_dados() 

        date_picker = ft.DatePicker(cancel_text="Cancelar", confirm_text="OK")
        time_picker = ft.TimePicker(confirm_text="Confirmar", help_text="Horário")
        page.overlay.append(date_picker); page.overlay.append(time_picker)
        
        def abrir_calendario(e): page.open(date_picker)
        def data_sel(e): 
            if date_picker.value: page.open(time_picker)
        def hora_sel(e):
            if date_picker.value and time_picker.value:
                txt_data_visual.value = f"{date_picker.value.strftime('%d/%m/%Y')} {time_picker.value.strftime('%H:%M')}"
                txt_data_visual.update()
        date_picker.on_change = data_sel; time_picker.on_change = hora_sel; txt_data_visual.on_click = abrir_calendario

        dlg_modal = ft.AlertDialog(
            title=ft.Row([ft.Text("Editar Lead", size=18, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_modal))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=600, padding=10, content=ft.Column([
                ft.Text("Dados do Lead", weight="bold"), m_nome, m_tel, m_origem, 
                ft.Divider(), ft.Text("Status e Interesse", weight="bold"), m_status, m_interesse, m_turma, m_turno, txt_data_visual,
                ft.Divider(), m_obs
            ], spacing=10, scroll=ft.ScrollMode.AUTO)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar_alteracoes)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.open(dlg_modal)

    # --- COMPONENTES RESPONSIVOS ---
    tabela_desktop = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Telefone", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Origem", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Curso", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Retorno", size=12, color="#6B7280", weight="bold")),
            ft.DataColumn(ft.Text("Status", size=12, color="#6B7280", weight="bold")),
        ],
        rows=[], heading_row_height=40, data_row_min_height=55, column_spacing=20, divider_thickness=0,
    )

    lista_mobile = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)

    def criar_lead_card_mobile(lead):
        status = lead.get('status', 'Novo')
        cor_status = "#1E40AF" if status == "Novo" else "#374151"
        bg_card = "#EFF6FF" if status == "Novo" else "white"
        return ft.Container(
            bgcolor=bg_card, border_radius=10, padding=15, border=ft.border.all(1, "#E5E7EB"),
            on_click=lambda e: abrir_modal_edicao(lead),
            content=ft.Column([
                ft.Row([
                    ft.CircleAvatar(content=ft.Text(lead.get('nome','?')[0], size=12), width=35, height=35, bgcolor=CORES['roxo_brand']),
                    ft.Column([
                        ft.Text(lead.get('nome'), weight="bold", size=14, color="#1F2937", overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(lead.get('telefone'), size=12, color="#4B5563")
                    ], spacing=2, expand=True),
                    ft.Container(content=ft.Text(status, size=10, color=cor_status, weight="bold"), bgcolor="white", padding=5, border_radius=5)
                ]),
                ft.Divider(height=10, color="transparent"),
                ft.Row([ft.Icon(ft.Icons.BOOK, size=14, color="grey"), ft.Text(lead.get('interesse') or "Sem curso", size=12, color="grey", expand=True)]),
                ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, size=14, color="grey"), ft.Text(lead.get('data_retorno') or "-", size=12, color="grey")])
            ])
        )

    def renderizar_dados():
        tabela_desktop.rows.clear(); lista_mobile.controls.clear()
        
        def parse_sort(x):
            d = x.get('data_retorno')
            if not d: return datetime.datetime.max
            try: return datetime.datetime.strptime(d, "%d/%m/%Y %H:%M")
            except: return datetime.datetime.max
        leads_cache.sort(key=parse_sort)

        for lead in leads_cache:
            status = lead.get('status', 'Novo')
            cor_linha = "#EFF6FF" if status == "Novo" else "white"
            cor_texto = "#1E40AF" if status == "Novo" else "#374151"
            weight = ft.FontWeight.BOLD if status == "Novo" else ft.FontWeight.NORMAL
            
            tabela_desktop.rows.append(
                ft.DataRow(color=cor_linha, cells=[
                    ft.DataCell(ft.Row([ft.CircleAvatar(content=ft.Text(lead.get('nome','?')[0], size=11, color="white"), width=32, height=32, bgcolor=CORES['roxo_brand']), ft.Text(lead.get('nome'), size=13, weight="bold", color="#111827")], spacing=12)),
                    ft.DataCell(ft.Text(lead.get('telefone',''), size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('origem','-'), size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('interesse','-'), size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('data_retorno','-'), size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(status, size=12, color=cor_texto, weight=weight)),
                ], on_select_changed=lambda e, l=lead: abrir_modal_edicao(l))
            )
            lista_mobile.controls.append(criar_lead_card_mobile(lead))
        page.update()

    def carregar_dados(inicial=False):
        nonlocal leads_cache
        leads_cache = leads_ctrl.buscar_leads(filtro_status=['Novo', 'Em Negociação', 'Em Contato', 'Interessado'])
        renderizar_dados()
        atualizar_notificacoes(inicial)

    # --- LÓGICA DE NAVEGAÇÃO SEGURA (CORREÇÃO DO ERRO) ---
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        
        # Lógica inteligente para descobrir o índice
        idx = 1
        if isinstance(e, int):
            idx = e
        elif isinstance(e, ft.ControlEvent):
            if hasattr(e.control, 'selected_index'):
                idx = e.control.selected_index
        
        page.go(rotas[idx])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=1, page=page)
    
    # CORREÇÃO AQUI: on_change chama a função direto, sem lambda complicado
    drawer = ft.NavigationDrawer(
        on_change=mudar_rota,
        selected_index=1,
        controls=[
            ft.Container(height=20),
            ft.Image(src="logo_renovar.png", width=60, height=60),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(label="Dashboard", icon=ft.Icons.DASHBOARD_OUTLINED),
            ft.NavigationDrawerDestination(label="Work Desk", icon=ft.Icons.WORK_OUTLINE),
            ft.NavigationDrawerDestination(label="Turmas", icon=ft.Icons.SCHOOL_OUTLINED),
            ft.NavigationDrawerDestination(label="Frequência", icon=ft.Icons.ASSESSMENT_OUTLINED),
            ft.NavigationDrawerDestination(label="Incubadora", icon=ft.Icons.HOURGLASS_EMPTY),
            ft.NavigationDrawerDestination(label="Configurações", icon=ft.Icons.SETTINGS_OUTLINED),
        ],
    )

    app_bar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(drawer), icon_color="white"),
        title=ft.Text("Renovar Mobile", size=16, weight="bold", color="white"),
        bgcolor=CORES['roxo_brand'],
        visible=False
    )

    topo_desktop = ft.Row([
        ft.Column([ft.Text("Work Desk", size=24, weight="bold", color="#31144A"), ft.Text("Gestão de leads", size=13, color="grey")]),
        ft.Container(expand=True),
        ft.Stack([ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color="grey"), ft.Container(content=bolinha_notificacao, top=5, right=5)])
    ])

    # Inputs Responsivos
    def criar_inputs_desktop():
        return ft.Row([txt_nome_novo, txt_tel_novo, dd_origem_novo, chk_cab_novo, btn_salvar_novo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def criar_inputs_mobile():
        return ft.Column([txt_nome_novo, txt_tel_novo, ft.Row([dd_origem_novo, ft.Container(expand=True), chk_cab_novo]), btn_salvar_novo], spacing=10)

    card_novo_lead_content = ft.Container(content=criar_inputs_desktop()) # Começa desktop
    
    card_novo_lead_container = ft.Container(
        bgcolor="white", border_radius=12, padding=20,
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PERSON_ADD, color=CORES['ouro']), ft.Text("Novo Lead", weight="bold", size=16)]),
            ft.Container(height=10),
            card_novo_lead_content
        ])
    )

    container_conteudo = ft.Container(expand=True)
    
    layout_principal = ft.Row([
        sidebar, 
        ft.Container(
            expand=True, bgcolor="#F3F4F6", padding=10,
            content=ft.Column([
                ft.Container(content=topo_desktop, visible=True, ref=ft.Ref()),
                ft.Container(height=10),
                card_novo_lead_container,
                ft.Container(height=10),
                container_conteudo
            ], scroll=ft.ScrollMode.AUTO)
        )
    ], expand=True, spacing=0)

    def ajustar_layout(e):
        is_mobile = page.width < 850
        if is_mobile:
            sidebar.visible = False
            app_bar.visible = True
            layout_principal.controls[1].content.controls[0].visible = False # Esconde topo desktop
            container_conteudo.content = lista_mobile
            card_novo_lead_content.content = criar_inputs_mobile()
        else:
            sidebar.visible = True
            app_bar.visible = False
            layout_principal.controls[1].content.controls[0].visible = True
            container_conteudo.content = ft.Column([tabela_desktop], scroll=ft.ScrollMode.AUTO)
            card_novo_lead_content.content = criar_inputs_desktop()
        page.update()

    page.on_resized = ajustar_layout
    carregar_dados(inicial=True)
    ajustar_layout(None)

    return ft.View("/workdesk", [app_bar, layout_principal], padding=0, bgcolor=CORES['fundo'], drawer=drawer)