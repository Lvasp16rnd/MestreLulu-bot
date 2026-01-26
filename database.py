"""
Database usando MongoDB Atlas para persistência na nuvem.
Com cache local para performance.
"""
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# Conexão com timeout e pool de conexões
client = MongoClient(
    MONGO_URI, 
    serverSelectionTimeoutMS=5000, 
    connectTimeoutMS=5000,
    maxPoolSize=10
)
db = client["MestreLuLu"]

# Collections
usuarios_col = db["usuarios"]
config_col = db["config"]

# === CACHE LOCAL ===
_cache_usuarios = {}
_cache_config = None
_cache_timestamp = 0
CACHE_TTL = 60  # Segundos para expirar o cache

def _cache_expirado():
    return time.time() - _cache_timestamp > CACHE_TTL

def invalidar_cache():
    """Força atualização do cache na próxima leitura."""
    global _cache_timestamp
    _cache_timestamp = 0

def carregar_usuario(user_id):
    """Carrega um usuário com cache."""
    global _cache_usuarios, _cache_timestamp
    
    user_id = str(user_id)
    
    # Se tem no cache e não expirou, retorna do cache
    if user_id in _cache_usuarios and not _cache_expirado():
        return _cache_usuarios[user_id].copy()
    
    # Busca do MongoDB
    doc = usuarios_col.find_one({"_id": user_id})
    if doc:
        doc.pop("_id", None)
        _cache_usuarios[user_id] = doc
        _cache_timestamp = time.time()
        return doc.copy()
    
    return None

def carregar_dados():
    """Carrega todos os dados do MongoDB (com cache)."""
    global _cache_usuarios, _cache_config, _cache_timestamp
    
    # Se cache ainda válido, monta dos dados cacheados
    if not _cache_expirado() and _cache_config is not None:
        return {
            "usuarios": {k: v.copy() for k, v in _cache_usuarios.items()},
            "itens_globais": _cache_config.get("itens_globais", {}),
            "loja_custom": _cache_config.get("loja_custom", {}),
            "missoes": _cache_config.get("missoes", [])
        }
    
    dados = {
        "usuarios": {},
        "itens_globais": {},
        "loja_custom": {},
        "missoes": []
    }
    
    # Carrega usuários
    for doc in usuarios_col.find():
        user_id = str(doc.pop("_id"))
        dados["usuarios"][user_id] = doc
        _cache_usuarios[user_id] = doc.copy()
    
    # Carrega config
    config = config_col.find_one({"_id": "global"})
    if config:
        config.pop("_id", None)
        _cache_config = config
        dados["itens_globais"] = config.get("itens_globais", {})
        dados["loja_custom"] = config.get("loja_custom", {})
        dados["missoes"] = config.get("missoes", [])
    
    _cache_timestamp = time.time()
    return dados

def salvar_dados(dados):
    """Salva dados no MongoDB e atualiza cache."""
    global _cache_usuarios, _cache_config, _cache_timestamp
    
    # Salva usuários
    for user_id, info in dados["usuarios"].items():
        usuarios_col.update_one(
            {"_id": str(user_id)},
            {"$set": info},
            upsert=True
        )
        _cache_usuarios[str(user_id)] = info.copy()
    
    # Salva config global
    config_data = {
        "itens_globais": dados.get("itens_globais", {}),
        "loja_custom": dados.get("loja_custom", {}),
        "missoes": dados.get("missoes", [])
    }
    config_col.update_one(
        {"_id": "global"},
        {"$set": config_data},
        upsert=True
    )
    _cache_config = config_data
    _cache_timestamp = time.time()

def salvar_usuario(user_id, info):
    """Salva apenas UM usuário - mais rápido!"""
    global _cache_usuarios, _cache_timestamp
    
    user_id = str(user_id)
    usuarios_col.update_one(
        {"_id": user_id},
        {"$set": info},
        upsert=True
    )
    _cache_usuarios[user_id] = info.copy()
    _cache_timestamp = time.time()

def obter_usuario(user_id):
    """Alias para carregar_usuario."""
    return carregar_usuario(user_id)

def atualizar_usuario(user_id, info):
    """Alias para salvar_usuario."""
    salvar_usuario(user_id, info)

def deletar_usuario(user_id):
    """Remove um usuário do banco."""
    usuarios_col.delete_one({"_id": str(user_id)})
