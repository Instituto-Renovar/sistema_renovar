import flet as ft
from core.colors import CORES
from components.sidebar import Sidebar
from components.custom_inputs import RenovarTextField
from controllers.leads_controller import LeadsController
from controllers.class_controller import ClassController
import datetime

def FrequencyView(page: ft.Page):
    leads_ctrl = LeadsController()
    class_ctrl = ClassController()
    
    # Tabela com largura total
    tabela = ft.DataTable(
        width=float("inf"),
        columns=[
            ft.DataColumn(ft.Text("Aluno", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Turma", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Frequência", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Faltas", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Status", weight="bold", size=12, color="#6B7280")),
            ft.DataColumn(ft.Text("Ação", weight="bold", size=12, color="#6B7280")),
        ],
        rows=[], heading_row_height=40, data_row_min_height=60, column_spacing=20, expand=True, divider_thickness=0
    )

    def abrir_registro_conversa(aluno):
        txt_obs = RenovarTextField("Resumo da Conversa / Ocorrência", multiline=True, height=120)
        
        def salvar_conversa(e):
            if not txt_obs.value: return
            novo_registro = f"{datetime.datetime.now().strftime('%d/%m/%Y')}: {txt_obs.value}"
            historico = aluno.get('historico_ocorrencias', [])
            if isinstance(historico, str): historico = [historico]
            historico.append(novo_registro)
            leads_ctrl.atualizar_lead(aluno['id'], {'historico_ocorrencias': historico})
            page.close(dlg)
            page.snack_bar = ft.SnackBar(ft.Text("Ocorrência registrada!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Conversa: {aluno.get('nome')}", size=16, weight="bold"),
            content=ft.Container(width=400, content=ft.Column([ft.Text("Registre o motivo da conversa.", size=12, color="grey"), txt_obs], spacing=10, height=150)),
            actions=[ft.ElevatedButton("Salvar", bgcolor=CORES['ouro'], color="white", on_click=salvar_conversa)],
            bgcolor="white", shape=ft.RoundedRectangleBorder(radius=10)
        )
        page.open(dlg)

    def carregar_dados():
        alunos = leads_ctrl.buscar_leads(filtro_status="Matriculado")
        tabela.rows.clear()
        
        for aluno in alunos:
            turma = aluno.get('turma_vinculada', 'Sem Turma')
            
            # --- Lógica de Dados e Cores ---
            perc = 0
            faltas = 0
            txt_status = "Sem Dados"
            tem_dados = False
            
            # Cores Padrão (Sem Dados - Branco)
            cor_linha = "white"
            cor_texto_status = "#6B7280" # Cinza
            cor_barra = "#E5E7EB"

            if turma != 'Sem Turma':
                dados_freq = class_ctrl.calcular_frequencia_aluno(aluno['id'], turma)
                
                if dados_freq is not None:
                    perc = dados_freq['percentual']
                    faltas = dados_freq['faltas']
                    tem_dados = True
                    
                    # REGULAR (Verde)
                    cor_linha = "#F0FDF4" 
                    cor_texto_status = "#166534"
                    cor_barra = "#10B981"
                    txt_status = "Regular"
                    
                    # ATENÇÃO (Amarelo)
                    if perc < 75:
                        cor_linha = "#FFFBEB"
                        cor_texto_status = "#92400E"
                        cor_barra = "#F59E0B"
                        txt_status = "Atenção"
                        
                    # CRÍTICO (Vermelho)
                    if perc < 50:
                        cor_linha = "#FEF2F2"
                        cor_texto_status = "#991B1B"
                        cor_barra = "#EF4444"
                        txt_status = "Crítico"

            tabela.rows.append(
                ft.DataRow(
                    color=cor_linha, # APLICA A COR NA LINHA INTEIRA
                    cells=[
                        ft.DataCell(ft.Row([
                            ft.CircleAvatar(content=ft.Text(aluno.get('nome','?')[0], size=10), width=28, height=28, bgcolor=CORES['roxo_brand']), 
                            ft.Text(aluno.get('nome'), size=13, weight="bold", color="#1F2937")
                        ], spacing=10)),
                        ft.DataCell(ft.Text(turma, size=12, color="#4B5563")),
                        ft.DataCell(
                            ft.Column([
                                ft.Text(f"{perc}%" if tem_dados else "--", size=11, weight="bold", color=cor_texto_status),
                                ft.ProgressBar(value=perc/100, color=cor_barra, bgcolor="white", height=6, border_radius=3)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2, width=80)
                        ),
                        ft.DataCell(ft.Text(f"{faltas} faltas" if tem_dados else "-", size=12, color="#4B5563")),
                        ft.DataCell(ft.Text(txt_status, size=12, weight="bold", color=cor_texto_status)),
                        ft.DataCell(ft.ElevatedButton("Conversar", icon=ft.Icons.FORUM, icon_color="white", color="white", bgcolor=CORES['roxo_accent'], height=30, style=ft.ButtonStyle(padding=10, shape=ft.RoundedRectangleBorder(radius=8)), on_click=lambda e, a=aluno: abrir_registro_conversa(a))),
                    ]
                )
            )
        page.update()

    # --- LAYOUT ---
    def mudar_rota(e):
        rotas = ["/dashboard", "/workdesk", "/classes", "/frequency", "/incubator", "/settings"]
        page.go(rotas[e.control.selected_index])

    sidebar = Sidebar(on_change_page=mudar_rota, selected_index=3)

    content = ft.Row([
        sidebar,
        ft.Container(
            expand=True, bgcolor="#F3F4F6", padding=35,
            content=ft.Column([
                ft.Text("Controle de Frequência", size=24, weight="bold", color="#31144A"),
                ft.Text("Acompanhe a assiduidade dos alunos matriculados", size=13, color="#6B7280"),
                ft.Container(height=20),
                ft.Container(
                    bgcolor="white", border_radius=12, padding=20, expand=True,
                    content=ft.Column([tabela], scroll=ft.ScrollMode.AUTO)
                )
            ])
        )
    ], expand=True, spacing=0)

    carregar_dados()
    return ft.View("/frequency", [content], padding=0, bgcolor=CORES['fundo'])