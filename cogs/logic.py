import random
import constantes

def rolar_dado(string_dado):
    """
    Suporta '2d10' (soma) e '2#d10' (maior valor).
    Retorna (resultado_final, lista_de_dados, modo)
    """
    string_dado = string_dado.lower().replace(" ", "")
    
    if '#' in string_dado:
        partes = string_dado.split('#')
        qtd = int(partes[0])
        faces_str = partes[1].replace('d', '')
        faces = int(faces_str)
        
        resultados = [random.randint(1, faces) for _ in range(qtd)]
        return max(resultados), resultados, "maior"

    elif 'd' in string_dado:
        qtd, faces = map(int, string_dado.split('d'))
        resultados = [random.randint(1, faces) for _ in range(qtd)]
        return sum(resultados), resultados, "soma"
    
    return 0, [], "erro"

def calcular_dano_nivel(nivel):
    """Retorna o dado de dano base do jogador conforme o nível"""
    if nivel <= 2: return "1d6"
    if nivel <= 5: return "1d8"
    if nivel <= 10: return "2d6"
    if nivel <= 15: return "2d8"
    return "3d6"

def aplicar_dano_complexo(p_data, dano_bruto):
    """
    Função ÚNICA para aplicar dano. 
    Calcula Escudo e verifica Fada.
    """
    escudo = p_data.get("ca", 0)
    
    if "Escudo da Vigília Ancestral" in p_data.get("inventario", []):
        escudo += 6
        
    dano_final = max(0, dano_bruto - escudo)
    p_data["pv"] -= dano_final
    
    log = f"💢 Dano: {dano_bruto} - Escudo: {escudo} = **{dano_final} sofrido.**"
    
    if p_data["pv"] <= 0:
        if "Fada" in p_data.get("inventario", []):
            p_data["inventario"].remove("Fada")
            nivel = p_data.get("nivel", 1)
            v_max = 30
            for faixa, valores in constantes.PROGRESSAO.items():
                partes = faixa.split('-')
                if int(partes[0]) <= nivel <= int(partes[1]):
                    v_max = valores["pv"]
                    break
            p_data["pv"] = v_max // 2
            log += f"\n✨ **A Fada salvou {p_data['nome']}!** PV: {p_data['pv']}"
            return log, False
        else:
            p_data["pv"] = 0
            log += f"\n💀 **{p_data['nome']} morreu.**"
            return log, True
            
    return log, False

def processar_xp_acumulado(p, quantidade_ganha):
    p["xp"] = p.get("xp", 0) + quantidade_ganha
    upou_pelo_menos_uma_vez = False
    
    while True:
        nivel_atual = p.get("nivel", 1)
        if nivel_atual >= 20: 
            break
            
        xp_necessario = nivel_atual * 100 
        
        if p["xp"] >= xp_necessario:
            p["xp"] -= xp_necessario
            p["nivel"] += 1
            p["descansos"] = p.get("descansos", 0) + 1
            upou_pelo_menos_uma_vez = True
            
            for faixa, st in constantes.TABELA_NIVEIS.items():
                f_inicio, f_fim = map(int, faixa.split('-'))
                if f_inicio <= p["nivel"] <= f_fim:
                    p["pv_max"] = st["pv"]
                    p["ca"] = st["ca"]
                    p["dado_nivel"] = st["dado"]
                    p["pv"] = p["pv_max"] 
                    break
        else:
            break
            
    return upou_pelo_menos_uma_vez

def usar_pocao_sorte(usuario_data):
    sorteio = random.random()

    if sorteio < 0.10:
        perda = random.randint(50, 150)
        usuario_data["dinheiro"] = max(0, usuario_data["dinheiro"] - perda)
        usuario_data["azarado"] = True
        return f"💀 **RUÍNA!** Perdeu **{perda} Krugs** e está azarado.", "azar"

    elif sorteio < 0.55:
        min_m, max_m = constantes.VALOR_SORTE_MOEDAS
        qtd = random.randint(min_m, max_m)
        usuario_data["dinheiro"] += qtd
        return f"🍀 Você encontrou **{qtd} Krugs**!", "moedas"

    else:
        item = random.choice(constantes.RECOMPENSAS_SORTE)
        usuario_data.setdefault("inventario", []).append(item)
        return f"🎁 O destino deu: **{item}**.", item