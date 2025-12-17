import flet as ft
from core.colors import CORES
from components.custom_inputs import RenovarTextField
from controllers.class_controller import ClassController
import datetime

def TeacherView(page: ft.Page):
    class_ctrl = ClassController()
    
    usuario_logado = page.session.get("usuario_logado")
    nome_professor = usuario_logado.get('nome', 'Professor') if usuario_logado else "Professor"
    
    alunos_presentes = set()

    date_picker = ft.DatePicker(cancel_text="Cancelar", confirm_text="OK")
    page.overlay.clear()
    page.overlay.append(date_picker)

    # --- Botão de Presença ---
    def criar_botao_presenca(aluno):
        id_aluno = aluno['id']
        alunos_presentes.add(id_aluno)
        
        def alternar_presenca(e):
            container = e.control
            icone = container.content
            
            if id_aluno in alunos_presentes:
                alunos_presentes.remove(id_aluno)
                container.bgcolor = "#FEE2E2" # Vermelho claro
                icone.name = ft.Icons.CLOSE
                icone.color = "#EF4444" # Vermelho forte
            else:
                alunos_presentes.add(id_aluno)
                container.bgcolor = "#D1FAE5" # Verde claro
                icone.name = ft.Icons.CHECK
                icone.color = "#059669" # Verde forte
            
            container.update()

        return ft.Container(
            content=ft.Icon(ft.Icons.CHECK, color="#059669", size=20),
            bgcolor="#D1FAE5", 
            width=45, height=45, # Um pouco maior para facilitar o toque
            border_radius=25, 
            alignment=ft.alignment.center,
            on_click=alternar_presenca,
            animate=ft.Animation(150, "easeOut")
        )

    # --- Modal de Chamada ---
    def abrir_chamada(turma):
        nome_turma_completo = f"{turma.get('curso')} - {turma.get('nome_turma')}"
        alunos = class_ctrl.buscar_alunos_da_turma(nome_turma_completo)
        alunos_presentes.clear()
        
        txt_data = RenovarTextField("Data da Aula", value=datetime.date.today().strftime("%d/%m/%Y"), read_only=True, suffix_icon=ft.Icons.CALENDAR_TODAY)
        txt_conteudo = RenovarTextField("Conteúdo Ministrado", multiline=True, height=100)
        
        lista_chamada = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350) # Altura maior para a lista
        
        if not alunos:
            lista_chamada.controls.append(ft.Text("Nenhum aluno nesta turma.", color="grey"))
        
        for aluno in alunos:
            alunos_presentes.add(aluno['id'])
            
            # Layout da Linha do Aluno (SEM AVATAR, ESPAÇO TOTAL)
            linha = ft.Container(
                bgcolor="white", 
                padding=ft.padding.symmetric(horizontal=15, vertical=10), 
                border_radius=12, 
                border=ft.border.all(1, "#E5E7EB"),
                content=ft.Row([
                    # Nome do aluno com expansão total e sem quebra forçada
                    ft.Text(
                        aluno.get('nome'), 
                        weight="bold", 
                        size=15, # Fonte um pouco maior
                        expand=True, 
                        color="#374151", 
                        no_wrap=False # Permite quebrar linha se o nome for gigante
                    ),
                    
                    # Botão de Check na direita
                    criar_botao_presenca(aluno)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            )
            lista_chamada.controls.append(linha)

        def salvar_chamada(e):
            if not txt_conteudo.value:
                page.snack_bar = ft.SnackBar(ft.Text("Preencha o conteúdo da aula!"), bgcolor="red"); page.snack_bar.open=True; page.update(); return
            
            e.control.text = "Salvando..."
            e.control.disabled = True
            e.control.update()

            dados = {
                "turma_id": turma['id'],
                "nome_turma": nome_turma_completo,
                "data": txt_data.value,
                "conteudo": txt_conteudo.value,
                "presentes": list(alunos_presentes),
                "total_alunos": len(alunos),
                "professor": nome_professor
            }
            
            sucesso, msg = class_ctrl.salvar_chamada(dados)
            
            if sucesso:
                page.close(dlg_chamada)
                page.snack_bar = ft.SnackBar(ft.Text("Chamada salva com sucesso!"), bgcolor="green")
            else:
                e.control.text = "Salvar Chamada"
                e.control.disabled = False
                e.control.update()
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar: {msg}"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        def abrir_cal(e): page.open(date_picker)
        def data_sel(e):
            if date_picker.value: txt_data.value = date_picker.value.strftime("%d/%m/%Y"); txt_data.update()
        date_picker.on_change = data_sel; txt_data.on_click = abrir_cal

        total_previsto = turma.get('total_aulas', 'N/D')
        
        # DEFINIÇÃO DO MODAL MAXIMIZADO
        dlg_chamada = ft.AlertDialog(
            title=ft.Row([
                ft.Text("Registro de Aula", weight="bold", color="#31144A", size=18),
                ft.Container(
                    content=ft.Text(f"Meta: {total_previsto}", size=12, color="white", weight="bold"),
                    bgcolor=CORES['roxo_accent'], padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=6
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Inset padding controla a margem externa. 10 é bem pouco, quase cola na borda.
            inset_padding=ft.padding.symmetric(horizontal=10, vertical=20),
            content_padding=15, # Padding interno confortável
            
            content=ft.Container(
                width=page.width, # Tenta pegar toda a largura disponível dentro do inset
                content=ft.Column([
                    ft.Text(nome_turma_completo, size=13, color="grey"),
                    ft.Divider(),
                    txt_data,
                    ft.Text("Toque para marcar falta", weight="bold", size=12, color="grey"),
                    ft.Container(content=lista_chamada, bgcolor="#F9FAFB", border_radius=10, padding=5),
                    txt_conteudo
                ], spacing=15, scroll=ft.ScrollMode.AUTO)
            ),
            actions=[
                ft.ElevatedButton("Cancelar", color="grey", bgcolor="white", on_click=lambda e: page.close(dlg_chamada)),
                ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar_chamada)
            ],
            bgcolor="white", 
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.open(dlg_chamada)

    # --- GRID e Layout ---
    grid_aulas = ft.GridView(expand=True, runs_count=3, max_extent=350, child_aspect_ratio=1.3, spacing=20, run_spacing=20)

    def carregar_turmas():
        if nome_professor and nome_professor != "Professor":
            turmas = class_ctrl.buscar_turmas_do_professor(nome_professor)
        else:
            turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
        
        cards = []
        if not turmas:
            grid_aulas.controls = [ft.Text("Nenhuma turma encontrada para você.", size=16, color="grey")]
            page.update()
            return

        for t in turmas:
            nome_turma_formatada = f"{t.get('curso')} - {t.get('nome_turma')}"
            qtd = class_ctrl.contar_alunos(nome_turma_formatada)
            
            card = ft.Container(
                bgcolor="white", border_radius=12, padding=20,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black"), offset=ft.Offset(0, 4)),
                on_click=lambda e, x=t: abrir_chamada(x),
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Icon(ft.Icons.CLASS_, color="white", size=20), bgcolor=CORES['roxo_brand'], padding=8, border_radius=8),
                        ft.Column([
                            ft.Text(t.get('curso'), weight="bold", size=14, color="#111827", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(t.get('nome_turma'), size=11, color="grey")
                        ], spacing=2, expand=True)
                    ]),
                    ft.Divider(color="transparent", height=10),
                    ft.Row([
                        ft.Icon(ft.Icons.ACCESS_TIME, size=14, color="grey"),
                        ft.Text(t.get('turno'), size=12, color="grey"),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.PEOPLE, size=14, color="grey"),
                        ft.Text(f"{qtd} Alunos", size=12, color="grey")
                    ]),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Iniciar Chamada", color="white", bgcolor=CORES['ouro'], width=float("inf"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=lambda e, x=t: abrir_chamada(x))
                ])
            )
            cards.append(card)
        
        grid_aulas.controls = cards
        page.update()

    def logout(e): page.session.clear(); page.go("/")

    # --- RESPONSIVIDADE ---
    app_bar = ft.Container(bgcolor=CORES['roxo_brand'], padding=15, content=ft.Row([ft.Text("Renovar Mobile", color="white", weight="bold", size=18), ft.Container(expand=True), ft.IconButton(ft.Icons.LOGOUT, icon_color="white", on_click=logout)]))
    sidebar_prof = ft.Container(width=80, bgcolor=CORES['roxo_brand'], padding=20, content=ft.Column([ft.Image(src="logo_renovar.png", width=40, height=40), ft.Divider(color="white24"), ft.IconButton(icon=ft.Icons.HOME, icon_color="white"), ft.Container(expand=True), ft.IconButton(icon=ft.Icons.LOGOUT, icon_color="red", on_click=logout)], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
    content_area = ft.Container(expand=True, bgcolor="#F3F4F6", padding=35, content=ft.Column([ft.Row([ft.Column([ft.Text(f"Área do Professor", size=24, weight="bold", color="#31144A"), ft.Text(f"Bem-vindo(a), {nome_professor}! Selecione sua turma.", size=13, color="grey")]), ft.CircleAvatar(content=ft.Text(nome_professor[0].upper(), color="white"), bgcolor=CORES['ouro'])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Divider(height=30, color="transparent"), grid_aulas]))

    layout_row = ft.Row([sidebar_prof, content_area], expand=True, spacing=0) 
    main_col = ft.Column([app_bar, content_area], expand=True, spacing=0)

    view = ft.View("/teacher", padding=0, bgcolor=CORES['fundo'])

    def ajustar_layout(e):
        is_mobile = page.width < 768
        if is_mobile:
            view.controls = [main_col]
            content_area.padding = 15
        else:
            view.controls = [layout_row]
            content_area.padding = 35
        
        if hasattr(page, 'views') and len(page.views) > 0:
            page.update()

    page.on_resized = ajustar_layout
    carregar_turmas()
    ajustar_layout(None)
    
    return view