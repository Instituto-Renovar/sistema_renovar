from fpdf import FPDF
import datetime
import os

class CertificateController:
    def gerar_pdf(self, nome_aluno, nome_curso, carga_horaria, data_conclusao):
        try:
            # Configuração do PDF
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            
            # --- Borda Decorativa ---
            pdf.set_line_width(1)
            pdf.set_draw_color(49, 20, 74) # Roxo Brand
            pdf.rect(5, 5, 287, 200)
            
            pdf.set_line_width(0.5)
            pdf.set_draw_color(218, 165, 32) # Dourado
            pdf.rect(8, 8, 281, 194)

            # --- Função Auxiliar para Acentos ---
            # O FPDF padrão usa Latin-1. Isso converte o texto para não dar erro.
            def txt(texto):
                return texto.encode('latin-1', 'replace').decode('latin-1')

            # --- Cabeçalho ---
            pdf.ln(30)
            pdf.set_font("Arial", "B", 36)
            pdf.set_text_color(49, 20, 74)
            pdf.cell(0, 10, txt("CERTIFICADO"), 0, 1, 'C')
            
            pdf.ln(5)
            pdf.set_font("Arial", "I", 14)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, txt("DE CONCLUSÃO DE CURSO"), 0, 1, 'C')

            # --- Corpo do Texto ---
            pdf.ln(20)
            pdf.set_font("Arial", "", 16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, txt("Certificamos que"), 0, 1, 'C')

            pdf.ln(5)
            pdf.set_font("Arial", "B", 24)
            pdf.set_text_color(49, 20, 74)
            # Nome do aluno em maiúsculo e tratado
            pdf.cell(0, 10, txt(nome_aluno.upper()), 0, 1, 'C')
            pdf.line(70, 108, 227, 108)

            pdf.ln(10)
            pdf.set_font("Arial", "", 16)
            pdf.set_text_color(0, 0, 0)
            texto_meio = "concluiu com êxito o curso profissionalizante de"
            pdf.cell(0, 10, txt(texto_meio), 0, 1, 'C')
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 22)
            pdf.set_text_color(218, 165, 32)
            pdf.cell(0, 10, txt(nome_curso.upper()), 0, 1, 'C')

            pdf.ln(10)
            pdf.set_font("Arial", "", 14)
            pdf.set_text_color(50, 50, 50)
            data_fmt = datetime.datetime.strptime(data_conclusao, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            # CORREÇÃO AQUI: Trocamos o '•' (que deu erro) por '-'
            texto_fim = f"Carga Horária: {carga_horaria} horas - Concluído em: {data_fmt}"
            pdf.cell(0, 10, txt(texto_fim), 0, 1, 'C')

            # --- Assinaturas ---
            pdf.ln(35)
            y_ass = pdf.get_y()
            
            # Assinatura 1
            pdf.line(40, y_ass, 110, y_ass)
            pdf.set_xy(40, y_ass + 2)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(70, 5, txt("Francisco Neto"), 0, 1, 'C')
            pdf.set_xy(40, y_ass + 7)
            pdf.set_font("Arial", "", 10)
            pdf.cell(70, 5, txt("Diretor - Instituto Renovar"), 0, 1, 'C')

            # Assinatura 2
            pdf.line(180, y_ass, 250, y_ass)
            pdf.set_xy(180, y_ass + 2)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(70, 5, txt("Coordenação Pedagógica"), 0, 1, 'C')
            
            # --- Salvar ---
            nome_limpo = nome_aluno.replace(' ', '_')
            nome_arquivo = f"Certificado_{nome_limpo}.pdf"
            pdf.output(nome_arquivo)
            
            return os.path.abspath(nome_arquivo)
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return None