import firebase_admin
from firebase_admin import firestore
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

    def buscar_leads(self, filtro_status=None):
        """
        Busca leads no Firestore.
        Aceita uma lista de status para filtrar (ex: ['Novo', 'Em Contato'])
        """
        try:
            leads_ref = self.db.collection('leads')
            
            # Se tiver filtro, aplica. Se não, traz tudo.
            if filtro_status:
                # O Firestore limita o 'in' a 10 itens, mas para CRM serve bem
                query = leads_ref.where(filter=firestore.FieldFilter('status', 'in', filtro_status))
                docs = query.stream()
            else:
                docs = leads_ref.stream()

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
        Conta quantos leads estão com a data de retorno atrasada.
        Regra: Status não é 'Finalizado' (ou equivalente) E data_retorno < agora
        """
        try:
            agora = datetime.now()
            # Pega todos os leads que não estão finalizados/desistentes para checar a data
            # Nota: Fazer isso no código (Python) é mais flexível que criar índices complexos no Firestore agora
            leads = self.buscar_leads() 
            
            contador = 0
            for lead in leads:
                data_str = lead.get('data_retorno')
                status = lead.get('status', '')
                
                # Ignora leads que já "morreram" ou viraram alunos
                if status in ['Matriculado', 'Desistente', 'Incubadora']:
                    continue

                if data_str:
                    try:
                        data_retorno = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                        if data_retorno < agora:
                            contador += 1
                    except:
                        # Se a data estiver em formato errado, ignora
                        pass
            return contador
        except Exception as e:
            print(f"Erro ao contar atrasados: {e}")
            return 0