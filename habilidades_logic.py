import random
from cogs.logic import calcular_dano_nivel, rolar_dado

def processar_uso_habilidade(p, dados_hab, mod_azar):
    roll = random.randint(1, 20)
    total = max(1, roll + mod_azar)
    sucesso = total >= dados_hab["dt"]
    
    resultado = {"total": total, "sucesso": sucesso, "dano": 0, "cura": 0}
    
    if sucesso:
        formato = dados_hab.get("valor_fixo", calcular_dano_nivel(p["nivel"]))
        valor = rolar_dado(formato) + p["atributos"]["forca"]
        if dados_hab.get("tipo") == "cura":
            resultado["cura"] = valor
        else:
            resultado["dano"] = valor
            
    return resultado