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
        try:
            if apenas_ativas:
                # CORREÇÃO: Usando FieldFilter para evitar aviso no terminal e filtrar no servidor
                query = self.collection.where(filter=FieldFilter("status", "==", "Aberta"))
                docs = query.stream()
            else:
                docs = self.collection.stream()

            lista = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                lista.append(d)
            return lista
        except Exception as e:
            print(f"Erro ao buscar turmas: {e}")
            return []

    # --- ÁREA DO PROFESSOR ---
    def buscar_turmas_do_professor(self, nome_professor):
        # Busca exata pelo nome do professor usando filtro novo
        docs = self.collection.where(filter=FieldFilter("professor", "==", nome_professor)).stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            # Garante que só traga turmas ativas
            if d.get('status') == "Aberta" or d.get('ativa') is True:
                lista.append(d)
        return lista

    # --- GESTÃO INTELIGENTE DE CHAMADAS (ATUALIZADO) ---
    def buscar_chamada_da_aula(self, aula_id):
        """Verifica se já existe uma chamada salva para esta aula específica"""
        try:
            query = self.chamadas_collection.where(filter=FieldFilter("aula_id", "==", aula_id))
            docs = query.get()
            
            for doc in docs:
                return doc.to_dict() 
            return None 
        except:
            return None

    def salvar_chamada(self, dados_chamada):
        """Salva ou Atualiza a chamada no banco (Evita duplicidade)"""
        try:
            aula_id = dados_chamada.get('aula_id')
            if not aula_id: return False, "Erro: Aula sem ID"

            # 1. Verifica se já existe chamada para esta aula
            query = self.chamadas_collection.where(filter=FieldFilter("aula_id", "==", aula_id)).get()
            
            doc_ref = None
            # Se encontrou, pega a referência para atualizar
            for doc in query:
                doc_ref = self.chamadas_collection.document(doc.id)
                break
            
            # Se não encontrou, cria referência nova
            if not doc_ref:
                doc_ref = self.chamadas_collection.document()
            
            # 2. Prepara os dados
            dados_chamada['updated_at'] = datetime.datetime.now()
            
            # Converte 'set' para 'list' (Firebase não aceita set)
            if 'presentes' in dados_chamada:
                dados_chamada['presentes'] = list(dados_chamada['presentes'])
                
            # 3. Salva com merge=True (Atualiza sem apagar outros campos)
            doc_ref.set(dados_chamada, merge=True)
            return True, "Chamada salva com sucesso!"
            
        except Exception as e:
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
        docs = self.chamadas_collection.where(filter=FieldFilter("nome_turma", "==", nome_turma_completo)).stream()
        
        total_aulas = 0
        presencas = 0
        
        for doc in docs:
            aula = doc.to_dict()
            total_aulas += 1
            lista_presentes = aula.get('presentes', [])
            
            if aluno_id in lista_presentes:
                presencas += 1
        
        if total_aulas == 0:
            return None
            
        percentual = int((presencas / total_aulas) * 100)
        faltas = total_aulas - presencas
        
        return {'percentual': percentual, 'faltas': faltas, 'total_aulas': total_aulas}
    
    # --- NOVO: CÁLCULO FINAL DA TURMA ---
    def gerar_boletim_turma(self, turma_id):
        """Calcula médias e frequências de todos os alunos da turma"""
        try:
            # 1. Busca todas as aulas realizadas dessa turma
            aulas_docs = self.chamadas_collection.where(filter=FieldFilter("turma_id", "==", turma_id)).get()
            
            # Se não teve aula, retorna vazio
            if not aulas_docs: return []

            dados_alunos = {} # Vai guardar { 'id_aluno': { 'presencas': 0, 'notas': [], 'nome': '...' } }
            total_aulas = 0
            
            # 2. Varre todas as chamadas somando tudo
            for doc in aulas_docs:
                aula = doc.to_dict()
                total_aulas += 1
                
                # Lista de presentes nesta aula
                presentes = aula.get('presentes', [])
                notas = aula.get('notas', {}) # Dicionário { 'id_aluno': '8.5' }
                
                # Para cada aluno presente, soma +1
                for pid in presentes:
                    if pid not in dados_alunos: dados_alunos[pid] = {'presencas': 0, 'notas': [], 'id': pid}
                    dados_alunos[pid]['presencas'] += 1
                
                # Para cada nota lançada, guarda na lista
                for nid, valor_nota in notas.items():
                    if nid not in dados_alunos: dados_alunos[nid] = {'presencas': 0, 'notas': [], 'id': nid}
                    try:
                        # Converte string "8.5" para float 8.5
                        dados_alunos[nid]['notas'].append(float(str(valor_nota).replace(',', '.')))
                    except: pass

            # 3. Busca nomes dos alunos para montar o relatório final
            # Precisamos buscar os alunos de novo para garantir que quem tem 0 presenças também apareça (opcional)
            # Por simplificação, vamos focar nos que tem registro. 
            # Para pegar o nome, vamos ter que buscar no 'leads' um por um ou ter o nome salvo na chamada (melhoria futura).
            # Por agora, vamos buscar os nomes no banco de leads baseado nos IDs coletados.
            
            relatorio = []
            
            for aid, dados in dados_alunos.items():
                # Busca nome do aluno
                aluno_doc = self.leads_collection.document(aid).get()
                nome_aluno = aluno_doc.to_dict().get('nome', 'Aluno Removido') if aluno_doc.exists else "Desconhecido"
                
                freq_pct = int((dados['presencas'] / total_aulas) * 100) if total_aulas > 0 else 0
                
                media = 0
                if dados['notas']:
                    media = sum(dados['notas']) / len(dados['notas'])
                
                # Regras de Aprovação (Configurável: 60% freq e média 6.0)
                status = "Aprovado"
                if freq_pct < 60: status = "Reprovado (Faltas)"
                elif media < 6.0 and dados['notas']: status = "Reprovado (Nota)" # Só reprova por nota se teve nota
                
                relatorio.append({
                    "nome": nome_aluno,
                    "frequencia": freq_pct,
                    "media": round(media, 1),
                    "status": status,
                    "total_aulas": total_aulas,
                    "presencas": dados['presencas']
                })
            
            return relatorio
            
        except Exception as e:
            print(f"Erro boletim: {e}")
            return []