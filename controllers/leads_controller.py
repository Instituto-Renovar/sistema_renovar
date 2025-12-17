import datetime
from config.firebase_config import get_db

class LeadsController:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("leads")

    def verificar_telefone_existe(self, telefone):
        """Verifica duplicidade (Sintaxe corrigida para evitar warning)"""
        # A correção do aviso do terminal está aqui: usamos field_path, op_string e value nomeados
        docs = self.collection.where(field_path="telefone", op_string="==", value=telefone).stream()
        return any(docs)

    def criar_lead(self, dados):
        doc_ref = self.collection.document()
        dados['created_at'] = datetime.datetime.now()
        dados['status'] = dados.get('status', 'Novo')
        doc_ref.set(dados)
        return doc_ref.id

    def atualizar_lead(self, doc_id, dados_atualizados):
        self.collection.document(doc_id).update(dados_atualizados)

    def buscar_leads(self, filtro_status=None, apenas_cabeleireiras=False):
        docs = self.collection.stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            
            if apenas_cabeleireiras:
                if d.get('is_cabeleireira') is True:
                    lista.append(d)
                continue

            if filtro_status:
                if isinstance(filtro_status, list):
                    if d.get('status') in filtro_status:
                        lista.append(d)
                elif d.get('status') == filtro_status:
                    lista.append(d)
            else:
                lista.append(d)
        return lista

    def contar_atrasados(self):
        """Conta leads com retorno PASSADO e ativos"""
        leads_ativos = self.buscar_leads(filtro_status=['Novo', 'Em Negociação', 'Em Contato', 'Interessado'])
        contador = 0
        agora = datetime.datetime.now()
        
        for lead in leads_ativos:
            data_str = lead.get('data_retorno')
            if data_str:
                try:
                    # Tenta converter string para data
                    data_retorno = datetime.datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                    if data_retorno < agora:
                        contador += 1
                except ValueError:
                    pass
        return contador