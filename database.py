import json
import os

DB_FILE = 'dados.json'

def carregar_dados():
    # Estrutura inicial padrão do seu RPG
    default_data = {
        "usuarios": {}, 
        "itens_globais": {}, 
        "loja_custom": {}, 
        "missoes": []
    }

    if not os.path.exists(DB_FILE):
        return default_data
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Garante que chaves novas existam mesmo em arquivos antigos
            for chave, valor in default_data.items():
                if chave not in dados:
                    dados[chave] = valor
            return dados
    except (json.JSONDecodeError, FileNotFoundError):
        return default_data

def salvar_dados(dados):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def obter_usuario(user_id):
    dados = carregar_dados()
    return dados["usuarios"].get(str(user_id))

def atualizar_usuario(user_id, info):
    dados = carregar_dados()
    dados["usuarios"][str(user_id)] = info
    salvar_dados(dados)