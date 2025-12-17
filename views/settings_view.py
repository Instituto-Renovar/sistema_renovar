import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from components.custom_inputs import RenovarTextField, RenovarDropdown
# Controllers
from controllers.course_controller import CourseController
from controllers.user_controller import UserController
from controllers.class_controller import ClassController
import datetime

def SettingsView(page: ft.Page):
    course_ctrl = CourseController()
    user_ctrl = UserController()
    class_ctrl = ClassController()

    # --- HELPER: Label Externo ---
    def campo_label(label, input_control, expand=1):
        return ft.Column([
            ft.Text(label, size=12, weight="bold", color="#111827", font_family="Jost"),
            input_control
        ], spacing=5, expand=expand)

    # --- HELPER: Badge de Status ---
    def StatusBadgeConfig(texto, cor_fundo="#DCFCE7", cor_texto="#166534"):
        return ft.Container(
            content=ft.Text(texto, size=10, weight="bold", color=cor_texto),
            bgcolor=cor_fundo, padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=4, alignment=ft.alignment.center
        )

    # =============================================================================================
    # ABA 1: GERENCIAR CURSOS
    # =============================================================================================
    tabela_cursos = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Carga Horária", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Valor", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Status", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, show_checkbox_column=False, divider_thickness=0
    )

    def abrir_modal_curso(curso=None):
        is_edit = curso is not None
        titulo = "Editar Curso" if is_edit else "Novo Curso"
        
        txt_nome = RenovarTextField("Nome", value=curso.get('nome') if is_edit else "")
        txt_carga = RenovarTextField("Carga (ex: 120h)", value=curso.get('carga_horaria') if is_edit else "")
        txt_valor = RenovarTextField("Valor (ex: 1500,00)", value=curso.get('valor') if is_edit else "")
        
        def salvar(e):
            if not txt_nome.value: return
            dados = {"nome": txt_nome.value, "carga_horaria": txt_carga.value, "valor": txt_valor.value}
            
            if is_edit:
                course_ctrl.atualizar_curso(curso['id'], dados)
                msg = "Curso atualizado!"
            else:
                course_ctrl.criar_curso(dados)
                msg = "Curso criado!"
                
            page.close(dlg_curso)
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green"); page.snack_bar.open=True; page.update()
            carregar_tabela_cursos()

        dlg_curso = ft.AlertDialog(
            title=ft.Row([ft.Text(titulo, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_curso))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=400, content=ft.Column([
                campo_label("Nome do Curso", txt_nome),
                ft.Row([campo_label("Carga Horária", txt_carga), campo_label("Valor (R$)", txt_valor)], spacing=15)
            ], height=150)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg_curso)

    def carregar_tabela_cursos():
        cursos = course_ctrl.buscar_cursos(apenas_nomes=False)
        tabela_cursos.rows.clear()
        for c in cursos:
            cor_linha = "white"
            tabela_cursos.rows.append(
                ft.DataRow(
                    color=cor_linha,
                    cells=[
                        ft.DataCell(ft.Text(c.get('nome', '-'), size=12, weight="bold", color="#1F2937")),
                        ft.DataCell(ft.Text(c.get('carga_horaria', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(f"R$ {c.get('valor', '0,00')}", size=12, color="#4B5563")),
                        ft.DataCell(ft.Text("Ativo", size=12, weight="bold", color="#059669")),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=c['id']: deletar_curso(x))),
                    ],
                    on_select_changed=lambda e, x=c: abrir_modal_curso(x)
                )
            )
        page.update()

    def deletar_curso(id_curso):
        course_ctrl.deletar_curso(id_curso)
        carregar_tabela_cursos()
        page.snack_bar = ft.SnackBar(ft.Text("Curso removido!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    conteudo_cursos = ft.Column([
        ft.Row([
            ft.Text("Gerenciar Cursos", size=16, weight="bold", color="#31144A"),
            ft.Container(expand=True),
            ft.ElevatedButton("+ Novo Curso", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_curso(None))
        ]),
        ft.Container(height=10),
        ft.Container(
            content=ft.Column([tabela_cursos], scroll=ft.ScrollMode.AUTO), 
            bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB")
        )
    ])

    # =============================================================================================
    # ABA 2: GERENCIAR TURMAS
    # =============================================================================================
    tabela_turmas = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Curso", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Turma", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Professor", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Início", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Turno", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Vagas", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Aulas", weight="bold", size=12, color="#6B7280")), # Coluna Nova
            ft.DataColumn(ft.Text("Status", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, show_checkbox_column=False, divider_thickness=0
    )

    def abrir_modal_turma(turma=None):
        is_edit = turma is not None
        titulo = "Editar Turma" if is_edit else "Nova Turma"
        
        # Buscas auxiliares
        cursos_nomes = course_ctrl.buscar_cursos(apenas_nomes=True)
        professores_nomes = user_ctrl.buscar_professores_nomes()
        
        dd_curso = RenovarDropdown("Curso", options=cursos_nomes, value=turma.get('curso') if is_edit else None)
        txt_nome = RenovarTextField("Nome da Turma", value=turma.get('nome_turma') if is_edit else "")
        dd_prof = RenovarDropdown("Professor Responsável", options=professores_nomes, value=turma.get('professor') if is_edit else None)
        txt_inicio = RenovarTextField("Data", value=turma.get('data_inicio') if is_edit else "")
        dd_turno = RenovarDropdown("Turno", options=["Manhã", "Tarde", "Noite", "Sábado"], value=turma.get('turno') if is_edit else None)
        dd_status = RenovarDropdown("Status", options=["Aberta", "Encerrada"], value=turma.get('status', 'Aberta') if is_edit else "Aberta")
        
        # Campos Numéricos
        txt_cap = RenovarTextField("Vagas (Alunos)", value=turma.get('capacidade', '15') if is_edit else "15")
        txt_aulas = RenovarTextField("Qtd. Aulas (Total)", value=turma.get('total_aulas', '20') if is_edit else "20") # <--- NOVO CAMPO

        def salvar(e):
            if not dd_curso.value or not txt_nome.value: return
            dados = {
                "curso": dd_curso.value, "nome_turma": txt_nome.value, 
                "professor": dd_prof.value,
                "data_inicio": txt_inicio.value, "turno": dd_turno.value, 
                "status": dd_status.value, "capacidade": txt_cap.value,
                "total_aulas": txt_aulas.value # Salvando o total de aulas
            }
            if is_edit:
                class_ctrl.atualizar_turma(turma['id'], dados)
            else:
                class_ctrl.criar_turma(dados)
            
            page.close(dlg_turma); carregar_tabela_turmas()

        dlg_turma = ft.AlertDialog(
            title=ft.Row([ft.Text(titulo, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_turma))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=600, content=ft.Column([
                campo_label("Curso Vinculado", dd_curso),
                campo_label("Identificação da Turma", txt_nome),
                campo_label("Professor Responsável", dd_prof),
                ft.Row([
                    campo_label("Data Início", txt_inicio, 1), 
                    campo_label("Turno", dd_turno, 1),
                ], spacing=15),
                ft.Row([
                    campo_label("Máx Alunos", txt_cap, 1),
                    campo_label("Qtd Aulas", txt_aulas, 1), # <--- NOVO
                    campo_label("Situação", dd_status, 1)
                ], spacing=15),
            ], height=380, scroll=ft.ScrollMode.AUTO)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg_turma)

    def carregar_tabela_turmas():
        turmas = class_ctrl.buscar_turmas(apenas_ativas=False)
        tabela_turmas.rows.clear()
        
        def sort_key(t):
            status_order = 0 if t.get('status') == 'Aberta' else 1
            try: dt = datetime.datetime.strptime(t.get('data_inicio', ''), "%d/%m/%Y")
            except: dt = datetime.datetime.max
            return (status_order, dt)

        turmas.sort(key=sort_key)

        for t in turmas:
            status = t.get('status', 'Aberta')
            cor_linha = "#F0FDF4" if status == "Aberta" else "#F3F4F6"
            cor_texto_status = "#166534" if status == "Aberta" else "#9CA3AF"

            tabela_turmas.rows.append(
                ft.DataRow(
                    color=cor_linha,
                    cells=[
                        ft.DataCell(ft.Text(t.get('curso', '-'), size=12, weight="bold", color="#1F2937")),
                        ft.DataCell(ft.Text(t.get('nome_turma', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(t.get('professor', 'N/D'), size=12, color="#1F2937", weight="bold")),
                        ft.DataCell(ft.Text(t.get('data_inicio', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(t.get('turno', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(t.get('capacidade', '15'), size=12, color="#4B5563", weight="bold")),
                        ft.DataCell(ft.Text(t.get('total_aulas', '-'), size=12, color="#4B5563")), # Mostra total de aulas
                        ft.DataCell(ft.Text(status, size=12, weight="bold", color=cor_texto_status)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=t['id']: deletar_turma(x))),
                    ],
                    on_select_changed=lambda e, x=t: abrir_modal_turma(x)
                )
            )
        page.update()

    def deletar_turma(id_turma):
        class_ctrl.deletar_turma(id_turma)
        carregar_tabela_turmas()
        page.snack_bar = ft.SnackBar(ft.Text("Turma removida!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    conteudo_turmas = ft.Column([
        ft.Row([
            ft.Text("Gerenciar Turmas", size=16, weight="bold", color="#31144A"),
            ft.Container(expand=True),
            ft.ElevatedButton("+ Nova Turma", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_turma(None))
        ]),
        ft.Container(height=10),
        ft.Container(content=ft.Column([tabela_turmas], scroll=ft.ScrollMode.AUTO), bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"))
    ])

    # =============================================================================================
    # ABA 3: GERENCIAR USUÁRIOS
    # =============================================================================================
    tabela_usuarios = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Email", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Função", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Permissões", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, show_checkbox_column=False, divider_thickness=0
    )

    def abrir_modal_usuario(usuario=None):
        is_edit = usuario is not None
        titulo = "Editar Usuário" if is_edit else "Novo Usuário"
        
        txt_nome = RenovarTextField("Nome", value=usuario.get('nome') if is_edit else "")
        txt_email = RenovarTextField("E-mail", value=usuario.get('email') if is_edit else "")
        txt_senha = RenovarTextField("Senha", password=True)
        dd_funcao = RenovarDropdown("Função", options=["Administrador", "Colaborador", "Professor"], value=usuario.get('funcao') if is_edit else None)
        
        def salvar(e):
            if not txt_email.value or not dd_funcao.value: return
            dados = {"nome": txt_nome.value, "email": txt_email.value, "funcao": dd_funcao.value}
            if txt_senha.value: dados["senha"] = txt_senha.value
            
            if is_edit: user_ctrl.atualizar_usuario(usuario['id'], dados)
            else: user_ctrl.criar_usuario(dados)
            
            page.close(dlg_user); carregar_tabela_usuarios()

        dlg_user = ft.AlertDialog(
            title=ft.Row([ft.Text(titulo, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_user))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=400, content=ft.Column([
                campo_label("Nome Completo", txt_nome),
                campo_label("E-mail de Acesso", txt_email),
                campo_label("Senha (Opcional na edição)", txt_senha),
                campo_label("Nível de Acesso", dd_funcao)
            ], height=300)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg_user)

    def carregar_tabela_usuarios():
        usuarios = user_ctrl.buscar_usuarios()
        tabela_usuarios.rows.clear()
        for u in usuarios:
            funcao = u.get('funcao', 'Colaborador')
            cor_linha = "#FFFBEB" if funcao == "Administrador" else ("#EFF6FF" if funcao == "Professor" else "white")
            permissao_txt = "Acesso Total" if funcao == "Administrador" else ("Acesso Aluno" if funcao == "Professor" else "Acesso Vendas")

            tabela_usuarios.rows.append(
                ft.DataRow(
                    color=cor_linha,
                    cells=[
                        ft.DataCell(ft.Row([
                            ft.CircleAvatar(content=ft.Text(u.get('nome','?')[0], size=10), width=24, height=24, bgcolor=CORES['roxo_brand']),
                            ft.Text(u.get('nome', '-'), size=12, weight="bold", color="#1F2937")
                        ], spacing=10)),
                        ft.DataCell(ft.Text(u.get('email', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(funcao, size=12, weight="bold", color="#374151")),
                        ft.DataCell(ft.Text(permissao_txt, size=12, color="grey")),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=u['id']: deletar_usuario(x))),
                    ],
                    on_select_changed=lambda e, x=u: abrir_modal_usuario(x)
                )
            )
        page.update()

    def deletar_usuario(id_user):
        user_ctrl.deletar_usuario(id_user)
        carregar_tabela_usuarios()
        page.snack_bar = ft.SnackBar(ft.Text("Usuário removido!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    conteudo_usuarios = ft.Column([
        ft.Row([
            ft.Text("Gerenciar Usuários", size=16, weight="bold", color="#31144A"),
            ft.Container(expand=True),
            ft.ElevatedButton("+ Novo Usuário", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_usuario(None))
        ]),
        ft.Container(height=10),
        ft.Container(content=ft.Column([tabela_usuarios], scroll=ft.ScrollMode.AUTO), bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"))
    ])

    # =============================================================================================
    # LAYOUT GERAL
    # =============================================================================================
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        page.go(rotas[e.control.selected_index])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=5)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=CORES['ouro'],
        label_color=CORES['roxo_brand'],
        unselected_label_color="grey",
        tabs=[
            ft.Tab(text="Cursos", icon=ft.Icons.BOOK, content=ft.Container(content=conteudo_cursos, padding=20)),
            ft.Tab(text="Turmas", icon=ft.Icons.SCHOOL, content=ft.Container(content=conteudo_turmas, padding=20)),
            ft.Tab(text="Usuários", icon=ft.Icons.PEOPLE, content=ft.Container(content=conteudo_usuarios, padding=20)),
        ],
        expand=True,
    )

    content = ft.Row([
        sidebar,
        ft.Container(
            expand=True, bgcolor="#F3F4F6", padding=20,
            content=ft.Column([
                ft.Text("Configurações", size=24, weight="bold", color="#31144A"),
                ft.Container(height=10),
                tabs
            ])
        )
    ], expand=True, spacing=0)

    carregar_tabela_cursos()
    carregar_tabela_turmas()
    carregar_tabela_usuarios()

    return ft.View("/settings", [content], padding=0, bgcolor=CORES['fundo'])