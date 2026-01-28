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
    
    # --- BOLETIM E CÁLCULOS (VERSÃO OTIMIZADA - BAIXO CONSUMO) ---
    def gerar_boletim_turma(self, turma_id):
        """Calcula médias buscando dados em lote para economizar leituras"""
        try:
            # 1. Busca dados da Turma para saber o nome do vínculo (1 Leitura)
            turma_doc = self.collection.document(turma_id).get()
            if not turma_doc.exists: return []
            t_dados = turma_doc.to_dict()
            # Monta o nome de vínculo ex: "CABELEIREIRO GRAU1 - TURMA 12"
            # Ajuste conforme seu padrão de salvamento no leads
            nome_turma_completo = f"{t_dados.get('curso')} - {t_dados.get('nome_turma')}"

            # 2. Busca TODAS as chamadas desta turma (1 Leitura composta)
            chamadas_docs = self.chamadas_collection.where(filter=FieldFilter("turma_id", "==", turma_id)).get()
            if not chamadas_docs: return []

            # 3. Busca Cronograma ATUAL (1 Leitura composta)
            cronograma_docs = self.db.collection("aulas").where(filter=FieldFilter("turma_id", "==", turma_id)).get()
            ids_aulas_validas = {doc.id for doc in cronograma_docs}
            mapa_aulas = {doc.id: doc.to_dict() for doc in cronograma_docs}

            # 4. (NOVO) Busca TODOS os alunos dessa turma de uma vez (1 Leitura composta)
            # Em vez de buscar um por um no loop, buscamos o lote inteiro
            alunos_query = self.leads_collection.where(filter=FieldFilter("turma_vinculada", "==", nome_turma_completo)).stream()
            mapa_alunos = {doc.id: doc.to_dict().get('nome', 'Desconhecido') for doc in alunos_query}

            dados_alunos = {} 
            total_aulas_validas = 0
            total_provas_realizadas = 0 

            # 5. Processa os dados (Agora tudo em memória, sem ir no banco)
            for doc in chamadas_docs:
                chamada = doc.to_dict()
                aula_id = chamada.get('aula_id')
                
                if aula_id not in ids_aulas_validas: continue 

                total_aulas_validas += 1
                dados_aula = mapa_aulas.get(aula_id)
                nome_aula = str(dados_aula.get('conteudo', '')).lower()
                eh_prova = dados_aula.get('e_prova') is True or any(x in nome_aula for x in ['prova', 'avaliação', 'exame', 'teste'])
                
                if eh_prova: total_provas_realizadas += 1

                presentes = chamada.get('presentes', [])
                notas = chamada.get('notas', {}) 
                
                # Presenças
                for pid in presentes:
                    if pid not in dados_alunos: dados_alunos[pid] = {'presencas': 0, 'soma_notas': 0.0, 'id': pid}
                    dados_alunos[pid]['presencas'] += 1
                
                # Notas
                for nid, valor_nota in notas.items():
                    if nid not in dados_alunos: dados_alunos[nid] = {'presencas': 0, 'soma_notas': 0.0, 'id': nid}
                    try:
                        nota_float = float(str(valor_nota).replace(',', '.'))
                        dados_alunos[nid]['soma_notas'] += nota_float
                    except: pass

            # 6. Monta o relatório final usando o MAPA de alunos (Rápido)
            relatorio = []
            
            for aid, dados in dados_alunos.items():
                # Pega nome da memória (Zero consumo de banco aqui)
                nome_aluno = mapa_alunos.get(aid, "Aluno (Não encontrado no Lead)")
                
                freq_pct = int((dados['presencas'] / total_aulas_validas) * 100) if total_aulas_validas > 0 else 0
                
                media = 0.0
                if total_provas_realizadas > 0:
                    media = dados['soma_notas'] / total_provas_realizadas
                
                status = "Aprovado"
                if freq_pct < 60: status = "Reprovado (Faltas)"
                elif media < 6.0: status = "Reprovado (Nota)"
                
                relatorio.append({
                    "nome": nome_aluno,
                    "frequencia": freq_pct,
                    "media": round(media, 1),
                    "status": status,
                    "total_aulas": total_aulas_validas,
                    "presencas": dados['presencas']
                })
            
            return relatorio
            
        except Exception as e:
            print(f"Erro boletim: {e}")
            return []