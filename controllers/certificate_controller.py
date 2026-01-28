import os
import datetime
import tempfile
from docxtpl import DocxTemplate
import platform

# Tenta importar bibliotecas de conversão PDF (Só Windows)
try:
    from docx2pdf import convert
    import pythoncom
    MODO_DESKTOP = True
except ImportError:
    MODO_DESKTOP = False

class CertificateController:
    def __init__(self):
        # Pasta onde ficam os modelos .docx
        self.template_path = os.path.join("assets", "templates")

    def gerar_certificado(self, dados_aluno, dados_turma, notas, frequencia, conteudo_programatico):
        """
        Gera certificado baseado no template Word.
        Recebe: dados_aluno (dict), dados_turma (dict), notas (dict), frequencia (str/int), conteudo (list)
        """
        # 1. Seleção do Modelo (Lógica por curso)
        nome_curso = dados_turma.get('curso', '').lower()
        
        # Defina seus arquivos aqui. Ex:
        if "cabeleireiro" in nome_curso:
            nome_modelo = "modelo_cabeleireiro.docx"
        elif "sobrancelha" in nome_curso:
            nome_modelo = "modelo_sobrancelha.docx"
        else:
            nome_modelo = "modelo_generico.docx"

        caminho_modelo = os.path.join(self.template_path, nome_modelo)

        # Fallback de segurança se não achar o específico
        if not os.path.exists(caminho_modelo):
            return None, f"Erro: Modelo '{nome_modelo}' não encontrado em assets/templates!"

        try:
            doc = DocxTemplate(caminho_modelo)

            # 2. Prepara os dados para o Word (As tags {{ }})
            contexto = {
                'nome_aluno': dados_aluno.get('nome', 'Aluno').upper(),
                'cpf': dados_aluno.get('cpf', ''),
                'curso': dados_turma.get('curso', '').upper(),
                'carga_horaria': dados_turma.get('carga_horaria', 'XX'),
                'data_conclusao': datetime.date.today().strftime("%d/%m/%Y"),
                'cidade_data': f"Aracaju/SE, {datetime.date.today().strftime('%d de %B de %Y')}",
                
                # Notas e Frequência
                'media_geral': str(notas.get('media_final', '--')),
                'nota_teorica': str(notas.get('teorica', '--')),
                'nota_pratica': str(notas.get('pratica', '--')),
                'frequencia': str(frequencia), # Ex: "95%"
                
                # Conteúdo Programático (Lista para o Word)
                # Se não tiver conteudo, coloca um padrão
                'conteudo': conteudo_programatico if conteudo_programatico else ["Módulo 1: Introdução", "Módulo 2: Técnicas", "Módulo 3: Prática"]
            }

            doc.render(contexto)

            # 3. Salva DOCX Temporário
            nome_limpo = dados_aluno.get('nome', 'certificado').replace(" ", "_")
            nome_arquivo = f"Certificado_{nome_limpo}"
            temp_dir = tempfile.gettempdir()
            caminho_docx = os.path.join(temp_dir, f"{nome_arquivo}.docx")
            doc.save(caminho_docx)

            # 4. Tenta Gerar PDF (Se for Windows Desktop)
            if MODO_DESKTOP and platform.system() == "Windows":
                try:
                    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                    caminho_pdf = os.path.join(pasta_downloads, f"{nome_arquivo}.pdf")
                    
                    pythoncom.CoInitialize()
                    convert(caminho_docx, caminho_pdf)
                    os.startfile(caminho_pdf) # Abre o PDF na tela
                    return caminho_pdf, "Sucesso! PDF Gerado."
                except Exception as e:
                    return caminho_docx, f"Aviso: Gerado apenas DOCX ({e})"
            else:
                return caminho_docx, "Certificado DOCX gerado."

        except Exception as e:
            return None, f"Erro crítico: {str(e)}"