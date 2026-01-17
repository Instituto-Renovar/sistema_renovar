import firebase_admin
from firebase_admin import firestore
from datetime import datetime

class CalendarController:
    def __init__(self):
        # Correção: Conecta direto ao Firestore
        self.db = firestore.client()
        self.collection = self.db.collection("calendario_escolar")

    def adicionar_evento(self, data_iso, descricao):
        """
        data_iso: string "YYYY-MM-DD"
        descricao: string "Feriado Nacional"
        """
        try:
            # Usa a própria data como ID para evitar duplicidade no mesmo dia
            self.collection.document(data_iso).set({
                "data": data_iso,
                "descricao": descricao
            })
            return True
        except Exception as e:
            print(f"Erro ao salvar evento: {e}")
            return False

    def remover_evento(self, data_iso):
        try:
            self.collection.document(data_iso).delete()
            return True
        except Exception as e:
            print(f"Erro ao remover evento: {e}")
            return False

    def buscar_feriados(self):
        """Retorna lista de datas bloqueadas ordenadas"""
        try:
            docs = self.collection.stream()
            feriados = []
            for doc in docs:
                feriados.append(doc.to_dict())
            
            # Ordena por data
            feriados.sort(key=lambda x: x.get('data'))
            return feriados
        except Exception as e:
            print(f"Erro ao buscar feriados: {e}")
            return []
            
    def verificar_feriado(self, data_iso):
        """Retorna a descrição se for feriado, ou None se for dia letivo"""
        try:
            doc = self.collection.document(data_iso).get()
            if doc.exists:
                return doc.to_dict().get('descricao')
            return None
        except:
            return None