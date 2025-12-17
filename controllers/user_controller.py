from config.firebase_config import get_db
import datetime

class UserController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("usuarios")

    def criar_usuario(self, dados):
        doc_ref = self.collection.document()
        dados['created_at'] = datetime.datetime.now()
        dados['ativo'] = True
        doc_ref.set(dados)
        return doc_ref.id

    def atualizar_usuario(self, doc_id, dados):
        self.collection.document(doc_id).update(dados)

    def buscar_usuarios(self):
        docs = self.collection.stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            lista.append(d)
        return lista

    def buscar_professores_nomes(self):
        """Retorna uma lista apenas com os nomes dos usuários que são Professores"""
        # Filtra onde a chave 'funcao' é igual a 'Professor'
        docs = self.collection.where("funcao", "==", "Professor").stream()
        return [doc.to_dict().get('nome') for doc in docs]

    def deletar_usuario(self, doc_id):
        self.collection.document(doc_id).delete()