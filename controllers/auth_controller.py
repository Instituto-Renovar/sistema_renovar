from config.firebase_config import get_db
import random
import string
from core.email_service import EmailService

class AuthController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("usuarios")
        self.email_service = EmailService()

    def login(self, email, senha):
        """Verifica se email e senha batem no banco"""
        # Busca usuário pelo email
        docs = self.collection.where("email", "==", email).stream()
        
        for doc in docs:
            dados = doc.to_dict()
            if dados.get('senha') == senha:
                # Login Sucesso! Retorna os dados do usuário (para saber se é Adm ou Prof)
                dados['id'] = doc.id
                return True, dados
        
        return False, None

    def recuperar_senha(self, email):
        """Gera nova senha e envia por email"""
        # 1. Verifica se usuario existe
        docs = self.collection.where("email", "==", email).stream()
        usuario_ref = None
        
        for doc in docs:
            usuario_ref = doc.reference
            break
            
        if not usuario_ref:
            return False, "E-mail não encontrado no sistema."

        # 2. Gera senha aleatória
        nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # 3. Atualiza no Banco
        usuario_ref.update({"senha": nova_senha})
        
        # 4. Envia E-mail (Se configurado)
        # Se não tiver configurado o email_service ainda, ele vai dar erro, então tratamos aqui
        if "seu_email" in self.email_service.remetente:
            return True, f"Modo Teste: Sua nova senha é {nova_senha} (Configure o SMTP para enviar por email)"
            
        sucesso, msg = self.email_service.enviar_recuperacao(email, nova_senha)
        return sucesso, msg