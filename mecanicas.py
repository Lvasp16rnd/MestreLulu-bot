def calcular_proximo_xp(nivel_atual, xp_max_atual):
    """Calcula o requisito de XP com as porcentagens sugeridas."""
    if nivel_atual < 5:
        # Até o nível 5: +50%
        return int(xp_max_atual * 1.5)
    elif nivel_atual < 10:
        # Do nível 5 ao 10: +25%
        return int(xp_max_atual * 1.25)
    else:
        # Do nível 10 em diante: +15%
        return int(xp_max_atual * 1.15)

def adicionar_xp(p, quantidade):
    """Adiciona XP e retorna True se subir de nível."""
    from cogs.logic import aplicar_status_nivel
    
    p["xp"] = p.get("xp", 0) + quantidade
    p["xp_max"] = p.get("xp_max", 100)  # Base inicial: 100 XP
    subiu = False

    while p["xp"] >= p["xp_max"]:
        p["xp"] -= p["xp_max"]
        p["nivel"] = p.get("nivel", 1) + 1
        p["descansos"] = p.get("descansos", 0) + 1
        p["xp_max"] = calcular_proximo_xp(p["nivel"], p["xp_max"])
        aplicar_status_nivel(p)
        subiu = True
    return subiu