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
    p["xp"] = p.get("xp", 0) + quantidade
    p["xp_max"] = p.get("xp_max", 500)
    subiu = False

    while p["xp"] >= p["xp_max"]:
        p["xp"] -= p["xp_max"]
        p["nivel"] += 1
        p["xp_max"] = calcular_proximo_xp(p["nivel"], p["xp_max"])
        subiu = True
    return subiu