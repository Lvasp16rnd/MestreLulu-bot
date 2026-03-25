"""
Database usando MongoDB Atlas para persistência na nuvem.
MULTI-GUILD: Cada servidor Discord tem seu próprio banco de dados separado.
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

# ID do servidor "Elandor" original (dados legados)
# Após a primeira execução, você pode definir isso como variável de ambiente
ELANDOR_GUILD_ID = os.getenv("ELANDOR_GUILD_ID", None)

# === CACHE LOCAL POR GUILD ===
# Estrutura: {guild_id: {"usuarios": {}, "config": {}, "timestamp": 0}}
_cache_guilds = {}
CACHE_TTL = 60  # Segundos para expirar o cache

def _get_collections(guild_id):
    """Retorna as collections específicas de um servidor."""
    guild_id = str(guild_id)
    usuarios_col = db[f"guild_{guild_id}_usuarios"]
    config_col = db[f"guild_{guild_id}_config"]
    return usuarios_col, config_col

def _cache_expirado(guild_id):
    """Verifica se o cache de uma guild expirou."""
    guild_id = str(guild_id)
    if guild_id not in _cache_guilds:
        return True
    return time.time() - _cache_guilds[guild_id].get("timestamp", 0) > CACHE_TTL

def _init_guild_cache(guild_id):
    """Inicializa o cache de uma guild se não existir."""
    guild_id = str(guild_id)
    if guild_id not in _cache_guilds:
        _cache_guilds[guild_id] = {
            "usuarios": {},
            "config": None,
            "timestamp": 0
        }

def invalidar_cache(guild_id=None):
    """Força atualização do cache na próxima leitura."""
    if guild_id:
        guild_id = str(guild_id)
        if guild_id in _cache_guilds:
            _cache_guilds[guild_id]["timestamp"] = 0
    else:
        # Invalida todos os caches
        for gid in _cache_guilds:
            _cache_guilds[gid]["timestamp"] = 0

def carregar_usuario(guild_id, user_id):
    """Carrega um usuário de um servidor específico com cache."""
    guild_id = str(guild_id)
    user_id = str(user_id)
    
    _init_guild_cache(guild_id)
    cache = _cache_guilds[guild_id]
    
    # Se tem no cache e não expirou, retorna do cache
    if user_id in cache["usuarios"] and not _cache_expirado(guild_id):
        return cache["usuarios"][user_id].copy()
    
    # Busca do MongoDB
    usuarios_col, _ = _get_collections(guild_id)
    doc = usuarios_col.find_one({"_id": user_id})
    if doc:
        doc.pop("_id", None)
        cache["usuarios"][user_id] = doc
        cache["timestamp"] = time.time()
        return doc.copy()
    
    return None

def carregar_dados(guild_id):
    """Carrega todos os dados de um servidor específico do MongoDB (com cache)."""
    guild_id = str(guild_id)
    _init_guild_cache(guild_id)
    cache = _cache_guilds[guild_id]
    
    # Se cache ainda válido, monta dos dados cacheados
    if not _cache_expirado(guild_id) and cache["config"] is not None:
        return {
            "usuarios": {k: v.copy() for k, v in cache["usuarios"].items()},
            "itens_globais": cache["config"].get("itens_globais", {}),
            "loja_custom": cache["config"].get("loja_custom", {}),
            "missoes": cache["config"].get("missoes", [])
        }
    
    dados = {
        "usuarios": {},
        "itens_globais": {},
        "loja_custom": {},
        "missoes": []
    }
    
    usuarios_col, config_col = _get_collections(guild_id)
    
    # Carrega usuários
    for doc in usuarios_col.find():
        user_id = str(doc.pop("_id"))
        dados["usuarios"][user_id] = doc
        cache["usuarios"][user_id] = doc.copy()
    
    # Carrega config
    config = config_col.find_one({"_id": "global"})
    if config:
        config.pop("_id", None)
        cache["config"] = config
        dados["itens_globais"] = config.get("itens_globais", {})
        dados["loja_custom"] = config.get("loja_custom", {})
        dados["missoes"] = config.get("missoes", [])
    else:
        cache["config"] = {}
    
    cache["timestamp"] = time.time()
    return dados

def salvar_dados(guild_id, dados):
    """Salva dados de um servidor específico no MongoDB e atualiza cache."""
    guild_id = str(guild_id)
    _init_guild_cache(guild_id)
    cache = _cache_guilds[guild_id]
    
    usuarios_col, config_col = _get_collections(guild_id)
    
    # Salva usuários
    for user_id, info in dados["usuarios"].items():
        usuarios_col.update_one(
            {"_id": str(user_id)},
            {"$set": info},
            upsert=True
        )
        cache["usuarios"][str(user_id)] = info.copy()
    
    # Salva config do servidor
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
    cache["config"] = config_data
    cache["timestamp"] = time.time()

def salvar_usuario(guild_id, user_id, info):
    """Salva apenas UM usuário de um servidor específico - mais rápido!"""
    guild_id = str(guild_id)
    user_id = str(user_id)
    
    _init_guild_cache(guild_id)
    cache = _cache_guilds[guild_id]
    
    usuarios_col, _ = _get_collections(guild_id)
    usuarios_col.update_one(
        {"_id": user_id},
        {"$set": info},
        upsert=True
    )
    cache["usuarios"][user_id] = info.copy()
    cache["timestamp"] = time.time()

def obter_usuario(guild_id, user_id):
    """Alias para carregar_usuario."""
    return carregar_usuario(guild_id, user_id)

def atualizar_usuario(guild_id, user_id, info):
    """Alias para salvar_usuario."""
    salvar_usuario(guild_id, user_id, info)

def deletar_usuario(guild_id, user_id):
    """Remove um usuário do banco de um servidor específico."""
    guild_id = str(guild_id)
    user_id = str(user_id)
    
    usuarios_col, _ = _get_collections(guild_id)
    usuarios_col.delete_one({"_id": user_id})
    
    # Remove do cache também
    if guild_id in _cache_guilds and user_id in _cache_guilds[guild_id]["usuarios"]:
        del _cache_guilds[guild_id]["usuarios"][user_id]

def listar_guilds():
    """Lista todas as guilds que têm dados no banco."""
    collections = db.list_collection_names()
    guilds = set()
    for col in collections:
        if col.startswith("guild_") and col.endswith("_usuarios"):
            guild_id = col.replace("guild_", "").replace("_usuarios", "")
            guilds.add(guild_id)
    return list(guilds)

# === MIGRAÇÃO DE DADOS LEGADOS (Elandor) ===
def migrar_dados_legados_para_guild(guild_id):
    """
    Migra os dados das collections antigas (usuarios, config) para o novo formato multi-guild.
    Use isso UMA VEZ para migrar os dados do servidor Elandor.
    """
    guild_id = str(guild_id)
    
    # Collections antigas (formato antigo)
    old_usuarios = db["usuarios"]
    old_config = db["config"]
    
    # Novas collections
    new_usuarios, new_config = _get_collections(guild_id)
    
    # Migra usuários
    count_usuarios = 0
    for doc in old_usuarios.find():
        new_usuarios.update_one(
            {"_id": doc["_id"]},
            {"$set": {k: v for k, v in doc.items() if k != "_id"}},
            upsert=True
        )
        count_usuarios += 1
    
    # Migra config
    old_config_doc = old_config.find_one({"_id": "global"})
    if old_config_doc:
        new_config.update_one(
            {"_id": "global"},
            {"$set": {k: v for k, v in old_config_doc.items() if k != "_id"}},
            upsert=True
        )
    
    print(f"✅ Migração concluída! {count_usuarios} usuários migrados para guild_{guild_id}")
    return count_usuarios
