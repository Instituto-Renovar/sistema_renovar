import datetime
from config.firebase_config import get_db
from google.cloud.firestore import FieldFilter

class ScheduleController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("aulas")

    def criar_aula(self, dados):
        """
        Cria uma aula no cronograma.
        dados = { 'turma_id': '...', 'data': 'YYYY-MM-DD', 'conteudo': '...', 'modulo': '...' }
        """
        try:
            # Verifica duplicidade (mesma turma, mesma data)
            query = self.collection.where(filter=FieldFilter("turma_id", "==", dados['turma_id'])) \
                                   .where(filter=FieldFilter("data", "==", dados['data'])) \
                                   .get()
            
            if len(query) > 0:
                # Se já existe, atualiza em vez de criar duplicado
                doc_id = query[0].id
                self.collection.document(doc_id).update(dados)
                return True, "Aula atualizada."
            
            self.collection.add(dados)
            return True, "Aula criada."
        except Exception as e:
            print(f"Erro criar aula: {e}")
            return False, str(e)

    def buscar_aulas_por_turma(self, turma_id):
        try:
            # CORREÇÃO: Usando FieldFilter
            query = self.collection.where(filter=FieldFilter("turma_id", "==", turma_id))
            docs = query.stream()
            
            lista = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                lista.append(d)
            
            # Ordena por data
            lista.sort(key=lambda x: x.get('data', ''))
            return lista
        except Exception as e:
            print(f"Erro buscar aulas: {e}")
            return []

    def atualizar_status_aula(self, aula_id, realizada=True):
        try:
            self.collection.document(aula_id).update({"realizada": realizada})
            return True
        except:
            return False

    def excluir_aula(self, aula_id):
        try:
            self.collection.document(aula_id).delete()
            return True
        except: return False