import datetime
from config.firebase_config import get_db
from google.cloud.firestore import FieldFilter

class ClassController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("turmas")
        self.leads_collection = self.db.collection("leads")
        self.chamadas_collection = self.db.collection("chamadas")

    # --- GESTÃO DE TURMAS ---
    def criar_turma(self, dados):
        doc_ref = self.collection.document()
        if 'status' not in dados: dados['status'] = "Aberta"
        dados['created_at'] = datetime.datetime.now()
        doc_ref.set(dados)
        return doc_ref.id

    def atualizar_turma(self, doc_id, dados):
        self.collection.document(doc_id).update(dados)

    def deletar_turma(self, doc_id):
        self.collection.document(doc_id).delete()

    def buscar_turmas(self, apenas_ativas=True):
        docs = self.collection.stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            if apenas_ativas:
                if d.get('status') == "Aberta" or d.get('ativa') is True:
                    lista.append(d)
            else:
                lista.append(d)
        return lista

    # --- ÁREA DO PROFESSOR ---
    def buscar_turmas_do_professor(self, nome_professor):
        # Busca exata pelo nome do professor
        docs = self.collection.where(filter=FieldFilter("professor", "==", nome_professor)).stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            if d.get('status') == "Aberta" or d.get('ativa') is True:
                lista.append(d)
        return lista

    def salvar_chamada(self, dados_chamada):
        try:
            doc_ref = self.chamadas_collection.document()
            dados_chamada['created_at'] = datetime.datetime.now()
            
            # --- CORREÇÃO CRÍTICA ---
            # O Firebase não aceita 'set', só aceita 'list'. Convertemos aqui para garantir.
            if 'presentes' in dados_chamada:
                dados_chamada['presentes'] = list(dados_chamada['presentes'])
                
            doc_ref.set(dados_chamada)
            return True, "Sucesso"
        except Exception as e:
            # Retorna o erro exato para sabermos o que houve
            return False, str(e)

    # --- GESTÃO DE ALUNOS ---
    def buscar_alunos_da_turma(self, nome_turma_completo):
        docs = self.leads_collection.where(filter=FieldFilter("turma_vinculada", "==", nome_turma_completo)).stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            lista.append(d)
        return lista

    def contar_alunos(self, nome_turma_completo):
        lista = self.buscar_alunos_da_turma(nome_turma_completo)
        return len(lista)

    # --- CÁLCULO DE FREQUÊNCIA ---
    def calcular_frequencia_aluno(self, aluno_id, nome_turma_completo):
        # Busca todas as chamadas onde o nome da turma bate
        docs = self.chamadas_collection.where(filter=FieldFilter("nome_turma", "==", nome_turma_completo)).stream()
        
        total_aulas = 0
        presencas = 0
        
        for doc in docs:
            aula = doc.to_dict()
            total_aulas += 1
            lista_presentes = aula.get('presentes', [])
            # Verifica se o ID do aluno está na lista de presentes (agora convertida corretamente)
            if aluno_id in lista_presentes:
                presencas += 1
        
        # Se não tiver aulas registradas, retorna None para a tela saber
        if total_aulas == 0:
            return None
            
        percentual = int((presencas / total_aulas) * 100)
        faltas = total_aulas - presencas
        
        return {'percentual': percentual, 'faltas': faltas, 'total_aulas': total_aulas}