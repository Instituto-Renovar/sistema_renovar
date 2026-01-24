import flet as ft
from core.colors import CORES
from controllers.class_controller import ClassController
from controllers.schedule_controller import ScheduleController
import datetime

def TeacherView(page: ft.Page):
    nome_prof = page.session.get("user_name") or "Professor"
    
    class_ctrl = ClassController()
    schedule_ctrl = ScheduleController()

    def logout(e):
        page.session.clear(); page.go("/")

    # --- LÓGICA DA CHAMADA ---
    def abrir_diario_classe(turma):
        # 1. Busca o Cronograma (Aulas)
        aulas = schedule_ctrl.buscar_aulas_por_turma(turma['id'])
        
        # Ordena por data
        aulas.sort(key=lambda x: x.get('data', ''))
        
        # Container da Lista de Aulas
        lista_aulas_visual = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)

        # --- NOVA FUNÇÃO: MOSTRAR BOLETIM ---
        def abrir_boletim(e):
            page.close(bs_aulas)
            
            dados_boletim = class_ctrl.gerar_boletim_turma(turma['id'])
            
            coluna_alunos = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
            
            if not dados_boletim:
                coluna_alunos.controls.append(ft.Text("Sem dados suficientes para gerar boletim.", color="grey"))
            else:
                # Cabeçalho
                coluna_alunos.controls.append(
                    ft.Row([
                        ft.Text("Aluno", weight="bold", expand=True),
                        ft.Text("Freq.", width=50, text_align="center"),
                        ft.Text("Média", width=50, text_align="center"),
                        ft.Text("Status", width=100, text_align="center"),
                    ])
                )
                coluna_alunos.controls.append(ft.Divider())

                # --- IMPORTAR O CONTROLLER NO TOPO DO ARQUIVO DEPOIS ---
                # from controllers.certificate_controller import CertificateController
                
                for d in dados_boletim:
                    cor_status = "green" if d['status'] == "Aprovado" else "red"
                    bg_status = "#DCFCE7" if d['status'] == "Aprovado" else "#FEE2E2"
                    
                    # Botão de Certificado (Só aparece se Aprovado)
                    btn_certificado = ft.Container()
                    if d['status'] == "Aprovado":
                        def gerar_cert(e, aluno=d):
                            import os
                            # Gambiarra rápida para importar aqui sem mexer no topo agora
                            from controllers.certificate_controller import CertificateController
                            cert = CertificateController()
                            
                            # Dados simulados (depois pegamos do banco da turma)
                            caminho = cert.gerar_pdf(aluno['nome'], turma['curso'], "40", datetime.date.today().strftime("%Y-%m-%d"))
                            
                            if caminho:
                                page.launch_url(f"file:///{caminho}") # Tenta abrir o PDF
                                page.snack_bar = ft.SnackBar(ft.Text(f"Certificado Gerado: {aluno['nome']}"), bgcolor="green")
                                page.snack_bar.open = True
                                page.update()

                        btn_certificado = ft.IconButton(
                            ft.Icons.PRINT, 
                            tooltip="Gerar Certificado", 
                            icon_color="green",
                            on_click=gerar_cert
                        )

                    coluna_alunos.controls.append(
                        ft.Container(
                            padding=10,
                            bgcolor="white",
                            border_radius=8,
                            border=ft.border.all(1, "#F3F4F6"),
                            content=ft.Row([
                                ft.Text(d['nome'], size=13, expand=True, weight="bold"),
                                ft.Text(f"{d['frequencia']}%", width=50, text_align="center", size=12),
                                ft.Text(str(d['media']), width=50, text_align="center", weight="bold", size=12),
                                ft.Container(
                                    content=ft.Text(d['status'].split()[0], color=cor_status, size=10, weight="bold"),
                                    bgcolor=bg_status, padding=5, border_radius=5, width=90, alignment=ft.alignment.center
                                ),
                                btn_certificado # <--- ADICIONADO O BOTÃO AQUI NO FINAL DA LINHA
                            ])
                        )
                    )

            dlg_boletim = ft.AlertDialog(
                title=ft.Text("Desempenho da Turma"),
                content=ft.Container(width=500, content=coluna_alunos),
                actions=[ft.TextButton("Fechar", on_click=lambda e: page.close(dlg_boletim))]
            )
            page.open(dlg_boletim)

        # --- FIM NOVA FUNÇÃO ---

        bs_aulas = ft.BottomSheet(
            ft.Container(
                padding=20, bgcolor="white",
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Diário: {turma['nome_turma']}", size=20, weight="bold", color=CORES['roxo_brand'], expand=True),
                        ft.IconButton(ft.Icons.ANALYTICS, tooltip="Ver Desempenho", icon_color=CORES['ouro'], on_click=abrir_boletim) # <--- BOTÃO NOVO AQUI
                    ]),
                    ft.Divider(),
                    lista_aulas_visual,
                    ft.Container(height=10),
                    ft.ElevatedButton("Ver Boletim da Turma", width=400, bgcolor=CORES['roxo_brand'], color="white", on_click=abrir_boletim) # <--- BOTÃO GRANDE NO FINAL
                ], tight=True)
            )
        )

        def abrir_lista_presenca(aula):
            # Fecha a lista de aulas anterior
            page.close(bs_aulas)
            
            # --- 1. Identifica se é dia de Prova ---
            # Normaliza o texto para minúsculas para facilitar a busca
            conteudo_lower = aula.get('conteudo', '').lower()
            termos_prova = ["prova", "avaliação", "exame", "teste", "Prova"]
            
            # Verifica se algum dos termos está no título OU se o flag do banco é True
            eh_prova = aula.get('e_prova') is True or any(termo in conteudo_lower for termo in termos_prova)
            
            # Busca alunos e dados anteriores
            nome_completo = f"{turma['curso']} - {turma['nome_turma']}"
            alunos = class_ctrl.buscar_alunos_da_turma(nome_completo)
            chamada_existente = class_ctrl.buscar_chamada_da_aula(aula['id'])
            
            ids_presentes = chamada_existente.get('presentes', []) if chamada_existente else []
            notas_salvas = chamada_existente.get('notas', {}) if chamada_existente else {}

            # Lista para guardar as referências dos campos (Checkboxes e Inputs de Nota)
            controles_alunos = []
            
            lista_visual_alunos = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

            if not alunos:
                lista_visual_alunos.controls.append(ft.Text("Nenhum aluno encontrado.", color="red"))
            
            for aluno in alunos:
                aluno_id = aluno['id']
                esta_presente = True
                if chamada_existente:
                    esta_presente = aluno_id in ids_presentes
                
                # Checkbox de Presença
                chk = ft.Checkbox(value=esta_presente, active_color="green")
                
                # Campo de Nota (Só aparece se for prova)
                nota_anterior = notas_salvas.get(aluno_id, "")
                txt_nota = ft.TextField(
                    value=str(nota_anterior), 
                    width=60, 
                    text_size=12,
                    content_padding=5,
                    text_align=ft.TextAlign.CENTER,
                    hint_text="0-10",
                    visible=eh_prova, # Só mostra se for prova
                    keyboard_type=ft.KeyboardType.NUMBER,
                    disabled=not esta_presente # Desabilita se aluno faltou (lógica visual inicial)
                )

                # Funçãozinha para habilitar/desabilitar nota ao clicar na presença
                def on_change_presenca(e, t=txt_nota):
                    t.disabled = not e.control.value
                    if not e.control.value: t.value = "" # Limpa nota se faltou
                    t.update()
                
                chk.on_change = on_change_presenca

                # Guarda referências para usarmos no Salvar
                controles_alunos.append({
                    "id": aluno_id,
                    "chk": chk,
                    "txt_nota": txt_nota
                })

                # Linha do Aluno (Nome --- Nota - Presença)
                row = ft.Container(
                    padding=5,
                    content=ft.Row([
                        ft.Text(aluno.get('nome', 'Sem Nome'), weight="bold", size=13, expand=True, color="#374151"),
                        txt_nota,
                        chk
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
                lista_visual_alunos.controls.append(row)
                lista_visual_alunos.controls.append(ft.Divider(height=1, color="#F3F4F6"))

            # --- Botão Salvar Presença (E Notas) ---
            def salvar_presenca(e):
                lista_presentes = []
                dicionario_notas = {}
                
                for item in controles_alunos:
                    if item['chk'].value:
                        aid = item['id']
                        lista_presentes.append(aid)
                        # Se for prova, salva a nota
                        if eh_prova:
                            nota_val = item['txt_nota'].value
                            if nota_val: dicionario_notas[aid] = nota_val

                total = len(alunos)
                qtd_presentes = len(lista_presentes)
                
                dados = {
                    "aula_id": aula['id'],
                    "turma_id": turma['id'],
                    "data": aula['data'],
                    "presentes": lista_presentes,
                    "notas": dicionario_notas, # Novo campo salvo
                    "total_alunos": total,
                    "qtd_presentes": qtd_presentes,
                    "nome_turma": nome_completo 
                }
                
                sucesso, msg = class_ctrl.salvar_chamada(dados)
                if sucesso:
                    schedule_ctrl.atualizar_status_aula(aula['id'], True)
                    texto_feedback = f"Chamada Salva! {qtd_presentes}/{total}."
                    if eh_prova: texto_feedback += " Notas registradas."
                    
                    page.snack_bar = ft.SnackBar(ft.Text(texto_feedback), bgcolor="green")
                    page.snack_bar.open = True
                    page.close(dlg_chamada)
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="red"); page.snack_bar.open=True; page.update()

            # Título do Modal
            data_titulo = datetime.datetime.strptime(aula['data'], '%Y-%m-%d').strftime('%d/%m')
            titulo_modal = f"Chamada - {data_titulo}"
            if eh_prova: titulo_modal += " (PROVA 📝)"

            dlg_chamada = ft.AlertDialog(
                title=ft.Text(titulo_modal, size=16),
                content=ft.Container(
                    width=400, height=450,
                    content=ft.Column([
                        ft.Text(f"Tema: {aula['conteudo']}", size=12, weight="bold", color="grey"),
                        ft.Divider(),
                        ft.Row([ft.Text("Aluno"), ft.Text("Nota  Presença" if eh_prova else "Presença")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        lista_visual_alunos
                    ])
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_chamada)),
                    ft.ElevatedButton("Salvar", bgcolor="green", color="white", on_click=salvar_presenca)
                ],
                bgcolor="white",
                shape=ft.RoundedRectangleBorder(radius=10)
            )
            page.open(dlg_chamada)

        # Preenche a lista de aulas visual
        data_hoje = datetime.date.today().strftime("%Y-%m-%d")
        
        for aula in aulas:
            # Formata data
            dt_obj = datetime.datetime.strptime(aula['data'], "%Y-%m-%d")
            dt_fmt = dt_obj.strftime("%d/%m")
            dia_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][dt_obj.weekday()]
            
            # Estilo do Card
            eh_hoje = (aula['data'] == data_hoje)
            ja_realizada = aula.get('realizada', False)
            
            cor_bg = "#DCFCE7" if eh_hoje else ("#F3F4F6" if ja_realizada else "white")
            icone = ft.Icons.CHECK_CIRCLE if ja_realizada else (ft.Icons.TODAY if eh_hoje else ft.Icons.CIRCLE_OUTLINED)
            cor_icone = "green" if ja_realizada else ("blue" if eh_hoje else "grey")
            
            # --- CORREÇÃO AQUI: EXIBINDO O CONTEÚDO COMPLETO ---
            texto_aula = aula['conteudo'] # Antes tinha .split(' - ')[0]
            
            item = ft.Container(
                bgcolor=cor_bg, padding=15, border_radius=10,
                border=ft.border.all(1, "green" if eh_hoje else "#E5E7EB"),
                on_click=lambda e, a=aula: abrir_lista_presenca(a),
                content=ft.Row([
                    ft.Container(width=50, content=ft.Column([ft.Text(dt_fmt, weight="bold"), ft.Text(dia_semana, size=10, color="grey")], spacing=0, alignment=ft.MainAxisAlignment.CENTER)),
                    ft.Column([
                        # Exibe o texto completo (Módulo + Tema)
                        ft.Text(texto_aula, weight="bold", size=14, color="#374151", overflow=ft.TextOverflow.ELLIPSIS), 
                        ft.Text("Clique para fazer chamada" if not ja_realizada else "Chamada realizada", size=11, color="green" if ja_realizada else "grey")
                    ], spacing=2, expand=True),
                    ft.Icon(icone, color=cor_icone)
                ])
            )
            lista_aulas_visual.controls.append(item)

        page.open(bs_aulas)

    # --- TELA PRINCIPAL DO PROFESSOR ---
    turmas = class_ctrl.buscar_turmas_do_professor(nome_prof)
    lista_turmas = ft.Column(spacing=15)

    if not turmas:
        lista_turmas.controls.append(ft.Container(padding=40, content=ft.Text("Nenhuma turma encontrada.", color="grey")))
    else:
        for t in turmas:
            card = ft.Container(
                bgcolor="white", padding=20, border_radius=12,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black")),
                on_click=lambda e, x=t: abrir_diario_classe(x), 
                content=ft.Row([
                    ft.Container(width=50, height=50, bgcolor="#F3F4F6", border_radius=10, content=ft.Icon(ft.Icons.CLASS_, color=CORES['roxo_brand'])),
                    ft.Column([
                        ft.Text(t.get('curso', 'Curso'), weight="bold", size=14, color="#111827"),
                        ft.Text(f"{t.get('nome_turma')} • {t.get('turno')}", size=12, color="grey")
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="grey")
                ])
            )
            lista_turmas.controls.append(card)

    return ft.View(
        route="/teacher", bgcolor="#F3F4F6", padding=0,
        controls=[
            ft.Container(
                bgcolor=CORES['roxo_brand'], padding=ft.padding.symmetric(horizontal=20, vertical=15),
                content=ft.Row([
                    ft.Column([ft.Text(f"Olá, {nome_prof}", color="white", weight="bold", size=16), ft.Text("Área do Professor", color=CORES['ouro'], size=12)], spacing=0),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color="white", on_click=logout)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ),
            ft.Container(
                padding=20, expand=True,
                content=ft.Column([ft.Text("Suas Turmas Ativas", weight="bold", size=18, color="#374151"), ft.Container(height=10), ft.Column([lista_turmas], scroll=ft.ScrollMode.AUTO, expand=True)])
            )
        ]
    )