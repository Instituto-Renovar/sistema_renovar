import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # --- CONFIGURAÇÃO DO SEU E-MAIL AQUI ---
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.remetente = "seu_email@gmail.com" # <--- COLOQUE SEU EMAIL
        self.senha = "sua_senha_de_aplicativo" # <--- COLOQUE SUA SENHA DE APP (Não a do email normal)

    def enviar_recuperacao(self, destinatario, nova_senha):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.remetente
            msg['To'] = destinatario
            msg['Subject'] = "Instituto Renovar - Recuperação de Senha"

            corpo = f"""
            Olá,
            
            Recebemos uma solicitação para redefinir sua senha.
            
            Sua NOVA senha provisória é: {nova_senha}
            
            Por favor, acesse o sistema e altere sua senha assim que possível.
            
            Atenciosamente,
            Equipe Instituto Renovar
            """
            
            msg.attach(MIMEText(corpo, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.remetente, self.senha)
            text = msg.as_string()
            server.sendmail(self.remetente, destinatario, text)
            server.quit()
            return True, "E-mail enviado com sucesso!"
        except Exception as e:
            return False, f"Erro ao enviar e-mail: {str(e)}"