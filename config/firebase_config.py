import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

_db_instance = None

def inicializar_firebase():
    """Inicializa a conexão com o Firebase (Singleton)"""
    global _db_instance
    
    # Se já existe uma conexão, não recria
    if firebase_admin._apps:
        if _db_instance is None:
            _db_instance = firestore.client()
        return _db_instance

    # Tenta conectar
    cred_path = "service_account.json"
    
    if not os.path.exists(cred_path):
        print(f"❌ ERRO CRÍTICO: Arquivo '{cred_path}' não encontrado na raiz.")
        sys.exit()

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db_instance = firestore.client()
        print("✅ Firebase Conectado com Sucesso!")
        return _db_instance
    except Exception as e:
        print(f"❌ Erro ao conectar no Firebase: {e}")
        return None

def get_db():
    """Retorna a instância do banco de dados para ser usada nos Controllers"""
    if _db_instance is None:
        return inicializar_firebase()
    return _db_instance