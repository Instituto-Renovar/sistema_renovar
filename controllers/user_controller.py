import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

class UserController:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("usuarios")

    def criar_usuario(self, dados):
        try:
            if self.buscar_por_email(dados['email']):
                return False, "Email já cadastrado!"
            
            self.collection.add(dados)
            return True, "Usuário criado com sucesso!"
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False, f"Erro: {e}"

    def buscar_por_email(self, email):
        """
        Versão corrigida e mais robusta usando .get() em vez de .stream()
        """
        try:
            print(f"--- INICIO BUSCA: {email} ---")
            
            # Tenta buscar usando o filtro moderno
            # O .get() traz a lista completa de uma vez, evitando travamentos de stream
            query = self.collection.where(filter=FieldFilter("email", "==", email))
            docs = query.get() 
            
            print(f"--- BANCO RESPONDEU. ENCONTRADOS: {len(docs)} ---")

            if not docs:
                print("❌ Nenhum documento retornado na lista.")
                return None

            for doc in docs:
                dados = doc.to_dict()
                dados['id'] = doc.id
                print(f"✅ Usuário identificado: {dados.get('nome')}")
                return dados
            
            return None

        except Exception as e:
            print(f"🔥 ERRO NO CONTROLLER: {e}")
            return None

    def buscar_usuarios(self):
        try:
            # Aqui mantemos stream ou get, mas get é mais seguro para listas pequenas
            docs = self.collection.get()
            lista = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                lista.append(d)
            return lista
        except Exception as e:
            print(f"Erro listar usuários: {e}")
            return []

    def atualizar_usuario(self, user_id, dados):
        try:
            self.collection.document(user_id).update(dados)
            return True
        except Exception as e:
            print(f"Erro update user: {e}")
            return False

    def deletar_usuario(self, user_id):
        try:
            self.collection.document(user_id).delete()
            return True
        except: return False

    def buscar_professores_nomes(self):
        """Retorna lista apenas de quem é marcado como Professor"""
        try:
            # Busca filtrada no banco (Mais eficiente e correto)
            # Traz quem tem funcao == 'Professor'
            query = self.collection.where(filter=FieldFilter("funcao", "==", "Professor"))
            docs = query.get()
            
            profs = [doc.to_dict()['nome'] for doc in docs]
            
            # Opcional: Se quiser incluir Admins na lista também, descomente abaixo:
            # query_adm = self.collection.where(filter=FieldFilter("funcao", "==", "Administrador")).get()
            # profs.extend([doc.to_dict()['nome'] for doc in query_adm])
            
            return sorted(profs) # Retorna em ordem alfabética
        except Exception as e:
            print(f"Erro ao buscar professores: {e}")
            return []