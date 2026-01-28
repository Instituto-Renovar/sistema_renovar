import flet as ft
from core.colors import CORES
from controllers.class_controller import ClassController
from controllers.certificate_controller import CertificateController # <--- Importamos o Gerador
import datetime
# --- ATENÇÃO: Verifique se o import abaixo está igual ao do seu dashboard_view.py ---
from components.sidebar import Sidebar 

def FrequencyView(page: ft.Page):
    class_ctrl = ClassController()
    cert_ctrl = CertificateController() # <--- Instanciamos o controlador
    
    # --- ESTADOS E VARIÁVEIS ---
    area_conteudo = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    titulo_pagina = ft.Text("Desempenho Escolar", size=24, weight="bold", color="#374151")

    # --- FUNÇÃO 1: MOSTRAR DETALHES DA TURMA (TABELA) ---
    def abrir_detalhes_turma(e, turma):
        # 1. Limpa a tela e mostra carregando
        area_conteudo.controls.clear()
        area_conteudo.controls.append(ft.ProgressBar(color=CORES['ouro']))
        titulo_pagina.value = f"Desempenho: {turma['nome_turma']}"
        page.update()

        # 2. Busca os dados
        dados = class_ctrl.gerar_boletim_turma(turma['id'])
        
        area_conteudo.controls.clear()
        
        # Botão Voltar
        btn_voltar = ft.ElevatedButton(
            "Voltar para Turmas", 
            icon=ft.Icons.ARROW_BACK,
            bgcolor="white", color="#374151",
            on_click=lambda _: carregar_lista_turmas()
        )
        area_conteudo.controls.append(btn_voltar)
        area_conteudo.controls.append(ft.Container(height=10))

        if not dados:
            area_conteudo.controls.append(
                ft.Container(
                    padding=40, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Icon(ft.Icons.SENTIMENT_DISSATISFIED, size=40, color="grey"),
                        ft.Text("Nenhum dado registrado para esta turma ainda.", color="grey")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )
        else:
            # Cabeçalho da Tabela (Agora com Financeiro)
            area_conteudo.controls.append(
                ft.Container(
                    bgcolor=CORES['roxo_brand'], padding=10, border_radius=8,
                    content=ft.Row([
                        ft.Text("Aluno", color="white", weight="bold", expand=True),
                        ft.Text("Presença", color="white", width=70, text_align="center"),
                        ft.Text("Média", color="white", width=60, text_align="center"),
                        ft.Text("Financeiro", color="white", width=100, text_align="center"), # Nova Coluna
                        ft.Text("Situação", color="white", width=100, text_align="center"),
                        ft.Text("Ação", color="white", width=50, text_align="center"), # Coluna da Impressora
                    ])
                )
            )
            
            # Linhas da Tabela
            for aluno in dados:
                cor_status = "green" if aluno['status'] == "Aprovado" else "red"
                bg_status = "#DCFCE7" if aluno['status'] == "Aprovado" else "#FEE2E2"
                
                # --- Lógica do Botão Certificado ---
                btn_cert = ft.Container(width=40) # Espaço vazio se não aprovado
                if aluno['status'] == "Aprovado":
                    def gerar_cert(e, a=aluno):
                        # --- CÓDIGO NOVO (PASSO 4) ---
                        # 1. Dados Temporários (Depois puxamos do banco de notas real)
                        notas_exemplo = {'media_final': '10.0', 'teorica': '10', 'pratica': '10'} 
                        freq_exemplo = "100%" 
                        conteudo_exemplo = ["Módulo 1: Introdução", "Módulo 2: Técnicas", "Módulo 3: Prática"]
                        
                        # 2. Chama a nova função (que aceita o modelo Word)
                        caminho, msg = cert_ctrl.gerar_certificado(
                            dados_aluno=a,           # 'a' é a variável do loop
                            dados_turma=turma,       # 'turma' vem do escopo da view
                            notas=notas_exemplo,
                            frequencia=freq_exemplo,
                            conteudo_programatico=conteudo_exemplo
                        )
                        # -----------------------------

                        if caminho:
                            # Ajuste para abrir o arquivo corretamente
                            import os
                            if caminho.endswith(".pdf"):
                                page.launch_url(f"file:///{caminho}")
                            else:
                                # Se for DOCX, avisa onde salvou (Web/Render)
                                page.snack_bar = ft.SnackBar(ft.Text(f"Certificado DOCX gerado em: {os.path.basename(caminho)}"), bgcolor="green")
                            
                            page.snack_bar = ft.SnackBar(ft.Text(f"Certificado de {a['nome']} gerado!"), bgcolor="green")
                            page.snack_bar.open = True
                            page.update()
                        else:
                             # Caso dê erro (caminho None)
                            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                        if caminho:
                            page.launch_url(f"file:///{caminho}")
                            page.snack_bar = ft.SnackBar(ft.Text(f"Certificado de {a['nome']} gerado!"), bgcolor="green")
                            page.snack_bar.open = True
                            page.update()

                    btn_cert = ft.IconButton(
                        ft.Icons.PRINT, 
                        tooltip="Imprimir Certificado", 
                        icon_color="green",
                        on_click=gerar_cert
                    )

                # --- Placeholder Financeiro (Futura Integração Cora) ---
                # Por enquanto fixo, depois virá do banco de dados
                status_fin = "Verificar" 
                cor_fin = "grey"
                bg_fin = "#F3F4F6"
                
                linha = ft.Container(
                    padding=10, bgcolor="white", border_radius=8, border=ft.border.all(1, "#E5E7EB"),
                    content=ft.Row([
                        ft.Column([
                            ft.Text(aluno['nome'], weight="bold", color="#374151"),
                            ft.Text(f"{aluno['presencas']} aulas presentes", size=10, color="grey")
                        ], expand=True, spacing=2),
                        
                        ft.Text(f"{aluno['frequencia']}%", width=70, text_align="center", weight="bold", color="#374151"),
                        
                        ft.Text(f"{aluno['media']}", width=60, text_align="center", weight="bold", size=14, color="#1E3A8A"),
                        
                        # Coluna Financeira (Placeholder)
                        ft.Container(
                            content=ft.Text(status_fin, color=cor_fin, size=11, weight="bold"),
                            bgcolor=bg_fin, padding=5, border_radius=5, width=100, alignment=ft.alignment.center
                        ),
                        
                        # Coluna Situação
                        ft.Container(
                            content=ft.Text(aluno['status'].split()[0], color=cor_status, size=11, weight="bold"),
                            bgcolor=bg_status, padding=5, border_radius=5, width=100, alignment=ft.alignment.center
                        ),
                        
                        # Coluna Ação (Impressora)
                        ft.Container(content=btn_cert, width=50, alignment=ft.alignment.center)
                    ])
                )
                area_conteudo.controls.append(linha)
        
        page.update()

    # --- FUNÇÃO 2: MOSTRAR LISTA DE TURMAS (CARDS) ---
    def carregar_lista_turmas():
        titulo_pagina.value = "Desempenho Escolar"
        area_conteudo.controls.clear()
        
        turmas = class_ctrl.buscar_turmas(apenas_ativas=True)
        
        grid_turmas = ft.Row(wrap=True, spacing=20, run_spacing=20)
        
        if not turmas:
            area_conteudo.controls.append(ft.Text("Nenhuma turma ativa encontrada.", color="grey"))
        else:
            for t in turmas:
                # Card da Turma
                card = ft.Container(
                    width=300, bgcolor="white", padding=20, border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
                    on_click=lambda e, x=t: abrir_detalhes_turma(e, x), 
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=50, height=50, bgcolor="#F3F4F6", border_radius=12,
                                content=ft.Icon(ft.Icons.CLASS_, color=CORES['roxo_brand'], size=24),
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Text(t.get('nome_turma', 'Turma'), weight="bold", size=16, color="#111827"),
                                ft.Text(t.get('curso', 'Curso'), size=12, color="grey", overflow=ft.TextOverflow.ELLIPSIS)
                            ], spacing=2, expand=True)
                        ]),
                        ft.Divider(height=20, color="transparent"),
                        ft.Row([
                            ft.Icon(ft.Icons.ANALYTICS, size=14, color="grey"),
                            ft.Text("Ver Boletim e Financeiro", size=12, color="grey"),
                            ft.Container(expand=True),
                            ft.Icon(ft.Icons.ARROW_FORWARD, size=16, color=CORES['ouro'])
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ])
                )
                grid_turmas.controls.append(card)
            
            area_conteudo.controls.append(ft.Text("Selecione uma turma para gestão administrativa:", color="grey"))
            area_conteudo.controls.append(ft.Container(height=10))
            area_conteudo.controls.append(grid_turmas)
        
        page.update()

    carregar_lista_turmas()

    return ft.View(
        route="/frequency",
        bgcolor="#F3F4F6",
        padding=0,
        controls=[
            ft.Row([
                # Passamos 'page' e o índice 3 para destacar "Frequência" em dourado
                Sidebar(page, selected_index=3), 
                ft.VerticalDivider(width=1, color="#E5E7EB"),
                ft.Container(
                    expand=True,
                    padding=30,
                    content=ft.Column([
                        titulo_pagina,
                        ft.Divider(),
                        area_conteudo
                    ])
                )
            ], expand=True)
        ]
    )