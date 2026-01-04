from database import salvar_dados
import random
from constantes import PROGRESSAO
import constantes

def aplicar_dano(usuario_data, dano):
    """
    Aplica dano e verifica se a Fada deve salvar o jogador.
    Retorna uma tupla: (mensagem_de_status, morreu_de_vez)
    """
    usuario_data["pv"] -= dano
    nome = usuario_data["nome"]

    if usuario_data["pv"] <= 0:
        # Verifica se tem o item 'Fada' no inventário
        if "Fada" in usuario_data["inventario"]:
            usuario_data["inventario"].remove("Fada") # Consome o item
            vida_maxima = 30 # Ou a vida baseada no nível dele
            # Resgata com 50% da vida total conforme a faixa de nível
            if usuario_data["nivel"] <= 5: vida_maxima = 30
            elif usuario_data["nivel"] <= 10: vida_maxima = 50
            elif usuario_data["nivel"] <= 15: vida_maxima = 70
            else: vida_maxima = 90
            
            usuario_data["pv"] = vida_maxima // 2
            return f"✨ **A Fada saiu do inventário de {nome} e se sacrificou!** {nome} voltou com {usuario_data['pv']} PV.", False
        else:
            usuario_data["pv"] = 0
            return f"💀 **{nome} sucumbiu aos ferimentos e morreu.**", True
            
    return f"💢 {nome} recebeu {dano} de dano. PV restante: {usuario_data['pv']}", False

def rolar_dado(string_dado):
    """Converte '2d6' em resultado numérico"""
    qtd, faces = map(int, string_dado.split('d'))
    return sum(random.randint(1, faces) for _ in range(qtd))

def aplicar_dano_complexo(p_data, dano_bruto):
    """
    p_data: dicionário do jogador no JSON
    dano_bruto: dano vindo da arma ou habilidade
    """
    escudo = p_data.get("ca", 0)
    
    # Se tiver itens de bônus no inventário, soma aqui
    # Exemplo simplificado:
    if "Escudo da Vigília Ancestral" in p_data["inventario"]:
        escudo += 6
        
    dano_final = max(0, dano_bruto - escudo)
    p_data["pv"] -= dano_final
    
    log = f"💢 Dano: {dano_bruto} - Escudo: {escudo} = **{dano_final} sofrido.**"
    
    # Lógica da Fada (Ressurreição)
    if p_data["pv"] <= 0:
        if "Fada" in p_data["inventario"]:
            p_data["inventario"].remove("Fada")
            # Pega vida máxima da tabela de progressão
            nivel = p_data["nivel"]
            v_max = 30
            for faixa, valores in PROGRESSAO.items():
                inicio, fim = map(int, faixa.split('-'))
                if inicio <= nivel <= fim:
                    v_max = valores["pv"]
                    break
            p_data["pv"] = v_max // 2
            log += f"\n✨ **A Fada salvou {p_data['nome']}!** Retornou com {p_data['pv']} PV."
            return log, False
        else:
            p_data["pv"] = 0
            log += f"\n💀 **{p_data['nome']} morreu.**"
            return log, True
            
    return log, False

def usar_pocao_sorte(usuario_data):
    sorteio = random.random() # Gera um número entre 0.0 e 1.0

    # 10% de chance de Azar Crítico (Ruína)
    if sorteio < 0.10:
        perda = random.randint(50, 150)
        usuario_data["dinheiro"] = max(0, usuario_data["dinheiro"] - perda)
        usuario_data["azarado"] = True # O azar fica espreitando...
        return f"💀 **RUÍNA!** A poção explodiu em fumaça negra. Você perdeu **{perda} Krugs** e sente uma aura de azar te perseguindo.", "azar"

    # 45% de chance de Moedas
    elif sorteio < 0.55:
        qtd = random.randint(50, 300)
        usuario_data["dinheiro"] += qtd
        return f"🍀 O destino sorriu! Você encontrou **{qtd} Krugs**.", "moedas"

    # 45% de chance de Item
    else:
        item = random.choice(constantes.RECOMPENSAS_SORTE)
        usuario_data["inventario"].append(item)
        return f"🎁 O destino foi generoso! Você ganhou: **{item}**.", item