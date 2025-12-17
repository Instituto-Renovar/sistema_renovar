from config.firebase_config import get_db

class CourseController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("cursos")

    def criar_curso(self, dados):
        doc_ref = self.collection.document()
        dados['ativo'] = True
        doc_ref.set(dados)
        return doc_ref.id

    def atualizar_curso(self, doc_id, dados):
        self.collection.document(doc_id).update(dados)

    def deletar_curso(self, doc_id):
        self.collection.document(doc_id).delete()

    def buscar_cursos(self, apenas_nomes=False):
        docs = self.collection.stream()
        if apenas_nomes:
            return [doc.to_dict().get('nome') for doc in docs]
        
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            lista.append(d)
        return lista