import firebase_admin
from firebase_admin import firestore

class ScheduleController:
    def __init__(self):
        # Correção: Conecta direto ao Firestore
        self.db = firestore.client()
        self.collection = self.db.collection("aulas")

    def criar_aula(self, dados):
        """
        dados = {
            "turma_id": "ID_DA_TURMA",
            "data": "2026-01-20",
            "conteudo": "Corte Masculino Degradê",
            "realizada": False,
            "presencas": [] # Lista de IDs de alunos
        }
        """
        try:
            doc_ref = self.collection.add(dados)
            return doc_ref[1].id
        except Exception as e:
            print(f"Erro ao criar aula: {e}")
            return None

    def buscar_aulas_por_turma(self, turma_id):
        try:
            # Busca aulas ordenadas por data
            docs = self.collection.where("turma_id", "==", turma_id).stream()
            aulas = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                aulas.append(d)
            
            # Ordenação manual por data (String YYYY-MM-DD funciona bem)
            aulas.sort(key=lambda x: x.get('data', ''))
            return aulas
        except Exception as e:
            print(f"Erro ao buscar aulas: {e}")
            return []

    def excluir_aula(self, aula_id):
        try:
            self.collection.document(aula_id).delete()
            return True
        except Exception as e:
            print(f"Erro ao excluir aula: {e}")
            return False