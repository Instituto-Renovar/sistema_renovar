import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from components.custom_inputs import RenovarTextField, RenovarDropdown
# Controllers
from controllers.course_controller import CourseController
from controllers.user_controller import UserController
from controllers.class_controller import ClassController
from controllers.calendar_controller import CalendarController
from controllers.schedule_controller import ScheduleController
import datetime
from datetime import datetime as dt_module
from datetime import timedelta

def SettingsView(page: ft.Page):
    # --- Controladores ---
    course_ctrl = CourseController()
    user_ctrl = UserController()
    class_ctrl = ClassController()
    calendar_ctrl = CalendarController()
    schedule_ctrl = ScheduleController()

    # --- Helpers Visuais ---
    def campo_label(label, input_control, expand=1):
        return ft.Column([
            ft.Text(label, size=12, weight="bold", color="#111827", font_family="Jost"),
            input_control
        ], spacing=5, expand=expand)

    # =============================================================================================
    # GERADOR E VISUALIZADOR DE CRONOGRAMA
    # =============================================================================================
    def abrir_gerador_cronograma(turma):
        # 1. Busca dados iniciais
        cursos = course_ctrl.buscar_cursos()
        curso_vinculado = next((c for c in cursos if c['nome'] == turma['curso']), None)
        
        if not curso_vinculado or not curso_vinculado.get('plano_ensino'):
            page.snack_bar = ft.SnackBar(ft.Text("Erro: O curso vinculado não tem Grade Curricular configurada!"), bgcolor="red")
            page.snack_bar.open = True; page.update(); return

        # 2. Elementos de UI
        area_conteudo = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
        
        # Botão nasce visível, mas desabilitado (Cinza)
        btn_acao = ft.ElevatedButton("Confirmar e Gerar Aulas", bgcolor="green", color="white", disabled=True)
        
        aulas_geradas_cache = []

        # --- DEFINIÇÃO DO DIÁLOGO ---
        dlg_cronograma = ft.AlertDialog(
            title=ft.Row([
                ft.Text(f"Cronograma: {turma['nome_turma']}", size=20, weight="bold", color="#31144A"),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_cronograma)) # Botão X Adicionado
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            content=ft.Container(width=600, height=600, content=area_conteudo, bgcolor="white"),
            actions=[btn_acao],
            bgcolor="white",
            shape=ft.RoundedRectangleBorder(radius=10)
        )

        # --- FUNÇÕES LÓGICAS ---
        def renderizar_tela_principal(atualizar_modal=True):
            """Decide se mostra o Gerador ou a Lista de Aulas existentes"""
            aulas_existentes = schedule_ctrl.buscar_aulas_por_turma(turma['id'])
            area_conteudo.controls.clear()
            
            if aulas_existentes:
                # MODO VISUALIZAÇÃO
                btn_acao.text = "Excluir Cronograma Inteiro"
                btn_acao.bgcolor = "red"
                btn_acao.color = "white"
                btn_acao.disabled = False # Habilita para excluir
                btn_acao.visible = True
                btn_acao.on_click = confirmar_exclusao_cronograma
                
                area_conteudo.controls.append(ft.Text(f"Cronograma Definido: {len(aulas_existentes)} Aulas", size=16, weight="bold", color="#31144A"))
                area_conteudo.controls.append(ft.Text("Para alterar as datas, exclua o cronograma e gere novamente.", size=12, color="grey"))
                area_conteudo.controls.append(ft.Divider())
                
                for aula in aulas_existentes:
                    try: dt_show = dt_module.strptime(aula['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                    except: dt_show = aula['data']
                    
                    icon = ft.Icons.ASSIGNMENT_LATE if aula.get('is_prova') else ft.Icons.CHECK_CIRCLE_OUTLINE
                    cor = "orange" if aula.get('is_prova') else "blue"
                    
                    area_conteudo.controls.append(
                        ft.Container(
                            padding=10, border=ft.border.all(1, "#E5E7EB"), border_radius=6,
                            content=ft.Row([
                                ft.Row([
                                    ft.Icon(icon, color=cor, size=16),
                                    ft.Text(dt_show, weight="bold", color="#374151"),
                                ]),
                                ft.Text(aula['conteudo'].split(' - ')[0], size=12, color="grey", no_wrap=True, expand=True)
                            ])
                        )
                    )
            else:
                # MODO GERADOR
                btn_acao.text = "Confirmar e Gerar Aulas"
                btn_acao.bgcolor = "green"
                btn_acao.disabled = True # Começa desabilitado até simular
                btn_acao.visible = True
                btn_acao.on_click = salvar_aulas_geradas
                
                dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                global checks_dias 
                checks_dias = [ft.Checkbox(label=dia, value=False) for dia in dias_semana]
                
                col_dias = ft.Column([
                    ft.Text("Selecione os dias de aula:", weight="bold"),
                    ft.Row(checks_dias[:4]), ft.Row(checks_dias[4:])
                ])
                
                btn_simular = ft.ElevatedButton("Simular Datas", bgcolor=CORES['roxo_brand'], color="white", on_click=executar_simulacao)
                
                area_conteudo.controls.extend([
                    ft.Text("O sistema irá distribuir as aulas automaticamente, pulando feriados.", size=12, color="grey"),
                    ft.Divider(),
                    col_dias,
                    ft.Container(height=10),
                    btn_simular,
                    ft.Divider(),
                    ft.Text("Pré-visualização:", weight="bold"),
                    ft.Container(height=20)
                ])
            
            if atualizar_modal:
                # Atualiza botão e conteúdo
                btn_acao.update()
                dlg_cronograma.update()

        def executar_simulacao(e):
            dias_selecionados = [i for i, chk in enumerate(checks_dias) if chk.value]
            if not dias_selecionados:
                page.snack_bar = ft.SnackBar(ft.Text("Selecione pelo menos um dia!"), bgcolor="red"); page.snack_bar.open=True; page.update(); return

            try: data_atual = dt_module.strptime(turma['data_inicio'], "%d/%m/%Y")
            except: page.snack_bar = ft.SnackBar(ft.Text("Data de início inválida!"), bgcolor="red"); page.snack_bar.open=True; page.update(); return

            feriados = [f['data'] for f in calendar_ctrl.buscar_feriados()]
            
            # Limpa preview antigo
            while len(area_conteudo.controls) > 7: area_conteudo.controls.pop()
            
            aulas_geradas_cache.clear()
            plano = curso_vinculado['plano_ensino']
            fila_aulas = []
            for modulo in plano:
                for aula in modulo.get('aulas', []):
                    fila_aulas.append({"modulo": modulo['titulo'], "titulo": aula['titulo'], "conteudo": aula.get('conteudo', ''), "is_prova": aula.get('is_prova', False)})

            idx = 0
            while idx < len(fila_aulas):
                if data_atual.weekday() in dias_selecionados:
                    data_iso = data_atual.strftime("%Y-%m-%d")
                    data_br = data_atual.strftime("%d/%m/%Y")
                    
                    if data_iso in feriados:
                        motivo = calendar_ctrl.verificar_feriado(data_iso) or "Feriado"
                        area_conteudo.controls.append(ft.Text(f"{data_br}: -- PULEI ({motivo}) --", color="red", size=12))
                    else:
                        aula_tpl = fila_aulas[idx]
                        aulas_geradas_cache.append({
                            "turma_id": turma['id'], "data": data_iso, "modulo": aula_tpl['modulo'],
                            "conteudo": f"{aula_tpl['modulo']} - {aula_tpl['titulo']}",
                            "realizada": False, "is_prova": aula_tpl['is_prova']
                        })
                        area_conteudo.controls.append(ft.Row([ft.Text(data_br, weight="bold"), ft.Text(f"{aula_tpl['modulo']} - {aula_tpl['titulo']}", size=12)]))
                        idx += 1
                data_atual += timedelta(days=1)
                if (data_atual - dt_module.strptime(turma['data_inicio'], "%d/%m/%Y")).days > 500: break

            # HABILITA O BOTÃO
            btn_acao.disabled = False
            btn_acao.update()
            
            dlg_cronograma.update()

        def salvar_aulas_geradas(e):
            if not aulas_geradas_cache: return
            for aula in aulas_geradas_cache: schedule_ctrl.criar_aula(aula)
            page.snack_bar = ft.SnackBar(ft.Text("Cronograma criado com sucesso!"), bgcolor="green"); page.snack_bar.open=True; page.update()
            renderizar_tela_principal()

        def confirmar_exclusao_cronograma(e):
            aulas = schedule_ctrl.buscar_aulas_por_turma(turma['id'])
            for aula in aulas: schedule_ctrl.excluir_aula(aula['id'])
            page.snack_bar = ft.SnackBar(ft.Text("Cronograma excluído!"), bgcolor="orange"); page.snack_bar.open=True; page.update()
            renderizar_tela_principal()

        renderizar_tela_principal(atualizar_modal=False)
        page.open(dlg_cronograma)

    # =============================================================================================
    # LÓGICA DO PLANO DE ENSINO (GRADE CURRICULAR - CURSOS)
    # =============================================================================================
    def abrir_gestor_plano_ensino(curso):
        plano_atual = curso.get('plano_ensino', [])
        
        txt_novo_modulo = RenovarTextField("Nome do Novo Módulo (Ex: Tricologia)", expand=True)
        area_conteudo = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        dlg_gestor = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=900, height=700, bgcolor="white", padding=20,
                content=ft.Column([
                    ft.Row([ft.Text(f"Grade: {curso['nome']}", size=20, weight="bold", color=CORES['roxo_brand']), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_gestor))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Container(expand=True), ft.ElevatedButton("Salvar Alterações da Grade", icon=ft.Icons.SAVE, bgcolor="green", color="white", on_click=lambda e: salvar_plano_no_banco())]),
                    ft.Divider(), area_conteudo 
                ])
            )
        )

        def renderizar_plano_principal(atualizar_modal=True):
            area_conteudo.controls.clear()
            
            def adicionar_modulo_inline(e):
                if not txt_novo_modulo.value: return
                plano_atual.append({"titulo": txt_novo_modulo.value, "aulas": []})
                txt_novo_modulo.value = ""; renderizar_plano_principal()
            
            btn_add_modulo = ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color="green", icon_size=40, tooltip="Adicionar Módulo", on_click=adicionar_modulo_inline)
            area_conteudo.controls.append(ft.Container(padding=10, bgcolor="#F3F4F6", border_radius=8, content=ft.Row([txt_novo_modulo, btn_add_modulo])))
            area_conteudo.controls.append(ft.Divider())

            if not plano_atual: area_conteudo.controls.append(ft.Text("Nenhum módulo cadastrado.", color="grey", italic=True))
            
            for i_mod, modulo in enumerate(plano_atual):
                aulas_visual = ft.Column(spacing=5)
                for i_aula, aula in enumerate(modulo.get('aulas', [])):
                    icon_prova = ft.Icon(ft.Icons.ASSIGNMENT_LATE, color="orange", size=16, tooltip="É Prova") if aula.get('is_prova') else ft.Icon(ft.Icons.CIRCLE, size=8, color="grey")
                    aulas_visual.controls.append(ft.Container(bgcolor="white", padding=10, border_radius=6, border=ft.border.all(1, "#E5E7EB"), content=ft.Row([ft.Row([icon_prova, ft.Text(aula['titulo'], size=13, weight="bold"), ft.Text(f"- {aula.get('conteudo','')}...", size=12, color="grey", no_wrap=True, width=150)], spacing=10), ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=16, on_click=lambda e, im=i_mod, ia=i_aula: remover_aula(im, ia))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)))

                card_modulo = ft.Container(bgcolor="white", padding=15, border_radius=8, border=ft.border.all(1, "#D1D5DB"), content=ft.Column([ft.Row([ft.Row([ft.Icon(ft.Icons.FOLDER, color=CORES['roxo_brand']), ft.Text(modulo['titulo'], weight="bold", size=14, color="#374151")]), ft.Row([ft.TextButton("+ Aula", icon=ft.Icons.ADD, on_click=lambda e, x=i_mod: mostrar_formulario_aula(x)), ft.IconButton(ft.Icons.DELETE, tooltip="Remover Módulo", icon_color="red", on_click=lambda e, x=i_mod: remover_modulo(x))])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Divider(height=10, color="transparent"), ft.Container(padding=ft.padding.only(left=20), content=aulas_visual)]))
                area_conteudo.controls.append(card_modulo)
            
            if atualizar_modal: 
                try: dlg_gestor.update()
                except: pass

        def mostrar_formulario_aula(idx_mod):
            area_conteudo.controls.clear()
            txt_titulo_aula = RenovarTextField("Título da Aula (Ex: Aula 01 - Introdução)")
            txt_conteudo = RenovarTextField("Conteúdos / Descrição", multiline=True, height=120)
            chk_prova = ft.Checkbox(label="Esta aula é uma Prova?", active_color="orange")
            
            def confirmar_aula(e):
                if txt_titulo_aula.value:
                    plano_atual[idx_mod]['aulas'].append({"titulo": txt_titulo_aula.value, "conteudo": txt_conteudo.value, "is_prova": chk_prova.value})
                    renderizar_plano_principal()

            def cancelar(e): renderizar_plano_principal() 

            area_conteudo.controls.append(ft.Container(padding=20, content=ft.Column([ft.Text(f"Nova Aula em: {plano_atual[idx_mod]['titulo']}", size=16, weight="bold", color=CORES['roxo_brand']), ft.Divider(), txt_titulo_aula, txt_conteudo, chk_prova, ft.Container(height=20), ft.Row([ft.OutlinedButton("Cancelar", on_click=cancelar), ft.ElevatedButton("Salvar Aula", bgcolor=CORES['ouro'], color="white", on_click=confirmar_aula)], alignment=ft.MainAxisAlignment.END)])))
            dlg_gestor.update()

        def remover_modulo(idx): plano_atual.pop(idx); renderizar_plano_principal()
        def remover_aula(im, ia): plano_atual[im]['aulas'].pop(ia); renderizar_plano_principal()

        def salvar_plano_no_banco():
            course_ctrl.atualizar_curso(curso['id'], {'plano_ensino': plano_atual})
            curso['plano_ensino'] = plano_atual # Atualiza memória local
            page.snack_bar = ft.SnackBar(ft.Text("Grade Salva!"), bgcolor="green"); page.snack_bar.open=True; page.update()

        renderizar_plano_principal(atualizar_modal=False)
        page.open(dlg_gestor)


    # =============================================================================================
    # ABA 1: GERENCIAR CURSOS
    # =============================================================================================
    tabela_cursos = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Carga", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Valor", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, divider_thickness=0
    )

    def carregar_tabela_cursos():
        cursos = course_ctrl.buscar_cursos(apenas_nomes=False)
        tabela_cursos.rows.clear()
        for c in cursos:
            tabela_cursos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c.get('nome', '-'), size=12, weight="bold", color="#1F2937")),
                        ft.DataCell(ft.Text(c.get('carga_horaria', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(f"R$ {c.get('valor', '0,00')}", size=12, color="#4B5563")),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=c['id']: deletar_curso(x))),
                    ],
                    on_select_changed=lambda e, x=c: abrir_modal_curso(x)
                )
            )
        page.update()

    def deletar_curso(id_curso):
        course_ctrl.deletar_curso(id_curso); carregar_tabela_cursos()
        page.snack_bar = ft.SnackBar(ft.Text("Curso removido!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    def abrir_modal_curso(curso=None):
        is_edit = curso is not None
        titulo = "Editar Curso" if is_edit else "Novo Curso"
        
        txt_nome = RenovarTextField("Nome", value=curso.get('nome') if is_edit else "")
        txt_carga = RenovarTextField("Carga (ex: 120h)", value=curso.get('carga_horaria') if is_edit else "")
        txt_valor = RenovarTextField("Valor (ex: 1500,00)", value=curso.get('valor') if is_edit else "")
        
        btn_grade = ft.Container()
        if is_edit:
            btn_grade = ft.OutlinedButton("Configurar Grade Curricular", icon=ft.Icons.LIST_ALT, on_click=lambda e: abrir_gestor_plano_ensino(curso), width=380)

        def salvar(e):
            if not txt_nome.value: return
            dados = {"nome": txt_nome.value, "carga_horaria": txt_carga.value, "valor": txt_valor.value}
            if is_edit: course_ctrl.atualizar_curso(curso['id'], dados)
            else: course_ctrl.criar_curso(dados)
            page.close(dlg_curso); page.snack_bar = ft.SnackBar(ft.Text("Curso Salvo!"), bgcolor="green"); page.snack_bar.open=True; page.update(); carregar_tabela_cursos()

        dlg_curso = ft.AlertDialog(
            title=ft.Row([ft.Text(titulo, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_curso))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=400, content=ft.Column([campo_label("Nome do Curso", txt_nome), ft.Row([campo_label("Carga Horária", txt_carga), campo_label("Valor (R$)", txt_valor)], spacing=15), ft.Divider(), btn_grade], height=220)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg_curso)

    conteudo_cursos = ft.Column([ft.Row([ft.Text("Gerenciar Cursos", size=16, weight="bold", color="#31144A"), ft.Container(expand=True), ft.ElevatedButton("+ Novo Curso", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_curso(None))]), ft.Container(height=10), ft.Container(content=ft.Column([tabela_cursos], scroll=ft.ScrollMode.AUTO), bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"), expand=True)], expand=True)

    # =============================================================================================
    # ABA 2: GERENCIAR TURMAS
    # =============================================================================================
    tabela_turmas = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Curso", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Turma", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Início", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Status", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, divider_thickness=0
    )

    def carregar_tabela_turmas():
        turmas = class_ctrl.buscar_turmas(apenas_ativas=False)
        tabela_turmas.rows.clear()
        
        def sort_key(t):
            status_order = 0 if t.get('status') == 'Aberta' else 1
            try: dt = dt_module.strptime(t.get('data_inicio', ''), "%d/%m/%Y")
            except: dt = dt_module.max
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
                        ft.DataCell(ft.Text(t.get('data_inicio', '-'), size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(status, size=12, weight="bold", color=cor_texto_status)),
                        ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=t['id']: deletar_turma(x))),
                    ],
                    on_select_changed=lambda e, x=t: abrir_modal_turma(x)
                )
            )
        page.update()

    def deletar_turma(id_turma):
        class_ctrl.deletar_turma(id_turma); carregar_tabela_turmas()
        page.snack_bar = ft.SnackBar(ft.Text("Turma removida!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    def abrir_modal_turma(turma=None):
        is_edit = turma is not None
        titulo = "Editar Turma" if is_edit else "Nova Turma"
        
        cursos_nomes = course_ctrl.buscar_cursos(apenas_nomes=True)
        professores_nomes = user_ctrl.buscar_professores_nomes()
        
        dd_curso = RenovarDropdown("Curso", options=cursos_nomes, value=turma.get('curso') if is_edit else None)
        txt_nome = RenovarTextField("Nome da Turma", value=turma.get('nome_turma') if is_edit else "")
        dd_prof = RenovarDropdown("Professor Responsável", options=professores_nomes, value=turma.get('professor') if is_edit else None)
        txt_inicio = RenovarTextField("Data", value=turma.get('data_inicio') if is_edit else "")
        dd_turno = RenovarDropdown("Turno", options=["Manhã", "Tarde", "Noite", "Sábado"], value=turma.get('turno') if is_edit else None)
        dd_status = RenovarDropdown("Status", options=["Aberta", "Encerrada"], value=turma.get('status', 'Aberta') if is_edit else "Aberta")
        txt_cap = RenovarTextField("Vagas (Alunos)", value=turma.get('capacidade', '15') if is_edit else "15")
        txt_aulas = RenovarTextField("Qtd. Aulas (Total)", value=turma.get('total_aulas', '20') if is_edit else "20") 

        btn_cronograma = ft.Container()
        if is_edit:
            btn_cronograma = ft.OutlinedButton(
                "Gerar Cronograma de Aulas", 
                icon=ft.Icons.CALENDAR_MONTH, 
                on_click=lambda e: abrir_gerador_cronograma(turma),
                style=ft.ButtonStyle(color=CORES['roxo_brand'])
            )

        def salvar(e):
            if not dd_curso.value or not txt_nome.value: return
            dados = {
                "curso": dd_curso.value, "nome_turma": txt_nome.value, "professor": dd_prof.value,
                "data_inicio": txt_inicio.value, "turno": dd_turno.value, "status": dd_status.value, 
                "capacidade": txt_cap.value, "total_aulas": txt_aulas.value 
            }
            if is_edit: class_ctrl.atualizar_turma(turma['id'], dados)
            else: class_ctrl.criar_turma(dados)
            page.close(dlg_turma); carregar_tabela_turmas()

        dlg_turma = ft.AlertDialog(
            title=ft.Row([ft.Text(titulo, weight="bold", color="#31144A"), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_turma))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=600, content=ft.Column([
                campo_label("Curso Vinculado", dd_curso),
                campo_label("Identificação da Turma", txt_nome),
                campo_label("Professor Responsável", dd_prof),
                ft.Row([campo_label("Data Início", txt_inicio, 1), campo_label("Turno", dd_turno, 1)], spacing=15),
                ft.Row([campo_label("Máx Alunos", txt_cap, 1), campo_label("Qtd Aulas", txt_aulas, 1), campo_label("Situação", dd_status, 1)], spacing=15),
                ft.Divider(),
                btn_cronograma 
            ], height=420, scroll=ft.ScrollMode.AUTO)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg_turma)

    conteudo_turmas = ft.Column([ft.Row([ft.Text("Gerenciar Turmas", size=16, weight="bold", color="#31144A"), ft.Container(expand=True), ft.ElevatedButton("+ Novo Turma", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_turma(None))]), ft.Container(height=10), ft.Container(content=ft.Column([tabela_turmas], scroll=ft.ScrollMode.AUTO), bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"), expand=True)], expand=True)

    # =============================================================================================
    # ABA 3: GERENCIAR USUÁRIOS
    # =============================================================================================
    tabela_usuarios = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Nome", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Email", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Acessos", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ações", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, column_spacing=20, expand=True, divider_thickness=0
    )

    def carregar_tabela_usuarios():
        usuarios = user_ctrl.buscar_usuarios()
        tabela_usuarios.rows.clear()
        for u in usuarios:
            perms = u.get('permissoes', [])
            texto_perms = f"{len(perms)} áreas" if len(perms) > 0 else "Sem acesso"
            if "settings" in perms: texto_perms = "Admin"
            tabela_usuarios.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Row([ft.CircleAvatar(content=ft.Text(u.get('nome','?')[0], size=10), width=24, height=24, bgcolor=CORES['roxo_brand']), ft.Text(u.get('nome', '-'), size=12, weight="bold", color="#1F2937")], spacing=10)), ft.DataCell(ft.Text(u.get('email', '-'), size=12, color="#4B5563")), ft.DataCell(ft.Container(content=ft.Text(texto_perms, size=10, weight="bold", color="#1E40AF"), bgcolor="#EFF6FF", padding=5, border_radius=4)), ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18, on_click=lambda e, x=u['id']: deletar_usuario(x)))], on_select_changed=lambda e, x=u: abrir_modal_usuario(x)))
        page.update()

    def deletar_usuario(id_user):
        user_ctrl.deletar_usuario(id_user); carregar_tabela_usuarios()
        page.snack_bar = ft.SnackBar(ft.Text("Usuário removido!"), bgcolor="red"); page.snack_bar.open=True; page.update()

    def abrir_modal_usuario(usuario=None):
        is_edit = usuario is not None
        titulo = "Editar Usuário" if is_edit else "Novo Usuário"
        
        txt_nome = RenovarTextField("Nome", value=usuario.get('nome') if is_edit else "")
        txt_email = RenovarTextField("E-mail", value=usuario.get('email') if is_edit else "")
        txt_senha = RenovarTextField("Senha (Opcional na edição)", password=True)
        
        # --- NOVO DROPDOWN DE TIPO DE USUÁRIO ---
        tipo_atual = usuario.get('funcao', 'Colaborador') if is_edit else "Colaborador"
        dd_tipo = RenovarDropdown("Tipo de Conta", options=["Administrador", "Colaborador", "Professor"], value=tipo_atual)

        perms_atuais = usuario.get('permissoes', []) if is_edit else []
        
        checks = {
            "dashboard": ft.Checkbox(label="Dashboard", value="dashboard" in perms_atuais),
            "workdesk": ft.Checkbox(label="Work Desk", value="workdesk" in perms_atuais),
            "classes": ft.Checkbox(label="Turmas", value="classes" in perms_atuais),
            "frequency": ft.Checkbox(label="Frequência", value="frequency" in perms_atuais),
            "incubator": ft.Checkbox(label="Incubadora", value="incubator" in perms_atuais),
            "settings": ft.Checkbox(label="Configurações", value="settings" in perms_atuais)
        }
        
        col_perms = ft.Column([
            ft.Text("Permissões Personalizadas:", weight="bold", size=12),
            ft.Row([checks['dashboard'], checks['workdesk']], spacing=20),
            ft.Row([checks['classes'], checks['frequency']], spacing=20),
            ft.Row([checks['incubator'], checks['settings']], spacing=20)
        ], spacing=10)
        
        def salvar(e):
            if not txt_email.value: return
            
            # Pega as permissões marcadas manualmente
            novas_perms = [key for key, chk in checks.items() if chk.value]
            
            # --- LÓGICA DE PROTEÇÃO POR TIPO ---
            funcao_escolhida = dd_tipo.value
            
            # Se for Professor, garantimos que ele tenha permissão de Turmas, mesmo que esqueça de marcar
            if funcao_escolhida == "Professor":
                if "classes" not in novas_perms: novas_perms.append("classes")
                # Opcional: Remover permissões administrativas se quiser forçar segurança
                # if "settings" in novas_perms: novas_perms.remove("settings")

            # Se for Admin, garante Settings
            if funcao_escolhida == "Administrador":
                if "settings" not in novas_perms: novas_perms.append("settings")

            dados = {
                "nome": txt_nome.value, 
                "email": txt_email.value, 
                "funcao": funcao_escolhida, # Salva se é Professor, Admin ou Colaborador
                "permissoes": novas_perms
            }
            
            if txt_senha.value: dados["senha"] = txt_senha.value
            
            if is_edit: user_ctrl.atualizar_usuario(usuario['id'], dados)
            else: user_ctrl.criar_usuario(dados)
            
            page.close(dlg_user); carregar_tabela_usuarios()

        dlg_user = ft.AlertDialog(
            title=ft.Text(titulo), 
            content=ft.Container(
                width=500, 
                content=ft.Column([
                    campo_label("Nome", txt_nome),
                    campo_label("Email", txt_email),
                    campo_label("Senha", txt_senha),
                    ft.Divider(),
                    campo_label("Função do Usuário", dd_tipo), # Novo Campo
                    ft.Container(height=10),
                    col_perms
                ], height=420) # Aumentei um pouco a altura
            ), 
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar)]
        )
        page.open(dlg_user)

    conteudo_usuarios = ft.Column([ft.Row([ft.Text("Gerenciar Acessos", size=16, weight="bold", color="#31144A"), ft.Container(expand=True), ft.ElevatedButton("+ Novo Usuário", bgcolor=CORES['ouro'], color="white", on_click=lambda e: abrir_modal_usuario(None))]), ft.Container(height=10), ft.Container(content=ft.Column([tabela_usuarios], scroll=ft.ScrollMode.AUTO), bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"), expand=True)], expand=True)

    # =============================================================================================
    # ABA 4: CALENDÁRIO ESCOLAR
    # =============================================================================================
    txt_data_evento = RenovarTextField("Data do Evento", read_only=True, suffix_icon=ft.Icons.CALENDAR_MONTH, expand=1)
    txt_desc_evento = RenovarTextField("Descrição (Ex: Feriado Nacional)", expand=2)
    lista_eventos_visual = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    date_picker = ft.DatePicker(first_date=dt_module(2023, 1, 1), last_date=dt_module(2030, 12, 31), on_change=lambda e: atualizar_input_data(e))
    try: page.overlay.append(date_picker)
    except: pass

    def atualizar_input_data(e):
        if date_picker.value: txt_data_evento.value = date_picker.value.strftime("%d/%m/%Y"); txt_data_evento.data = date_picker.value.strftime("%Y-%m-%d"); txt_data_evento.update()
    txt_data_evento.on_click = lambda e: page.open(date_picker)

    def carregar_lista_eventos():
        eventos = calendar_ctrl.buscar_feriados()
        lista_eventos_visual.controls.clear()
        if not eventos: lista_eventos_visual.controls.append(ft.Text("Nenhum feriado cadastrado.", color="grey", size=13))
        for evt in eventos:
            try: dt_fmt = dt_module.strptime(evt['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except: dt_fmt = evt['data']
            card = ft.Container(bgcolor="white", padding=15, border_radius=8, border=ft.border.all(1, "#E5E7EB"), content=ft.Row([ft.Row([ft.Container(content=ft.Text(dt_fmt.split('/')[0], size=18, weight="bold", color="white"), bgcolor="#EF4444", padding=10, border_radius=8), ft.Column([ft.Text(evt['descricao'], weight="bold", size=15, color="#374151"), ft.Text(f"{dt_fmt} - Suspensão de Aula", size=12, color="grey")], spacing=2)]), ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e, d=evt['data']: deletar_evento(d))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
            lista_eventos_visual.controls.append(card)
        page.update()

    def deletar_evento(data_iso): calendar_ctrl.remover_evento(data_iso); carregar_lista_eventos(); page.snack_bar = ft.SnackBar(ft.Text("Evento removido!"), bgcolor="red"); page.snack_bar.open=True; page.update()
    def salvar_evento(e):
        if not txt_data_evento.value or not txt_desc_evento.value: return
        calendar_ctrl.adicionar_evento(txt_data_evento.data, txt_desc_evento.value); txt_desc_evento.value = ""; txt_data_evento.value = ""; txt_data_evento.data = None; carregar_lista_eventos()
        page.snack_bar = ft.SnackBar(ft.Text("Data Bloqueada!"), bgcolor="green"); page.snack_bar.open=True

    conteudo_calendario = ft.Column([ft.Text("Calendário Escolar", size=16, weight="bold", color="#31144A"), ft.Text("Cadastre feriados e dias de suspensão. O sistema pulará estas datas ao gerar aulas.", size=12, color="grey"), ft.Container(height=10), ft.Row([txt_data_evento, txt_desc_evento, ft.ElevatedButton("Bloquear Data", bgcolor="#EF4444", color="white", height=50, on_click=salvar_evento)], vertical_alignment=ft.CrossAxisAlignment.START), ft.Divider(), ft.Text("Dias Bloqueados", weight="bold", color="#374151", size=14), ft.Container(content=lista_eventos_visual, bgcolor="white", border_radius=10, padding=10, border=ft.border.all(1, "#E5E7EB"), expand=True)], expand=True)

    # =============================================================================================
    # LAYOUT GERAL
    # =============================================================================================
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        idx = e if isinstance(e, int) else e.control.selected_index
        page.go(rotas[idx])

    sidebar = Sidebar(page, selected_index=5)
    tabs = ft.Tabs(selected_index=0, animation_duration=300, indicator_color=CORES['ouro'], label_color=CORES['roxo_brand'], unselected_label_color="grey", tabs=[ft.Tab(text="Cursos", icon=ft.Icons.BOOK, content=ft.Container(content=conteudo_cursos, padding=20)), ft.Tab(text="Turmas", icon=ft.Icons.SCHOOL, content=ft.Container(content=conteudo_turmas, padding=20)), ft.Tab(text="Usuários", icon=ft.Icons.PEOPLE, content=ft.Container(content=conteudo_usuarios, padding=20)), ft.Tab(text="Calendário", icon=ft.Icons.CALENDAR_MONTH, content=ft.Container(content=conteudo_calendario, padding=20))], expand=True)
    content = ft.Row([sidebar, ft.Container(expand=True, bgcolor="#F3F4F6", padding=20, content=ft.Column([ft.Text("Configurações", size=24, weight="bold", color="#31144A"), ft.Container(height=10), tabs], expand=True))], expand=True, spacing=0)

    def inicializar(e=None):
        try: carregar_tabela_cursos(); carregar_tabela_turmas(); carregar_tabela_usuarios(); carregar_lista_eventos()
        except Exception as ex: print(f"Erro init: {ex}")

    view = ft.View(route="/settings", controls=[content], padding=0, bgcolor=CORES['fundo'], scroll=None)
    view.did_mount = inicializar
    
    return view