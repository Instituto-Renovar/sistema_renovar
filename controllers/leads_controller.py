import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter # Importante para o filtro funcionar
from datetime import datetime

class LeadsController:
    def __init__(self):
        # Garante que o Firestore está conectado
        try:
            self.db = firestore.client()
        except:
            print("Erro de conexão no Controller (Verifique o firebase_config)")

    def criar_lead(self, dados):
        """Cria um novo lead com timestamp automático"""
        try:
            dados['criado_em'] = datetime.now()
            self.db.collection('leads').add(dados)
            return True
        except Exception as e:
            print(f"Erro ao criar lead: {e}")
            return False

    def atualizar_lead(self, id_lead, dados):
        """Atualiza os dados de um lead existente"""
        try:
            dados['atualizado_em'] = datetime.now()
            self.db.collection('leads').document(id_lead).update(dados)
            return True
        except Exception as e:
            print(f"Erro ao atualizar lead: {e}")
            return False

    def deletar_lead(self, id_lead):
        """Remove permanentemente um lead do banco de dados"""
        try:
            self.db.collection('leads').document(id_lead).delete()
            print(f"Lead {id_lead} deletado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao deletar lead: {e}")
            return False

    # Altere a definição para aceitar 'limite'
    def buscar_leads(self, filtro_status=None): # <--- Adicione limite=50
        """
        Busca leads no Firestore.
        Aceita uma lista de status para filtrar e um limite de documentos.
        """
        try:
            leads_ref = self.db.collection('leads')
            
            if filtro_status:
                query = leads_ref.where(filter=FieldFilter('status', 'in', filtro_status))
            else:
                query = leads_ref
                        
            docs = query.stream()

            lista_leads = []
            for doc in docs:
                lead = doc.to_dict()
                lead['id'] = doc.id
                lista_leads.append(lead)
            
            return lista_leads
        except Exception as e:
            print(f"Erro ao buscar leads: {e}")
            return []

    def contar_atrasados(self):
        """
        Conta quantos leads ATIVOS estão com a data de retorno atrasada.
        OTIMIZADO: Busca apenas 'Novo' e 'Em Contato' para economizar leituras.
        """
        try:
            agora = datetime.now()
            
            # --- CORREÇÃO CRÍTICA DE PERFORMANCE ---
            # Antes: Baixava o banco todo.
            # Agora: Baixa apenas os leads que importam (Funil Ativo).
            # Ignoramos Matriculados e Desistentes direto na fonte.
            status_ativos = ['Novo', 'Em Contato']
            leads = self.buscar_leads(filtro_status=status_ativos) 
            
            contador = 0
            for lead in leads:
                data_str = lead.get('data_retorno')
                
                # A validação de status aqui ficou redundante (já filtramos no banco), 
                # mas mantemos por segurança caso mude a lógica.
                
                if data_str:
                    try:
                        data_retorno = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                        if data_retorno < agora:
                            contador += 1
                    except:
                        pass
            return contador
        except Exception as e:
            print(f"Erro ao contar atrasados: {e}")
            return 0