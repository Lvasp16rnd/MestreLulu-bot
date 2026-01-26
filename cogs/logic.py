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

def aplicar_status_nivel(p):
    """Lê a TABELA_NIVEIS e define PV, CA e Dado estáticos conforme a faixa."""
    import constantes
    nivel = p.get("nivel", 1)
    for faixa, st in constantes.TABELA_NIVEIS.items():
        try:
            f_inicio, f_fim = map(int, faixa.split('-'))
            if f_inicio <= nivel <= f_fim:
                p["pv_max"] = st["pv"]
                p["ca"] = st["ca"]
                p["dado_nivel"] = st["dado"]
                p["pv"] = p["pv_max"] 
                return True
        except:
            continue
    return False

def calcular_xp_necessario(nivel_atual, xp_max_atual):
    """
    Calcula o XP necessário para o próximo nível usando a curva de progressão:
    - Nível 1-5: +50% por nível
    - Nível 6-10: +25% por nível  
    - Nível 11-20: +15% por nível
    """
    if nivel_atual < 5:
        return int(xp_max_atual * 1.5)
    elif nivel_atual < 10:
        return int(xp_max_atual * 1.25)
    else:
        return int(xp_max_atual * 1.15)

def processar_xp_acumulado(p, quantidade_ganha):
    p["xp"] = p.get("xp", 0) + quantidade_ganha
    p["xp_max"] = p.get("xp_max", 100)
    upou = False
    
    while True:
        nivel_atual = p.get("nivel", 1)
        if nivel_atual >= 20: break
            
        xp_necessario = p["xp_max"]
        
        if p["xp"] >= xp_necessario:
            p["xp"] -= xp_necessario 
            p["nivel"] += 1
            p["descansos"] = p.get("descansos", 0) + 1
            p["xp_max"] = calcular_xp_necessario(p["nivel"], p["xp_max"]) 
            aplicar_status_nivel(p) 
            upou = True
        else:
            break 
            
    return upou

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

ATRIBUTOS_VALIDOS = {
    "força": "forca",
    "forca": "forca",
    "for": "forca",
    "agilidade": "agilidade",
    "agi": "agilidade",
    "intelecto": "intelecto",
    "int": "intelecto",
    "presença": "presenca",
    "presenca": "presenca",
    "pre": "presenca",
    "carisma": "carisma",
    "car": "carisma"
}

ATRIBUTOS_DISPLAY = ["Força", "Agilidade", "Intelecto", "Presença", "Carisma"]


def normalizar_atributo(nome: str) -> str | None:
    """
    Converte variações do nome do atributo para o formato interno.
    Retorna None se o atributo não for válido.
    """
    return ATRIBUTOS_VALIDOS.get(nome.lower().strip())


def calcular_formula_atributo(valor_atributo: int) -> tuple[int, str]:
    """
    Retorna a quantidade de dados e o modo de seleção baseado no valor do atributo.
    
    Regras:
    - 0: 2d20, pega o MENOR (desvantagem)
    - 1: 1d20 normal
    - 2: 2d20, pega o MAIOR (vantagem)
    - 3+: 3d20, pega o MAIOR (super vantagem)
    
    Returns:
        tuple: (quantidade_dados, modo) onde modo é "menor", "normal" ou "maior"
    """
    if valor_atributo <= 0:
        return 2, "menor"
    elif valor_atributo == 1:
        return 1, "normal"
    elif valor_atributo == 2:
        return 2, "maior"
    else:  # 3 ou mais
        return 3, "maior"


def rolar_teste_atributo(valor_atributo: int, modificador: int = 0) -> dict:
    """
    Executa um teste baseado no valor do atributo.
    
    Args:
        valor_atributo: O valor do atributo (0, 1, 2, 3+)
        modificador: Bônus ou penalidade adicional ao resultado
    
    Returns:
        dict com:
            - resultado: valor final após seleção
            - dados: lista de todos os dados rolados
            - modo: "menor", "normal" ou "maior"
            - quantidade: quantos dados foram rolados
            - total: resultado + modificador
            - modificador: o modificador aplicado
    """
    quantidade, modo = calcular_formula_atributo(valor_atributo)
    
    dados = [random.randint(1, 20) for _ in range(quantidade)]
    
    if modo == "menor":
        resultado = min(dados)
    elif modo == "maior":
        resultado = max(dados)
    else:  # normal
        resultado = dados[0]
    
    total = resultado + modificador
    
    return {
        "resultado": resultado,
        "dados": dados,
        "modo": modo,
        "quantidade": quantidade,
        "total": total,
        "modificador": modificador
    }


def formatar_resultado_teste(nome_atributo: str, valor_atributo: int, resultado: dict) -> str:
    """
    Formata o resultado do teste para exibição.
    
    Returns:
        String formatada para embed do Discord
    """
    dados_str = ", ".join(map(str, resultado["dados"]))
    
    if resultado["modo"] == "menor":
        emoji_modo = "📉"
        descricao_modo = "Desvantagem (menor valor)"
    elif resultado["modo"] == "maior":
        emoji_modo = "📈"
        descricao_modo = "Vantagem (maior valor)" if resultado["quantidade"] == 2 else "Super Vantagem (maior valor)"
    else:
        emoji_modo = "🎲"
        descricao_modo = "Rolagem normal"
    
    texto = f"{emoji_modo} **Modo:** {descricao_modo}\n"
    texto += f"🎲 **Dados rolados:** `[{dados_str}]`\n"
    texto += f"✨ **Resultado selecionado:** `{resultado['resultado']}`"
    
    if resultado["modificador"] != 0:
        sinal = "+" if resultado["modificador"] > 0 else ""
        texto += f"\n🔧 **Modificador:** `{sinal}{resultado['modificador']}`"
        texto += f"\n📊 **Total Final:** `{resultado['total']}`"
    
    return texto