import random
from cogs.logic import calcular_dano_nivel, rolar_dado

def processar_uso_habilidade(p, dados_hab, mod_azar):
    inventario = p.get("inventario", [])
    raca_player = p.get("raca", "Humano")
    
    # --- 1. PREPARAÇÃO DE VARIÁVEIS ---
    atr_usado = dados_hab.get("atributo", "forca").lower()
    valor_atributo = p["atributos"].get(atr_usado, 0)
    
    mod_dt_item = 0
    dano_extra = 0
    formato_dado = dados_hab.get("valor_fixo", calcular_dano_nivel(p["nivel"]))
    log_uso = [] # Para avisar o que foi consumido

    # --- 2. LÓGICA DE ITENS DOS ELFOS (O VEL) ---

    # 🏹 Flechas de Sol (Consumível - Só Elfos ou Arcos Puros)
    # Regra: +3 de dano. Se não for Elfo, há risco de traição (narrativo).
    if "Flechas de Sol" in inventario:
        if raca_player == "Elfo":
            dano_extra += 3
            inventario.remove("Flechas de Sol")
            log_uso.append("🏹 Uma *Flecha de Sol* foi disparada!")
        else:
            # Se não for elfo, a flecha pode falhar ou revelar posição (Lógica de Mestre)
            log_uso.append("⚠️ As *Flechas de Sol* brilham instáveis em mãos não-élficas!")

    # 🩸 Sangue do Cupido (Consumível - Uso Único)
    # Regra: -2 na DT do teste atual.
    if "Sangue do Cupido" in inventario:
        mod_dt_item -= 2
        inventario.remove("Sangue do Cupido")
        log_uso.append("🩸 Uma gota de *Sangue do Cupido* guiou sua lâmina.")

    # ☘️ Presilhas Trevo (Equipamento - Não some, mas a sorte é passageira)
    # Regra: -3 na DT de todos os testes.
    if "Presilhas Trevo" in inventario:
        mod_dt_item -= 3

    # 💎 Brincos de Frey (Equipamento - Requer par)
    # Regra: +3 de Carisma em qualquer teste.
    if "Brincos de Frey" in inventario:
        # Se o teste usa carisma, aplicamos o bônus
        if atr_usado == "carisma":
            valor_atributo += 3
        # Se for outro atributo, mas o item dá "aura de encanto", 
        # podemos dar um bônus menor ou narrativo.

    # 🥕 Cenouras Cantantes (Consumível - Atordoar)
    # Se a habilidade for de controle/atordoar, ela ganha bônus.
    if "Cenouras Cantantes" in inventario and "atordoar" in dados_hab.get("tags", []):
        mod_dt_item -= 2 # Fica mais fácil acertar o atordoamento
        inventario.remove("Cenouras Cantantes")
        log_uso.append("🥕 Você mordeu uma *Cenoura Cantante*! O grito atordoou o alvo.")

    # --- LÓGICA KHAERUN (KHARR-DUM) ---

    # 🔨 Martelo do Eco Profundo (Equipamento)
    # Regra: 2d8 de dano. Rejeita fuga.
    if "Martelo do Eco Profundo" in inventario:
        formato_dado = "2d8"
        log_uso.append("🔨 O solo vibra com o *Martelo do Eco Profundo*!")

    # 🛡️ Escudo da Vigília Ancestral (Equipamento)
    # Regra: +6 de armadura (Essa lógica já aplicamos no aplicar_dano_complexo)
    # Aqui podemos dar um bônus extra se a habilidade for defensiva.
    if "Escudo da Vigília Ancestral" in inventario and dados_hab.get("tipo") == "defesa":
        mod_dt_item -= 2 # Mais fácil ter sucesso em defesas

    # 🪓 Machado das Runas de Sangue (Risco e Recompensa)
    # Regra: -1d4 PV no portador, +1d10 + dano_perdido no alvo.
    if "Machado das Runas de Sangue" in inventario:
        perda_portador = random.randint(1, 4)
        p["pv"] -= perda_portador
        dano_extra += (random.randint(1, 10) + perda_portador)
        log_uso.append(f"🪓 O Machado bebeu seu sangue! (-{perda_portador} PV) e brilhou em fúria.")

    # 🪖 Elmo da Rocha Silenciosa (Equipamento)
    # Regra: +2 Presença, -2 Agilidade. Imunidade a Medo.
    if "Elmo da Rocha Silenciosa" in inventario:
        if atr_usado == "presenca": valor_atributo += 2
        if atr_usado == "agilidade": valor_atributo -= 2
        log_uso.append("🪖 Sua mente é uma montanha (Elmo da Rocha Silenciosa).")

    # ⛓️ Corrente do Conselho Partido (Social)
    if "Corrente do Conselho Partido" in inventario and atr_usado in ["carisma", "presenca"]:
        mod_dt_item -= 4 # Bônus massivo em negociações, mas perigoso se mentir
        log_uso.append("⛓️ A *Corrente do Conselho* impõe um silêncio reverente.")

    # 💣 Proibida (Consumível - Dano em Área)
    # Regra: +1d30 de dano (dividido se houver múltiplos alvos - lógica de Mestre)
    if "Proibida" in inventario:
        dano_extra += random.randint(1, 30)
        inventario.remove("Proibida")
        log_uso.append("💣 **DETONADO!** A esfera proibida causou uma explosão catastrófica.")

    # --- LÓGICA FADAS (LÚMINA - ÍRIS) ---

    # 💎 Pulseiras do Batimento Lúmino (Equipamento)
    # Regra: +3 de Carisma fixo.
    if "Pulseiras do Batimento Lúmino" in inventario:
        if atr_usado == "carisma":
            valor_atributo += 3
        log_uso.append("💎 As pulseiras pulsam em sincronia com seu coração (+3 Carisma).")

    # 🍶 Frasco de Luz Engarrafada (Consumível - Arremessável)
    # Regra: Causa 1d6 de dano direto em Corações Corrompidos ao ser arremessado.
    if "Frasco de Luz Engarrafada" in inventario:
        # Verifica se o alvo é corrompido (via tag da habilidade)
        if "corrompido" in dados_hab.get("tags", []):
            # O dano agora é o próprio 1d6 do arremesso
            dano_arremesso = random.randint(1, 6)
            dano_extra += dano_arremesso
            
            inventario.remove("Frasco de Luz Engarrafada")
            log_uso.append(f"🍶 Você arremessou o *Frasco de Luz*! A explosão luminosa causou **{dano_arremesso}** de dano purificador.")
        else:
            # Se o mestre permitir arremessar em alvos normais, o dano pode ser menor ou nulo
            log_uso.append("⚠️ Você segura o Frasco... mas não sente escuridão no alvo para liberar a luz.")

    # 🌱 Sementes do Recomeço Lento (Consumível)
    # Regra: +1d15 de cura em área (até 3 criaturas).
    if "Sementes do Recomeço Lento" in inventario:
        if dados_hab.get("tipo") == "cura":
            cura_area_bonus = random.randint(1, 15)
            dano_extra += cura_area_bonus # Adicionamos ao valor final da cura
            inventario.remove("Sementes do Recomeço Lento")
            log_uso.append(f"🌱 Sementes plantadas! O tempo desacelera para curar (+{cura_area_bonus} PV).")

    # 🕸️ Véu da Última Lembrança (Equipamento)
    # Regra: Imunidade a medo/trauma (Narrativo). 
    # Podemos dar um bônus de resistência se a habilidade for para resistir a medo.
    if "Véu da Última Lembrança" in inventario and "medo" in dados_hab.get("tags", []):
        mod_dt_item -= 5 # Fica muito mais fácil resistir ao medo
        log_uso.append("🕸️ O Véu apaga a lembrança do medo. Sua mente está calma.")

    # 💧 Colar do Nome Verdadeiro (Equipamento)
    # Regra: DT 18 para mentirem para o usuário.
    # Esta lógica é Social/Narrativa. Se você usar em um teste de 'Intuição' ou 'Sentir Motivação':
    if "Colar do Nome Verdadeiro" in inventario and atr_usado in ["presenca", "intuicao"]:
        mod_dt_item -= 4 
        log_uso.append("💧 O pingente brilha... o som da verdade ecoa no Colar.")

    # --- LÓGICA BRUXAS (CASA DAS BRUXAS - MESTRE LULU) ---

    # ⏳ Poção do Tempo Velado (Consumível)
    # Regra: +1d10 de vida. Manipula o tempo para curar ou acelerar.
    if "Poção do Tempo Velado" in inventario:
        # Se for uma habilidade de cura, ela potencializa. 
        # Se for uma habilidade de agilidade (parar o tempo), ela facilita a DT.
        if dados_hab.get("tipo") == "cura":
            bonus_tempo = random.randint(1, 10)
            dano_extra += bonus_tempo
            inventario.remove("Poção do Tempo Velado")
            log_uso.append(f"⏳ O tempo desacelera... suas feridas fecham instantaneamente! (+{bonus_tempo} PV)")
        elif atr_usado == "agilidade":
            mod_dt_item -= 4
            inventario.remove("Poção do Tempo Velado")
            log_uso.append("⏳ O mundo congelou por um segundo! (DT -4 em Agilidade)")

    # 🧪 Poções Mentais (Amor, Verdade, Raiva, Esquecimento)
    # Regra: Criam elos irresistíveis ou apagam mentes. Facilitam testes Sociais/Mentais.
    pocoes_mentais = {
        "Poção do Amor": "💖 O fascínio da poção tornou o alvo vulnerável!",
        "Poção da Verdade": "👁️ A prata líquida obriga a verdade a sair!",
        "Poção da Raiva": "💢 O sangue ferve! Fúria e força sobre-humanas despertadas.",
        "Poção do Esquecimento": "☁️ Um véu de bruma apagou a memória do alvo."
    }

    for nome_pocao, mensagem in pocoes_mentais.items():
        if nome_pocao in inventario:
            # Essas poções afetam habilidades de Carisma ou Presença (ou tags sociais)
            if atr_usado in ["carisma", "presenca"] or "social" in dados_hab.get("tags", []):
                mod_dt_item -= 6 # Bônus massivo, quase um sucesso automático
                
                # Bônus de dano específico para a Poção da Raiva
                if nome_pocao == "Poção da Raiva":
                    dano_extra += 5 
                
                inventario.remove(nome_pocao)
                log_uso.append(f"{mensagem} (DT -6)")
                break # Usa apenas uma poção por vez

    # 🍀 Poção da Sorte (Consumível)
    # Nota: A lógica de ganhar itens/moedas geralmente é feita num comando separado (!beber),
    # mas se usada em combate, podemos dar um bônus de sorte.
    if "Poção da Sorte" in inventario:
        mod_dt_item -= 2
        # Aqui não removemos automaticamente para deixar o player usar o comando !beber_sorte 
        # e ganhar os itens/moedas, a menos que você queira que ela dê sorte no dado agora.
        log_uso.append("🍀 O destino se curva ao seu favor com a Poção da Sorte.")

    # --- LÓGICA DROWS (SALÃO DO VENENO SILENCIOSO - ZHYRA) ---
    
    # Verificação de Raça para Uso de Itens Drow
    pode_usar_drow = raca_player in ["Drow", "Fragmentado", "Humano", "Bruxa"]

    # ⚔️ Lâminas Irmãs de Ardósia (Equipamento)
    # Regra: 2d6 de dano se for uma das raças permitidas.
    if "Lâminas Irmãs de Ardósia" in inventario and pode_usar_drow:
        formato_dado = "2d6"
        log_uso.append("⚔️ As *Lâminas Irmãs* cortam o ar em sincronia (2d6).")

    # 🌑 Manto da Penumbra Vingativa (Equipamento)
    # Regra: Bônus em ataques surpresa / invisibilidade.
    if "Manto da Penumbra Vingativa" in inventario and pode_usar_drow:
        if "furtivo" in dados_hab.get("tags", []):
            mod_dt_item -= 4 # Muito mais fácil atacar furtivamente
            dano_extra += 5  # Bônus de ataque surpresa
            log_uso.append("🌑 O Manto absorve a luz, ocultando seu golpe letal.")

    # 💍 Anel do Exílio Antigo (Equipamento)
    # Regra: +5 de dano contra Elfos, Fadas e Khaerun.
    if "Anel do Exílio Antigo" in inventario and pode_usar_drow:
        tags_hab = [t.lower() for t in dados_hab.get("tags", [])]
        raca_alvo = dados_hab.get("raca_alvo", "").lower() 

        alvos_odiados = ["elfo", "fada", "khaerun"]
        
        if any(r in tags_hab for r in alvos_odiados) or raca_alvo in alvos_odiados:
            dano_extra += rolar_dado("1d6")
            log_uso.append("💍 O Anel do Exílio brilha com um ódio frio contra o alvo (+5 dano).")
    # 🧪 Veneno da Lua Incerta (Consumível - Mecânica de Risco)
    # Regra: Sucesso = Paralisa inimigo. Falha = Paralisa usuário.
    if "Veneno da Lua Incerta" in inventario and pode_usar_drow:
        inventario.remove("Veneno da Lua Incerta")
        veneno_ativo = True 
        log_uso.append("🧪 Você aplicou o *Veneno da Lua* na lâmina. O destino é incerto...")
    else:
        veneno_ativo = False

    # 🔮 Oráculo de Obsidiana Quebrada (Equipamento)
    # Regra: Prever movimento (Bônus na DT de defesa).
    if "Oráculo de Obsidiana Quebrada" in inventario and pode_usar_drow:
        if dados_hab.get("tipo") == "defesa":
            mod_dt_item -= 3
            log_uso.append("🔮 O Oráculo mostra fragmentos do futuro movimento inimigo.")

    # --- LÓGICA HUMANOS ERRANTES (CARAVANA DE MAELIS) ---

    # 🎖️ Broche da Bandeira Invisível (Equipamento)
    # Regra: +5 de Presença (Liderança e Moral)
    if "Broche da Bandeira Invisível" in inventario:
        if atr_usado == "presenca":
            valor_atributo += 5
            log_uso.append("🎖️ O *Broche da Bandeira* brilha! Sua liderança inspira aliados (+5 Presença).")

    # ⚔️ Espada do Juramento Quebrado (Equipamento)
    # Regra: 1d8 de dano. Bônus contra corrompidos (arrependimento).
    if "Espada do Juramento Quebrado" in inventario:
        formato_dado = "1d8"
        if "corrompido" in dados_hab.get("tags", []):
            dano_extra += 4 # O "remorso" do portador pune o alvo
            log_uso.append("⚔️ A *Espada do Juramento* vibra contra a corrupção do alvo.")

    # 🧪 Frascos de Alquimia Errante (Consumível - Risco)
    # Regra: 1d4 de cura + efeito aleatório
    if "Frascos de Alquimia Errante" in inventario and dados_hab.get("tipo") == "cura":
        cura_base = random.randint(1, 4)
        dano_extra += cura_base
        inventario.remove("Frascos de Alquimia Errante")
        
        # Sorteio de efeito colateral
        colateral = random.choice(["vigor (bônus no próximo turno)", "náusea (-2 no próximo dado)", "coceira súbita"])
        log_uso.append(f"🧪 Alquimia Errante: +{cura_base} PV. Efeito Colateral: *{colateral}*.")

    # 🎲 Dado do Destino Ambulante (Consumível - Aposta Total)
    # Regra: Se o dado for baixo (ruim), ele pode forçar um sucesso, mas com risco.
    if "Dado do Destino Ambulante" in inventario:
        if roll <= 7: # Se o jogador tirou um dado baixo
            roll = 20 # Força o Sucesso Crítico
            inventario.remove("Dado do Destino Ambulante")
            log_uso.append("🎲 Você jogou o *Dado do Destino*! O fracasso virou um **SUCESSO CRÍTICO**, mas forças maiores notaram...")

    # 🧪 Poção do Quase Milagre (Consumível - O custo da sobrevivência)
    # Regra: 1d20 de cura. Se tirar 1 no d20, a cura é incompleta.
    if "Poção do Quase Milagre" in inventario and dados_hab.get("tipo") == "cura":
        roll_milagre = random.randint(1, 20)
        dano_extra += roll_milagre
        inventario.remove("Poção do Quase Milagre")
        
        if roll_milagre == 1:
            log_uso.append("🧪 **FALHA NO MILAGRE:** A poção teve um gosto amargo e a cura foi mínima...")
        else:
            log_uso.append(f"🧪 **MILAGRE!** A poção turva restaurou **{roll_milagre}** PV.")

    # 📜 Contrato de Areia (Social - Consumível)
    # Regra: Vantagem em negociações (DT -5).
    if "Contrato de Areia" in inventario and atr_usado in ["carisma", "presenca"]:
        mod_dt_item -= 5
        inventario.remove("Contrato de Areia")
        log_uso.append("📜 O *Contrato de Areia* garante termos favoráveis... por enquanto.")

    # --- LÓGICA FRAGMENTADOS (O ALTAR - SERETH VAUL) ---

    # 🔔 Sino da Repulsão Abissal (Consumível - Controle de Grupo)
    # Regra: Expulsa criaturas não-humanas.
    if "Sino da Repulsão Abissal" in inventario:
        # Se a habilidade for de controle ou espantar inimigos
        if "espantar" in dados_hab.get("tags", []) or "controle" in dados_hab.get("tags", []):
            mod_dt_item -= 5 # Facilita muito a expulsão
            inventario.remove("Sino da Repulsão Abissal")
            log_uso.append("🔔 O som do Sino negro ecoa... Criaturas não-humanas sentem um pavor abissal!")

    # 💨 Cinzas do Nome Perdido (Consumível - Defensivo)
    # Regra: Força recuo de outras espécies.
    if "Cinzas do Nome Perdido" in inventario:
        if dados_hab.get("tipo") == "defesa":
            mod_dt_item -= 4
            inventario.remove("Cinzas do Nome Perdido")
            log_uso.append("💨 Você lançou as Cinzas ao vento! Uma barreira invisível impede o avanço de outras espécies.")

   # 🛡️ Marca da Exclusão (Equipamento Permanente)
    # Regra: +7 de Defesa (passivo) e facilita o sucesso em testes de defesa.
    if "Marca da Exclusão" in inventario:
        # Se a habilidade for de defesa, ela fica mais fácil de acertar
        if dados_hab.get("tipo") == "defesa":
            mod_dt_item -= 3 
        # O bônus de +7 de CA/Defesa deve ser aplicado na função de cálculo de dano
        log_uso.append("🛡️ A *Marca da Exclusão* arde em sua pele, repelindo o ataque inimigo.")

    # --- 3. EXECUÇÃO DO TESTE ---
    dt_final = max(1, dados_hab["dt"] + mod_dt_item)
    roll = random.randint(1, 20)
    # Total = dado + atributo + modificador de azar (se houver)
    total = roll + valor_atributo + mod_azar
    sucesso = total >= dt_final
    
    # Lógica Extra do Veneno da Lua Incerta
    if veneno_ativo:
        if sucesso:
            log_uso.append("✨ **GLÓRIA:** O inimigo foi paralisado pelo veneno!")
        else:
            log_uso.append("💀 **RUÍNA:** O veneno reagiu com seu sangue! VOCÊ está paralisado.")

    resultado = {
        "total": total,               # Dado + Atributos + Itens
        "sucesso": sucesso,           # True ou False
        "dano": 0, 
        "cura": 0, 
        "dt_aplicada": dt_final,      # DT final após bônus de itens
        "logs": log_uso,              # Frases dos itens usados
        "dado_puro": roll,            # Valor real que caiu no d20
        "atributo_valor": valor_atributo, # Valor do atributo (forca, carisma, etc)
        "atributo_nome": atr_usado.capitalize() # Nome do atributo usado
    }
    
    if sucesso:
        valor_base, _, _ = rolar_dado(formato_dado)
        valor_total = valor_base + valor_atributo + dano_extra
        
        if dados_hab.get("tipo") == "cura":
            resultado["cura"] = valor_total
        else:
            resultado["dano"] = valor_total
            
    return resultado