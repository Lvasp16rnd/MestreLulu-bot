"""
Script para migrar dados do dados.json para MongoDB.
Execute uma vez antes do deploy.
"""
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ MONGO_URI não encontrado no .env!")
    print("Adicione: MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster.mongodb.net/")
    exit(1)

client = MongoClient(MONGO_URI)
db = client["mestre_lulu"]

usuarios_col = db["usuarios"]
config_col = db["config"]

# Carrega dados.json
if not os.path.exists("dados.json"):
    print("❌ dados.json não encontrado!")
    exit(1)

with open("dados.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

print(f"📂 Encontrados {len(dados.get('usuarios', {}))} usuários no dados.json")

# Migra usuários
for user_id, info in dados.get("usuarios", {}).items():
    usuarios_col.update_one(
        {"_id": user_id},
        {"$set": info},
        upsert=True
    )
    print(f"  ✅ Migrado: {info.get('nome', user_id)}")

# Migra config global
config_col.update_one(
    {"_id": "global"},
    {"$set": {
        "itens_globais": dados.get("itens_globais", {}),
        "loja_custom": dados.get("loja_custom", {}),
        "missoes": dados.get("missoes", [])
    }},
    upsert=True
)

print("\n🎉 Migração concluída!")
print("Agora renomeie database_mongo.py para database.py")
