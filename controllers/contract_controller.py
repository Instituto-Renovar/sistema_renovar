import os
import datetime
from docxtpl import DocxTemplate
import platform

# Tenta importar bibliotecas do Windows. Se falhar (Web/Linux), segue a vida.
try:
    from docx2pdf import convert
    import pythoncom
    MODO_DESKTOP = True
except ImportError:
    MODO_DESKTOP = False

class ContractController:
    def gerar_contrato(self, dados_aluno):
        # 1. Localiza o modelo
        caminho_modelo = os.path.join("assets", "contrato_modelo.docx")
        if not os.path.exists(caminho_modelo):
            caminho_modelo = "contrato_modelo.docx"
            if not os.path.exists(caminho_modelo):
                return "ERRO: Modelo não encontrado!"

        try:
            doc = DocxTemplate(caminho_modelo)
            
            # 2. Prepara os dados
            def v(chave):
                valor = dados_aluno.get(chave)
                return str(valor).upper() if valor else "________________"

            contexto = {
                'nome_aluno': v('nome'), 'cpf': v('cpf'), 'rg': v('rg'), 'orgao_exp': v('orgao_exp'),
                'nascimento': v('nascimento'), 'sexo': v('sexo'), 'estado_civil': v('estado_civil'),
                'nome_mae': v('nome_mae'), 'nome_pai': v('nome_pai'), 'naturalidade': v('naturalidade'),
                'profissao': v('profissao'), 'endereco': v('endereco'), 'bairro': v('bairro'),
                'cidade': v('cidade'), 'uf': v('uf'), 'cep': v('cep'), 'telefone': v('telefone'),
                'email': str(dados_aluno.get('email', '')).lower(),
                'nome_curso': v('nome_curso'), 'turno': v('turno'), 'data_inicio': v('data_inicio'),
                'valor_mensal': v('valor_mensal'), 'valor_total': v('valor_total'),
                'forma_pagamento': v('forma_pagamento'),
                'data_hoje': datetime.date.today().strftime('%d/%m/%Y'),
                'ano_atual': datetime.date.today().year
            }

            doc.render(contexto)

            # 3. Define onde salvar
            # Na Web, não temos acesso a "C:/Users/Downloads". Salvamos na pasta local temporária.
            nome_arquivo = f"Contrato_{dados_aluno.get('nome', 'Aluno').strip().replace(' ', '_')}"
            
            # Se for Web, salvamos apenas na raiz para o Flet oferecer download (futuro)
            # Por enquanto, salvamos localmente
            caminho_docx = f"{nome_arquivo}.docx"
            doc.save(caminho_docx)

            # 4. Decisão: Gera PDF ou só DOCX?
            if MODO_DESKTOP and platform.system() == "Windows":
                try:
                    # Lógica exclusiva para Windows/PC com Word instalado
                    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                    caminho_final_docx = os.path.join(pasta_downloads, f"{nome_arquivo}.docx")
                    caminho_final_pdf = os.path.join(pasta_downloads, f"{nome_arquivo}.pdf")
                    
                    doc.save(caminho_final_docx) # Salva no Downloads
                    
                    pythoncom.CoInitialize()
                    convert(caminho_final_docx, caminho_final_pdf)
                    os.remove(caminho_final_docx) # Limpa o docx
                    os.startfile(caminho_final_pdf) # Abre o PDF
                    return "Sucesso! PDF gerado e aberto."
                except Exception as e:
                    return f"Aviso: Contrato gerado em DOCX (Erro PDF: {e})"
            else:
                # MODO WEB (HostGator/Linux)
                # Na web estática, não conseguimos abrir o arquivo direto no PC do usuário assim.
                # O ideal seria implementar um botão de Download, mas para não complicar agora:
                # Ele vai salvar o DOCX na pasta do site.
                return f"Contrato DOCX gerado: {nome_arquivo}.docx"

        except Exception as e:
            return f"Erro ao gerar contrato: {str(e)}"