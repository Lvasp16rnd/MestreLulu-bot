import random
import constantes

def rolar_dado(string_dado):
    """Converte '2d6' em resultado numérico"""
    qtd, faces = map(int, string_dado.split('d'))
    return sum(random.randint(1, faces) for _ in range(qtd))

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
    # Se o jogador não tiver o campo 'ca', assume 0
    escudo = p_data.get("ca", 0)
    
    # Bônus de itens específicos
    if "Escudo da Vigília Ancestral" in p_data.get("inventario", []):
        escudo += 6
        
    dano_final = max(0, dano_bruto - escudo)
    p_data["pv"] -= dano_final
    
    log = f"💢 Dano: {dano_bruto} - Escudo: {escudo} = **{dano_final} sofrido.**"
    
    # Lógica da Fada
    if p_data["pv"] <= 0:
        if "Fada" in p_data.get("inventario", []):
            p_data["inventario"].remove("Fada")
            nivel = p_data.get("nivel", 1)
            v_max = 30
            # Busca vida máxima nas constantes
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