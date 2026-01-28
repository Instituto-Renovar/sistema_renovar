import os
import datetime
import tempfile # <--- Importante para não sujar a raiz
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
        # Procura na pasta assets/templates (padrão que definimos)
        caminho_modelo = os.path.join("assets", "templates", "contrato_modelo.docx")
        
        # Fallback para raiz ou assets direto caso tenha movido
        if not os.path.exists(caminho_modelo):
            caminho_modelo = os.path.join("assets", "contrato_modelo.docx")
            if not os.path.exists(caminho_modelo):
                # Retorna None no caminho para indicar erro
                return None, "ERRO: Modelo 'contrato_modelo.docx' não encontrado em assets/templates!"

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

            # 3. Define onde salvar (Pasta Temporária Segura)
            nome_limpo = dados_aluno.get('nome', 'Aluno').strip().replace(' ', '_')
            nome_arquivo = f"Contrato_{nome_limpo}"
            
            # Usa diretório temporário do sistema (funciona no Render e Local)
            temp_dir = tempfile.gettempdir()
            
            # Caminho completo do DOCX
            caminho_docx = os.path.join(temp_dir, f"{nome_arquivo}.docx")
            
            # Salva o DOCX
            doc.save(caminho_docx)

            # 4. Decisão: Gera PDF ou só DOCX?
            if MODO_DESKTOP and platform.system() == "Windows":
                try:
                    # Lógica exclusiva para Windows/PC com Word instalado
                    # Tenta salvar na pasta Downloads do usuário local
                    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                    caminho_final_pdf = os.path.join(pasta_downloads, f"{nome_arquivo}.pdf")
                    
                    # Converte usando o arquivo temporário como fonte
                    pythoncom.CoInitialize()
                    convert(caminho_docx, caminho_final_pdf)
                    
                    # Abre o PDF gerado
                    os.startfile(caminho_final_pdf)
                    
                    # Retorna o caminho do PDF para o front-end saber
                    return caminho_final_pdf, "Sucesso! PDF gerado e aberto."
                except Exception as e:
                    # Se falhar a conversão (ex: Word não ativado), retorna o DOCX
                    return caminho_docx, f"Aviso: Contrato gerado em DOCX (Erro PDF: {e})"
            else:
                # MODO WEB (Render/Linux) -> Retorna o caminho do DOCX temporário
                # O front-end (View) vai pegar esse caminho e oferecer o download
                return caminho_docx, "Contrato DOCX gerado com sucesso."

        except Exception as e:
            return None, f"Erro crítico ao gerar contrato: {str(e)}"