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
    # --- CONFIGURAÇÃO DE IDIOMA (PT-BR) ---
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("pt", "BR")],
        current_locale=ft.Locale("pt", "BR")
    )
    page.update()

    leads_ctrl = LeadsController()
    course_ctrl = CourseController()
    class_ctrl = ClassController()
    
    leads_cache = []

    # --- Notificações ---
    bolinha_notificacao = ft.Container(
        content=ft.Text("0", size=10, color="white", weight="bold"),
        width=16, height=16, bgcolor="red", border_radius=8, alignment=ft.Alignment(0, 0),
        visible=False
    )

    # --- FUNÇÕES AUXILIARES ---
    def aplicar_mascara_telefone(e):
        valor_sujo = e.control.value
        apenas_digitos = "".join(filter(str.isdigit, valor_sujo))
        tamanho = len(apenas_digitos)
        
        if tamanho == 0:
            e.control.value = ""
            e.control.error_text = None
        elif tamanho == 11:
            e.control.value = f"({apenas_digitos[:2]}) {apenas_digitos[2]} {apenas_digitos[3:7]}-{apenas_digitos[7:]}"
            e.control.error_text = None
        elif tamanho == 10:
            e.control.value = f"({apenas_digitos[:2]}) {apenas_digitos[2:6]}-{apenas_digitos[6:]}"
            e.control.error_text = None
        else:
            e.control.error_text = "Inválido (Use 11 dígitos)"
        e.control.update()

    def formatar_para_tabela(valor):
        if not valor: return "-"
        nums = "".join(filter(str.isdigit, str(valor)))
        if len(nums) == 11:
            return f"({nums[:2]}) {nums[2]} {nums[3:7]}-{nums[7:]}"
        return valor

    def atualizar_notificacoes(inicial=False):
        try:
            qtd_atrasados = leads_ctrl.contar_atrasados()
            if qtd_atrasados > 0:
                bolinha_notificacao.content.value = str(qtd_atrasados)
                bolinha_notificacao.visible = True
            else:
                bolinha_notificacao.visible = False
            if not inicial: bolinha_notificacao.update()
        except Exception as e:
            print(f"Erro ao atualizar notificações: {e}")

    # --- INPUTS DO NOVO LEAD ---
    estilo_input_bar = {
        "bgcolor": "white", "border_color": "#D1D5DB", "border_width": 1,         
        "border_radius": 8, "height": 45, "content_padding": 10,
        "text_size": 13, "hint_style": ft.TextStyle(color="grey", size=13)
    }

    txt_nome_novo = ft.TextField(hint_text="Nome do Lead", expand=3, **estilo_input_bar)
    
    txt_tel_novo = ft.TextField(
        hint_text="Telefone (Zap)",
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9 \-\(\)]", replacement_string=""),
        on_blur=aplicar_mascara_telefone,
        expand=2, 
        **estilo_input_bar
    )
    
    dd_origem_novo = ft.Dropdown(
        hint_text="Fonte / Origem", 
        options=[ft.dropdown.Option("Instagram"), ft.dropdown.Option("Google"), ft.dropdown.Option("Indicação"), ft.dropdown.Option("Passante")], 
        expand=2, bgcolor="white", border_color="#D1D5DB", border_width=1,
        border_radius=8, height=45, content_padding=10, text_size=13,
    )
    
    chk_cab_novo = ft.Checkbox(label="Cabeleireiro(a)?", active_color=CORES['ouro'], label_style=ft.TextStyle(size=12, color="grey"))
    
    def salvar_lead(e):
        if not txt_tel_novo.value: return
        
        telefone_limpo = "".join(filter(str.isdigit, txt_tel_novo.value))
        
        if len(telefone_limpo) != 11:
            page.snack_bar = ft.SnackBar(ft.Text("Erro: Telefone deve ter 11 dígitos (DDD + 9 + Número)."), bgcolor="red")
            page.snack_bar.open = True; page.update(); return 

        for lead in leads_cache:
            lead_tel = "".join(filter(str.isdigit, lead.get('telefone', '')))
            if lead_tel == telefone_limpo:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: O telefone {telefone_limpo} já existe!"), bgcolor="red")
                page.snack_bar.open = True; page.update(); return 
        
        dados = {
            "nome": txt_nome_novo.value, "telefone": telefone_limpo, 
            "origem": dd_origem_novo.value, "is_cabeleireira": chk_cab_novo.value, "status": "Novo"
        }
        leads_ctrl.criar_lead(dados)
        txt_nome_novo.value = ""; txt_tel_novo.value = ""; dd_origem_novo.value = None; chk_cab_novo.value = False
        page.snack_bar = ft.SnackBar(ft.Text("Lead Salvo!"), bgcolor="green"); page.snack_bar.open=True
        carregar_dados()

    btn_salvar_novo = ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar_lead, height=45)

    # --- ELEMENTOS DE FILTRO (NOVA FUNCIONALIDADE) ---
    txt_busca = ft.TextField(
        hint_text="Buscar por Nome ou Telefone", 
        prefix_icon=ft.Icons.SEARCH,
        height=40, text_size=13, content_padding=10,
        border_radius=8, bgcolor="white", border_color="#D1D5DB",
        expand=True
    )

    dd_filtro_status = ft.Dropdown(
        hint_text="Filtrar Status",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Novo"),
            ft.dropdown.Option("Em Contato")        
        ],
        height=40, text_size=13, content_padding=10,
        border_radius=8, bgcolor="white", border_color="#D1D5DB",
        width=200
    )

    def filtrar_tabela(e):
        termo = txt_busca.value.lower() if txt_busca.value else ""
        status_sel = dd_filtro_status.value
        
        lista_filtrada = []
        
        for lead in leads_cache:
            # Filtro de Texto (Nome ou Telefone)
            match_texto = False
            nome = (lead.get('nome') or "").lower()
            tel = (lead.get('telefone') or "")
            if termo in nome or termo in tel:
                match_texto = True
            
            # Filtro de Status
            match_status = False
            st = lead.get('status') or "Novo"
            if not status_sel or status_sel == "Todos" or status_sel == st:
                match_status = True
            
            if match_texto and match_status:
                lista_filtrada.append(lead)
        
        renderizar_dados(lista_filtrada)

    txt_busca.on_change = filtrar_tabela
    dd_filtro_status.on_change = filtrar_tabela

    barra_filtros = ft.Row([txt_busca, dd_filtro_status], spacing=10)

    # --- MODAL DE EDIÇÃO ---
    def abrir_modal_edicao(lead):
        try:
            todos_cursos = course_ctrl.buscar_cursos(apenas_nomes=True) 
            raw_turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
            cursos_com_turmas = list(set([t.get('curso') for t in raw_turmas if t.get('curso')]))
            opcoes_turmas = [f"{t.get('curso')} - {t.get('nome_turma')}" for t in raw_turmas]
        except:
            todos_cursos = []; cursos_com_turmas = []; opcoes_turmas = []

        m_nome = RenovarTextField("Nome Completo", value=lead.get('nome'))

        # --- NOVO CHECKBOX PARA EDIÇÃO ---
        m_chk_cab = ft.Checkbox(
            label="Já é cabeleireira?", 
            value=lead.get('is_cabeleireira', False), # Puxa do banco ou False se não tiver
            active_color=CORES['ouro'],
            label_style=ft.TextStyle(weight="bold", color="#31144A")
        )
        
        m_tel = RenovarTextField(
            "Telefone", 
            value=lead.get('telefone'),
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9 \-\(\)]", replacement_string=""),
            on_blur=aplicar_mascara_telefone
        )
        
        m_origem = RenovarDropdown("Origem", options=["Instagram", "Google", "Indicação", "Passante"], value=lead.get('origem'))
        status_options = ["Novo", "Em Contato", "Matriculado", "Incubadora", "Desistente"]
        m_status = RenovarDropdown("Status Atual", options=status_options, value=lead.get('status') or "Novo")
        
        m_interesse = RenovarDropdown(label="", hint_text="Selecione...", options=todos_cursos, value=lead.get('interesse'), expand=1)
        m_turma = RenovarDropdown(label="", hint_text="Qual a Turma?", options=opcoes_turmas, value=lead.get('turma_vinculada'), visible=False, expand=1)
        m_turno = RenovarDropdown(label="", hint_text="Turno Preferido", options=["Manhã", "Tarde", "Noite"], value=lead.get('turno_interesse'), visible=False, expand=1)
        
        txt_data_visual = RenovarTextField("Data Retorno", value=lead.get('data_retorno') or "", read_only=True, suffix_icon=ft.Icons.CALENDAR_MONTH)
        # CORREÇÃO: Busca a observação do banco
        m_obs = RenovarTextField("Observações", value=lead.get('obs', ''), multiline=True, height=80)

        linha_detalhes = ft.Row([m_interesse, m_turma, m_turno], spacing=15)

        def verificar_status_campos(e=None):
            st = m_status.value
            m_turma.visible = False; m_turno.visible = False
            
            if st == "Matriculado":
                m_interesse.label = "Curso Matriculado"; m_interesse.options = [ft.dropdown.Option(c) for c in cursos_com_turmas]; m_turma.visible = True
            elif st == "Incubadora":
                m_interesse.label = "Curso de Interesse"; m_interesse.options = [ft.dropdown.Option(c) for c in todos_cursos]; m_turno.visible = True
            else:
                m_interesse.label = "Curso de Interesse"; m_interesse.options = [ft.dropdown.Option(c) for c in todos_cursos]
            
            if e is not None: m_interesse.update(); m_turma.update(); m_turno.update(); dlg_modal.update() 

        m_status.on_change = verificar_status_campos
        verificar_status_campos(e=None) 

        def salvar_alteracoes(e):
            st = m_status.value
            dados_upd = {
                "nome": m_nome.value, "telefone": m_tel.value, "origem": m_origem.value,
                "status": m_status.value, "interesse": m_interesse.value,
                "turma_vinculada": m_turma.value if st == "Matriculado" else None,
                "turno_interesse": m_turno.value if st == "Incubadora" else None,
                "data_retorno": txt_data_visual.value if txt_data_visual.value else None,
                "obs": m_obs.value,
                "is_cabeleireira": m_chk_cab.value # <--- ADICIONADO AQUI
            }
            leads_ctrl.atualizar_lead(lead['id'], dados_upd)
            page.close(dlg_modal)
            page.snack_bar = ft.SnackBar(ft.Text("Atualizado!"), bgcolor="green"); page.snack_bar.open = True
            carregar_dados() 

        def deletar_lead(e):
            def confirmar_delete(e):
                leads_ctrl.deletar_lead(lead['id']) 
                page.close(dlg_confirm); page.close(dlg_modal)
                page.snack_bar = ft.SnackBar(ft.Text("Lead excluído!"), bgcolor="red"); page.snack_bar.open = True
                carregar_dados()

            dlg_confirm = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusão"), content=ft.Text("Deseja realmente apagar este lead?"),
                actions=[ft.TextButton("Não", on_click=lambda e: page.close(dlg_confirm)), ft.ElevatedButton("Sim, Excluir", bgcolor="red", color="white", on_click=confirmar_delete)]
            )
            page.open(dlg_confirm)

        date_picker = ft.DatePicker(
            first_date=datetime.datetime(2023, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            cancel_text="Cancelar", confirm_text="Confirmar", error_format_text="Data inválida",
            field_hint_text="DD/MM/AAAA", help_text="Selecione a data"
        )
        time_picker = ft.TimePicker(cancel_text="Cancelar", confirm_text="Confirmar", help_text="Selecione o horário", error_invalid_text="Hora inválida")
        
        page.overlay.append(date_picker); page.overlay.append(time_picker)
        
        def abrir_calendario(e): page.open(date_picker)
        def data_selecionada(e): 
            if date_picker.value: page.open(time_picker) 
        def hora_selecionada(e):
            if date_picker.value and time_picker.value:
                dt_formatada = f"{date_picker.value.strftime('%d/%m/%Y')} {time_picker.value.strftime('%H:%M')}"
                txt_data_visual.value = dt_formatada
                txt_data_visual.update()
        date_picker.on_change = data_selecionada; time_picker.on_change = hora_selecionada; txt_data_visual.on_click = abrir_calendario 

        is_admin_mode = True 
        btn_excluir = ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color="red", tooltip="Excluir Lead", on_click=deletar_lead, visible=is_admin_mode)

        conteudo_modal = ft.Column([
            ft.Row([
                ft.Text("Dados Pessoais", weight="bold", color="#31144A"), 
                m_chk_cab
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            m_nome, ft.Row([m_tel, m_origem], spacing=15),
            ft.Divider(),
            ft.Text("Status e Gestão", weight="bold", color="#31144A"), m_status, linha_detalhes, 
            ft.Container(height=5), txt_data_visual, 
            ft.Divider(), m_obs
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

        dlg_modal = ft.AlertDialog(
            title=ft.Row([ft.Text("Editar Lead", size=18, weight="bold"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_modal))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=550, padding=10, content=conteudo_modal),
            actions=[btn_excluir, ft.Container(expand=True), ft.ElevatedButton("Salvar Alterações", bgcolor=CORES['ouro'], color="white", on_click=salvar_alteracoes)],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.open(dlg_modal)

    # --- TABELAS E LAYOUT GERAL ---
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
        nome_seguro = lead.get('nome') or "?"
        
        return ft.Container(
            bgcolor=bg_card, border_radius=10, padding=15, border=ft.border.all(1, "#E5E7EB"),
            on_click=lambda e: abrir_modal_edicao(lead),
            content=ft.Column([
                ft.Row([
                    ft.CircleAvatar(content=ft.Text(nome_seguro[0], size=12), width=35, height=35, bgcolor=CORES['roxo_brand']),
                    ft.Column([
                        ft.Text(lead.get('nome') or "Sem Nome", weight="bold", size=14, color="#1F2937"), 
                        ft.Text(formatar_para_tabela(lead.get('telefone')), size=12, color="#4B5563")
                    ], spacing=2, expand=True),
                    ft.Container(content=ft.Text(status, size=10, color=cor_status, weight="bold"), bgcolor="white", padding=5, border_radius=5)
                ]),
                ft.Row([ft.Icon(ft.Icons.BOOK, size=14, color="grey"), ft.Text(lead.get('interesse') or "Sem curso", size=12, color="grey", expand=True)]),
            ])
        )

    def renderizar_dados(lista_para_exibir=None):
        # Se não passar lista, usa o cache completo
        if lista_para_exibir is None:
            lista_para_exibir = leads_cache

        tabela_desktop.rows.clear(); lista_mobile.controls.clear()
        
        def parse_sort(x):
            d = x.get('data_retorno')
            if not d: return datetime.datetime.max
            try: return datetime.datetime.strptime(d, "%d/%m/%Y %H:%M")
            except: return datetime.datetime.max
        try: lista_para_exibir.sort(key=parse_sort)
        except: pass

        for lead in lista_para_exibir:
            nome_raw = lead.get('nome') or "Sem Nome"
            primeira_letra = nome_raw[0].upper()
            status = lead.get('status', 'Novo')
            cor_linha = "#EFF6FF" if status == "Novo" else "white"
            cor_texto = "#1E40AF" if status == "Novo" else "#374151"
            weight = ft.FontWeight.BOLD if status == "Novo" else ft.FontWeight.NORMAL
            
            tabela_desktop.rows.append(
                ft.DataRow(color=cor_linha, cells=[
                    ft.DataCell(ft.Row([ft.CircleAvatar(content=ft.Text(primeira_letra, size=11, color="white"), width=32, height=32, bgcolor=CORES['roxo_brand']), ft.Text(nome_raw, size=13, weight="bold", color="#111827")], spacing=12)),
                    ft.DataCell(ft.Text(formatar_para_tabela(lead.get('telefone')), size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('origem') or '-', size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('interesse') or '-', size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(lead.get('data_retorno') or '-', size=13, color="#4B5563")),
                    ft.DataCell(ft.Text(status, size=12, color=cor_texto, weight=weight)),
                ], on_select_changed=lambda e, l=lead: abrir_modal_edicao(l))
            )
            lista_mobile.controls.append(criar_lead_card_mobile(lead))
        page.update()

    def carregar_dados(inicial=False):
        nonlocal leads_cache
        try:
            # Define quais status pertencem ao Work Desk (Funil Ativo)
            status_ativos = ['Novo', 'Em Contato']
            
            # Busca apenas estes no banco. Matriculados e Desistentes são ignorados.
            leads_cache = leads_ctrl.buscar_leads(filtro_status=status_ativos)
            
            renderizar_dados()
            atualizar_notificacoes(inicial)
        except Exception as e:
            print(f"Erro ao carregar dados do workdesk: {e}")

    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        idx = 1
        if isinstance(e, int): idx = e
        elif isinstance(e, ft.ControlEvent) and hasattr(e.control, 'selected_index'): idx = e.control.selected_index
        page.go(rotas[idx])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=1, page=page)
    drawer = ft.NavigationDrawer(on_change=mudar_rota, selected_index=1, controls=[
        ft.Container(height=20), ft.Image(src="logo_renovar.png", width=60, height=60), ft.Divider(thickness=2),
        ft.NavigationDrawerDestination(label="Dashboard", icon=ft.Icons.DASHBOARD_OUTLINED),
        ft.NavigationDrawerDestination(label="Work Desk", icon=ft.Icons.WORK_OUTLINE),
    ])
    app_bar = ft.AppBar(leading=ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(drawer), icon_color="white"), title=ft.Text("Renovar Mobile", color="white"), bgcolor=CORES['roxo_brand'], visible=False)

    topo_desktop = ft.Row([
        ft.Column([ft.Text("Work Desk", size=24, weight="bold", color="#31144A"), ft.Text("Gestão de leads", size=13, color="grey")]),
        ft.Container(expand=True),
        ft.Stack([ft.IconButton(ft.Icons.NOTIFICATIONS, icon_color="grey"), ft.Container(content=bolinha_notificacao, top=5, right=5)])
    ])

    def criar_inputs_desktop():
        return ft.Row([txt_nome_novo, txt_tel_novo, dd_origem_novo, ft.Row([chk_cab_novo, btn_salvar_novo], spacing=10)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.START)

    def criar_inputs_mobile():
        return ft.Column([txt_nome_novo, txt_tel_novo, ft.Row([dd_origem_novo, ft.Container(expand=True), chk_cab_novo]), btn_salvar_novo], spacing=10)

    card_novo_lead_content = ft.Container(content=criar_inputs_desktop()) 
    card_novo_lead_container = ft.Container(bgcolor="white", border_radius=12, padding=20, content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.PERSON_ADD, color=CORES['ouro']), ft.Text("Novo Lead", weight="bold", size=16)]),
        ft.Container(height=10), card_novo_lead_content
    ]))
    container_conteudo = ft.Container(expand=True)
    
    layout_principal = ft.Row([sidebar, ft.Container(expand=True, bgcolor="#F3F4F6", padding=10, content=ft.Column([
        ft.Container(content=topo_desktop, visible=True, ref=ft.Ref()), ft.Container(height=10),
        card_novo_lead_container,
        ft.Container(height=10),
        barra_filtros, # ADICIONADO: Barra de busca e filtro
        ft.Container(height=10),
        container_conteudo
    ], scroll=ft.ScrollMode.AUTO))], expand=True, spacing=0)

    def ajustar_layout(e):
        is_mobile = page.width < 850
        if is_mobile:
            sidebar.visible = False; app_bar.visible = True; layout_principal.controls[1].content.controls[0].visible = False 
            container_conteudo.content = lista_mobile; card_novo_lead_content.content = criar_inputs_mobile()
        else:
            sidebar.visible = True; app_bar.visible = False; layout_principal.controls[1].content.controls[0].visible = True
            container_conteudo.content = ft.Column([tabela_desktop], scroll=ft.ScrollMode.AUTO); card_novo_lead_content.content = criar_inputs_desktop()
        page.update()

    page.on_resized = ajustar_layout
    carregar_dados(inicial=True)
    ajustar_layout(None)

    return ft.View(route="/workdesk", controls=[app_bar, layout_principal], padding=0, bgcolor=CORES['fundo'], drawer=drawer, scroll=None)