import flet as ft
import os
from core.colors import CORES
from components.sidebar import Sidebar
from components.custom_inputs import RenovarTextField, RenovarDropdown
# Importando as máscaras
from core.utils import formatar_cpf, formatar_data, formatar_cep, formatar_telefone, formatar_moeda
# Controllers
from controllers.class_controller import ClassController
from controllers.leads_controller import LeadsController
from controllers.contract_controller import ContractController

def ClassesView(page: ft.Page):
    # 1. Instancia os Controllers
    class_ctrl = ClassController()
    leads_ctrl = LeadsController()
    contract_ctrl = ContractController()

    # 2. Cache de Contagem (Para não travar o banco)
    cache_contagem = {}

    # 3. Gerenciador de Downloads (CORREÇÃO DO ERRO 'downloader not defined')
    # Definimos ele aqui no topo para estar disponível em toda a tela
    downloader = ft.FilePicker(on_result=lambda e: print(f"Status do salvamento: {e.path}"))
    page.overlay.append(downloader) # Adiciona o componente invisível à página

    # --- HELPER: Label Externo ---
    def campo_label(label, input_control, expand=1):
        return ft.Column([
            ft.Text(label, size=12, weight="bold", color="#111827", font_family="Jost"),
            input_control
        ], spacing=5, expand=expand)

    # ... (O código continua aqui com def abrir_perfil_aluno...)

    # =============================================================================================
    # 3. MODAL FICHA DE MATRÍCULA
    # =============================================================================================
    def abrir_perfil_aluno(aluno):
        # --- SEÇÃO 1: DADOS PESSOAIS ---
        txt_nome = RenovarTextField("Nome Completo", value=aluno.get('nome'))
        # Máscaras aplicadas:
        txt_cpf = RenovarTextField("CPF (000.000.000-00)", value=aluno.get('cpf', ''), on_change=formatar_cpf)
        txt_rg = RenovarTextField("RG", value=aluno.get('rg', ''))
        txt_orgao = RenovarTextField("Órgão Exp.", value=aluno.get('orgao_exp', ''))
        txt_nasc = RenovarTextField("Data Nasc. (DD/MM/AAAA)", value=aluno.get('nascimento', ''), on_change=formatar_data)
        
        dd_sexo = RenovarDropdown("Sexo", options=["Feminino", "Masculino"], value=aluno.get('sexo'))
        dd_civil = RenovarDropdown("Estado Civil", options=["Solteiro(a)", "Casado(a)", "Divorciado(a)"], value=aluno.get('estado_civil'))
        
        txt_mae = RenovarTextField("Nome da Mãe", value=aluno.get('nome_mae', ''))
        txt_pai = RenovarTextField("Nome do Pai", value=aluno.get('nome_pai', ''))
        txt_natural = RenovarTextField("Naturalidade", value=aluno.get('naturalidade', ''))
        txt_prof = RenovarTextField("Profissão", value=aluno.get('profissao', ''))

        # --- SEÇÃO 2: ENDEREÇO E CONTATO ---
        txt_end = RenovarTextField("Logradouro", value=aluno.get('endereco', ''))
        txt_bairro = RenovarTextField("Bairro", value=aluno.get('bairro', ''))
        txt_cidade = RenovarTextField("Cidade", value=aluno.get('cidade', ''))
        txt_uf = RenovarTextField("UF", value=aluno.get('uf', ''), width=80)
        
        # Máscaras aplicadas:
        txt_cep = RenovarTextField("CEP", value=aluno.get('cep', ''), on_change=formatar_cep)
        txt_tel = RenovarTextField("Celular", value=aluno.get('telefone', ''), on_change=formatar_telefone)
        txt_email = RenovarTextField("E-mail", value=aluno.get('email', ''))

        # --- SEÇÃO 3: FINANCEIRO E CURSO ---
        txt_curso = RenovarTextField("Curso", value=aluno.get('nome_curso') or aluno.get('interesse', ''), read_only=True)
        txt_turno = RenovarTextField("Turno", value=aluno.get('turno', ''))
        # Máscara data
        txt_inicio = RenovarTextField("Início (DD/MM/AAAA)", value=aluno.get('data_inicio', ''), on_change=formatar_data)
        
        # Máscaras de Moeda aplicadas:
        txt_v_mensal = RenovarTextField("Mensalidade (R$)", value=aluno.get('valor_mensal', ''), on_change=formatar_moeda)
        txt_v_total = RenovarTextField("Valor Total (R$)", value=aluno.get('valor_total', ''), on_change=formatar_moeda)
        
        txt_pagto = RenovarDropdown("Forma de Pagto", options=["Boleto", "Cartão", "Pix", "Dinheiro"], value=aluno.get('forma_pagamento'))

        def salvar_dados(e):
            dados_atualizados = {
                "nome": txt_nome.value, "cpf": txt_cpf.value, "rg": txt_rg.value, "orgao_exp": txt_orgao.value,
                "nascimento": txt_nasc.value, "sexo": dd_sexo.value, "estado_civil": dd_civil.value,
                "nome_mae": txt_mae.value, "nome_pai": txt_pai.value, "naturalidade": txt_natural.value, "profissao": txt_prof.value,
                "endereco": txt_end.value, "bairro": txt_bairro.value, "cidade": txt_cidade.value, "uf": txt_uf.value,
                "cep": txt_cep.value, "telefone": txt_tel.value, "email": txt_email.value,
                "turno": txt_turno.value, "data_inicio": txt_inicio.value,
                "valor_mensal": txt_v_mensal.value, "valor_total": txt_v_total.value, "forma_pagamento": txt_pagto.value
            }
            
            leads_ctrl.atualizar_lead(aluno['id'], dados_atualizados)
            aluno.update(dados_atualizados)
            
            page.snack_bar = ft.SnackBar(ft.Text("Ficha do aluno salva com sucesso!"), bgcolor="green")
            page.snack_bar.open = True
            page.update()

        def acao_gerar_contrato(e):
            salvar_dados(None) 
            btn_contrato.text = "Gerando..."
            btn_contrato.disabled = True
            btn_contrato.update()
            
            # --- AQUI ESTAVA O PROBLEMA: Definindo as variáveis ---
            caminho, msg = contract_ctrl.gerar_contrato(aluno)
            # ----------------------------------------------------
            
            btn_contrato.text = "Gerar Contrato PDF"
            btn_contrato.disabled = False
            btn_contrato.update()
            
            cor_msg = "red" # Padrão caso falhe

            if caminho:
                # Se gerou sucesso
                cor_msg = "green"
                # Se for DOCX, oferece para salvar
                if caminho.endswith(".docx"):
                     downloader.save_file(
                        dialog_title="Salvar Contrato",
                        file_name=os.path.basename(caminho),
                        initial_directory="Downloads"
                     )
            
            # Exibe a mensagem (msg) que veio do controller
            page.snack_bar = ft.SnackBar(ft.Text(str(msg)), bgcolor=cor_msg)
            page.snack_bar.open = True
            page.update()

        btn_contrato = ft.ElevatedButton(
            "Gerar Contrato PDF", icon=ft.Icons.PICTURE_AS_PDF, bgcolor="#31144A", color="white", height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=acao_gerar_contrato
        )
        
        btn_salvar = ft.ElevatedButton(
            "Salvar Ficha", icon=ft.Icons.SAVE, bgcolor=CORES['ouro'], color="white", height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=salvar_dados
        )

        conteudo_modal = ft.Column([
            ft.Text("Dados Pessoais", weight="bold", size=16, color=CORES['roxo_brand']),
            ft.Divider(),
            campo_label("Nome Completo", txt_nome),
            ft.Row([campo_label("CPF", txt_cpf), campo_label("RG", txt_rg), campo_label("Órgão Exp", txt_orgao)], spacing=10),
            ft.Row([campo_label("Nascimento", txt_nasc), campo_label("Sexo", dd_sexo), campo_label("Estado Civil", dd_civil)], spacing=10),
            ft.Row([campo_label("Nome da Mãe", txt_mae), campo_label("Nome do Pai", txt_pai)], spacing=10),
            ft.Row([campo_label("Naturalidade", txt_natural), campo_label("Profissão", txt_prof)], spacing=10),
            
            ft.Container(height=20),
            ft.Text("Endereço e Contato", weight="bold", size=16, color=CORES['roxo_brand']),
            ft.Divider(),
            campo_label("Logradouro", txt_end),
            ft.Row([campo_label("Bairro", txt_bairro), campo_label("CEP", txt_cep)], spacing=10),
            ft.Row([campo_label("Cidade", txt_cidade), campo_label("UF", txt_uf)], spacing=10),
            ft.Row([campo_label("Celular/Whatsapp", txt_tel), campo_label("E-mail", txt_email)], spacing=10),

            ft.Container(height=20),
            ft.Text("Financeiro do Curso", weight="bold", size=16, color=CORES['roxo_brand']),
            ft.Divider(),
            ft.Row([campo_label("Curso", txt_curso), campo_label("Turno", txt_turno), campo_label("Início", txt_inicio)], spacing=10),
            ft.Row([campo_label("Valor Mensal", txt_v_mensal), campo_label("Valor Total", txt_v_total), campo_label("Forma Pagto", txt_pagto)], spacing=10),
        ], scroll=ft.ScrollMode.AUTO)

        dlg_aluno = ft.AlertDialog(
            title=ft.Row([ft.Text("Ficha de Matrícula", weight="bold", size=20), ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_aluno))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=700, height=600, content=conteudo_modal),
            actions=[
                ft.Row([btn_salvar, ft.Container(width=10), btn_contrato], alignment=ft.MainAxisAlignment.END)
            ],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.open(dlg_aluno)

    # =============================================================================================
    # 2. MODAL LISTA DE ALUNOS
    # =============================================================================================
    def abrir_detalhes_turma(turma):
        nome_completo_turma = f"{turma.get('curso')} - {turma.get('nome_turma')}"
        alunos = class_ctrl.buscar_alunos_da_turma(nome_completo_turma)
        
        lista_visual = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)
        
        if not alunos:
            lista_visual.controls.append(ft.Container(padding=20, content=ft.Text("Nenhum aluno matriculado nesta turma ainda.", color="grey", text_align="center")))
        
        for aluno in alunos:
            # Preenche dados faltantes da turma no objeto aluno para a ficha
            aluno['nome_curso'] = turma.get('curso')
            # Só sobrescreve se o aluno não tiver turno próprio salvo
            if not aluno.get('turno'): aluno['turno'] = turma.get('turno')
            if not aluno.get('data_inicio'): aluno['data_inicio'] = turma.get('data_inicio')

            card_aluno = ft.Container(
                bgcolor="#F9FAFB", padding=10, border_radius=8,
                border=ft.border.all(1, "#E5E7EB"),
                content=ft.Row([
                    ft.CircleAvatar(content=ft.Text(aluno.get('nome','?')[0], size=12), width=30, height=30, bgcolor=CORES['roxo_brand']),
                    ft.Column([
                        ft.Text(aluno.get('nome', 'Sem Nome'), weight="bold", size=13),
                        ft.Text(aluno.get('telefone', ''), size=11, color="grey")
                    ], spacing=2, expand=True),
                    ft.IconButton(ft.Icons.EDIT_DOCUMENT, icon_size=18, icon_color=CORES['ouro'], tooltip="Abrir Ficha", on_click=lambda e, a=aluno: abrir_perfil_aluno(a))
                ]),
                on_click=lambda e, a=aluno: abrir_perfil_aluno(a)
            )
            lista_visual.controls.append(card_aluno)

        dlg_turma = ft.AlertDialog(
            title=ft.Row([
                ft.Column([
                    ft.Text(turma.get('curso'), weight="bold", size=16, color="#31144A"),
                    ft.Text(turma.get('nome_turma'), size=12, color="grey")
                ], spacing=2),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_turma))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(width=450, content=lista_visual),
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.open(dlg_turma)

    # =============================================================================================
    # 1. GRID DE TURMAS
    # =============================================================================================
    grid_turmas = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=400,
        child_aspect_ratio=1.5,
        spacing=20,
        run_spacing=20,
    )

    # =============================================================================================
    # OTIMIZAÇÃO: Cache para não ir no banco dentro do loop
    # =============================================================================================
    def carregar_turmas():
        # 1. Busca todas as turmas (1 Leitura)
        turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
        
        # 2. Busca TODOS os alunos de uma vez só (1 Leitura Grande em vez de 50 pequenas)
        # Assumindo que o leads_ctrl tem um método para buscar tudo ou podemos buscar filtrado
        # Se não tiver, vamos contar na "raça" mas de forma inteligente:
        # A melhor forma seria o ClassController ter um método "contar_alunos_todas_turmas"
        # Mas para não mexer no Controller agora, vamos usar o LeadsController.
        
        todos_leads = leads_ctrl.buscar_leads(filtro_status=['Matriculado']) # Só quem conta
        
        # Zera e preenche o cache
        cache_contagem.clear()
        for lead in todos_leads:
            turma_vinculada = lead.get('turma_vinculada')
            if turma_vinculada:
                cache_contagem[turma_vinculada] = cache_contagem.get(turma_vinculada, 0) + 1
        
        # Agora cria os cards usando o cache (memória RAM)
        grid_turmas.controls = [criar_card_turma(t) for t in turmas]
        page.update()

    def criar_card_turma(turma):
        curso = turma.get('curso', 'Curso')
        nome_turma = turma.get('nome_turma', 'Turma')
        data_inicio = turma.get('data_inicio', '--/--/--')
        turno = turma.get('turno', 'Noite')
        capacidade_max = int(turma.get('capacidade', 15))
        status = turma.get('status', 'Aberta')
        
        id_composto = f"{curso} - {nome_turma}"
        
        # --- OTIMIZADO: Lê do cache, não do banco ---
        qtd_alunos = cache_contagem.get(id_composto, 0) 
        # --------------------------------------------
        
        progresso = qtd_alunos / capacidade_max if capacidade_max > 0 else 0
        cor_progresso = CORES['ouro'] if progresso < 0.8 else "red"

        icone_turno = ft.Icons.NIGHTLIGHT_ROUND if turno == "Noite" else (ft.Icons.WB_SUNNY if turno == "Manhã" else ft.Icons.WB_TWILIGHT)
        cor_status = "#DCFCE7" if status == "Aberta" else "#F3F4F6"
        txt_status = "#166534" if status == "Aberta" else "#374151"

        return ft.Container(
            bgcolor="white", border_radius=12, padding=20,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black"), offset=ft.Offset(0, 4)),
            on_click=lambda e: abrir_detalhes_turma(turma), 
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.SCHOOL, color="white", size=20), bgcolor=CORES['roxo_brand'], padding=8, border_radius=8),
                    ft.Column([
                        ft.Text(curso, weight="bold", size=14, color="#111827", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(nome_turma, size=11, color="#6B7280")
                    ], spacing=2, expand=True),
                    ft.Container(content=ft.Text(status.upper(), size=9, weight="bold", color=txt_status), bgcolor=cor_status, padding=ft.padding.symmetric(6, 2), border_radius=4)
                ]),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color="grey"), ft.Text(data_inicio, size=12, color="grey")]),
                    ft.Row([ft.Icon(icone_turno, size=14, color="grey"), ft.Text(turno, size=12, color="grey")]),
                ], spacing=15),
                ft.Container(expand=True),
                ft.Column([
                    ft.Row([ft.Text("Ocupação", size=11, color="grey"), ft.Text(f"{qtd_alunos} / {capacidade_max} Alunos", size=11, weight="bold", color="#374151")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=progresso, color=cor_progresso, bgcolor="#F3F4F6", height=6, border_radius=3)
                ], spacing=5)
            ])
        )

    def carregar_turmas():
        # 1. Busca todas as turmas (1 Leitura)
        turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
        
        # 2. Busca TODOS os alunos de uma vez só (1 Leitura Grande em vez de 50 pequenas)
        # Assumindo que o leads_ctrl tem um método para buscar tudo ou podemos buscar filtrado
        # Se não tiver, vamos contar na "raça" mas de forma inteligente:
        # A melhor forma seria o ClassController ter um método "contar_alunos_todas_turmas"
        # Mas para não mexer no Controller agora, vamos usar o LeadsController.
        
        todos_leads = leads_ctrl.buscar_leads(filtro_status=['Matriculado']) # Só quem conta
        
        # Zera e preenche o cache
        cache_contagem.clear()
        for lead in todos_leads:
            turma_vinculada = lead.get('turma_vinculada')
            if turma_vinculada:
                cache_contagem[turma_vinculada] = cache_contagem.get(turma_vinculada, 0) + 1
        
        # Agora cria os cards usando o cache (memória RAM)
        grid_turmas.controls = [criar_card_turma(t) for t in turmas]
        page.update()

    # --- LAYOUT GERAL ---
# CÓDIGO NOVO (Colar)
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        
        # Verifica se recebeu um NÚMERO (da Sidebar) ou BOTÃO (do Menu Mobile)
        if isinstance(e, int):
            idx = e
        else:
            idx = e.control.selected_index
            
        page.go(rotas[idx])

    sidebar = Sidebar(page, selected_index=2)

    topo = ft.Row([
        ft.Column([
            ft.Text("Gestão de Turmas", size=24, weight="bold", color="#31144A", font_family="Jost"),
            ft.Text("Acompanhe o preenchimento das turmas", size=13, color="#6B7280")
        ], spacing=0),
        ft.Container(expand=True),
        ft.Container(
            width=250, height=40, bgcolor="white", border_radius=8,
            border=ft.border.all(1, "#E5E7EB"), padding=ft.padding.only(left=15),
            content=ft.Row([ft.Icon(ft.Icons.SEARCH, color="#9CA3AF", size=18), ft.TextField(hint_text="Buscar...", border="none", text_size=13)], spacing=5)
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    content = ft.Row([
        sidebar,
        ft.Container(expand=True, bgcolor="#F3F4F6", padding=35, content=ft.Column([topo, ft.Container(height=30), grid_turmas]))
    ], expand=True, spacing=0)

    carregar_turmas()
    
    return ft.View(
        route="/classes", 
        controls=[content], 
        padding=0, 
        bgcolor=CORES['fundo'],
        scroll=None 
    )