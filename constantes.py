# constantes.py

# Definição das Raças e bônus iniciais
RACAS = {
    "Elfo": "Altos e magros, conectados à natureza. Especialidade: Arqueiros e Magia Natural.",
    "Khaerun": "Pele mineral e olhos incandescentes. Especialidade: Armas vivas e combate pesado.",
    "Fada": "Seres luminosos e delicados. Especialidade: Cura e Ilusões.",
    "Humano": "Versáteis e determinados. Especialidade: Diplomacia e Alquimia.",
    "Fragmentado": "Distorcidos e misteriosos. Especialidade: Magia Sombria.",
    "Drow": "Furtivos e ambiciosos. Especialidade: Venenos e Espionagem.",
    "Bruxa": "Sabedoria ancestral. Especialidade: Maldições e Necromancia."
}

HABILIDADES_RACA = {
    "Bruxa": {
        "1-2": ["Transmutação Sombria", "Olho do Véu"],
        "3-4": ["Magia de Sangue", "Invocação Elemental"],
        "5-6": ["Maldição da Lua", "Voo da Vassoura"],
        "7-8": ["Necro-Comunhão", "Chamas Etéreas"],
        "9-10": ["Espelho das Almas", "Poções Vivas"]
    },
    "Fada": {
        "1-2": ["Luz de Cura", "Sussurro do Vento"],
        "3-4": ["Pó Encantado", "Toque da Primavera"],
        "5-6": ["Riso da Confusão", "Espelho da Bruma"],
        "7-8": ["Encantamento Musical", "Passos Invisíveis"],
        "9-10": ["Dom da Sorte", "Lágrima Estelar"]
    },
    "Elfo": {
        "1-2": ["Visão da Floresta", "Flecha Celeste"],
        "3-4": ["Caminho das Folhas", "Comunhão Ancestral"],
        "5-6": ["Encanto da Harmonia", "Cântico de Renovação"],
        "7-8": ["Controle Vegetal", "Luz das Estrelas"],
        "9-10": ["Reflexos Élficos", "Aura de Pureza"]
    },
    "Drow": {
        "1-2": ["Sombra Viva", "Veneno Abissal"],
        "3-4": ["Magia de Crueldade", "Olhar do Terror"],
        "5-6": ["Domínio da Escuridão", "Chicote dos Subterrâneos"],
        "7-8": ["Armadilha das Teias", "Voz Enfeitiçadora"],
        "9-10": ["Portão das Profundezas", "Resistência Sombria"]
    },
    "Humano": {
        "1-2": ["Rastreador Urbano", "Mestre de Armas"],
        "3-4": ["Poção de Cura Comprada", "Bolsa de Truques Alquímicos"],
        "5-6": ["Preparação de Emboscada", "Determinação Humana"],
        "7-8": ["Instinto de Sobrevivência", "Poção de Ataque Comprada"],
        "9-10": ["Medicina Improvisada", "Tiro Preciso"]
    },
    "Fragmentado": {
        "1-2": ["Ecos da Alma Quebrada", "Cicatriz que Vive"],
        "3-4": ["Olhar da Ruptura", "Vozes do Fragmento"],
        "5-6": ["Rasgo Involuntário", "Presença Fraturada"],
        "7-8": ["Empatia Ruinosa", "Alma Desalinhada"],
        "9-10": ["Ruptura Mental", "Mimese Quebrada"]
    },
    "Khaerun": {
        "1-2": ["Forja Vivo-Ferro", "Canto da Pedra Desperta"],
        "3-4": ["Pele de Obsidiana", "Olhos de Forja"],
        "5-6": ["Punho Rachado", "Arma da Essência"],
        "7-8": ["Eco da Montanha", "Pulso Mineral"],
        "9-10": ["Coração da Bigorna", "Despertar da Forja Profunda"]
    }
}

DIFICULDADES = {
    "Fácil": 14,
    "Média": 15,
    "Difícil": 16
}

# Tabelas de Progressão baseadas no seu novo sistema
PROGRESSAO = {
    "1-5":  {"pv": 30, "escudo": 5, "dado_escudo": "1d6"},
    "6-10": {"pv": 60, "escudo": 7, "dado_escudo": "1d8"},
    "11-15": {"pv": 80, "escudo": 9, "dado_escudo": "2d6"},
    "16-20": {"pv": 100, "escudo": 11, "dado_escudo": "2d8"}
}

# Itens com Atributos Técnicos para o Código
LOJA_ITENS = {
    "elfos": {
        "Flechas de Sol": {"preco": 180, "dano_bonus": 3, "desc": "+3 de dano. Rapidez solar."},
        "Sangue do Cupido": {"preco": 700, "mod_dt": -2, "desc": "Diminui 2 da DT do teste."},
        "Presilhas Trevo": {"preco": 550, "mod_dt_global": -3, "desc": "Diminui 3 da DT de todos os testes."},
        "Brincos de Frey": {"preco": 560, "carisma_bonus": 3, "duracao": "cena", "desc": "+3 de carisma em todo teste durante uma cena."},
        "Meias do Desaparecimento Parcial": {"preco": 600, "efeito": "invisibilidade_parcial", "desc": "Torna o usuário invisível da cintura para baixo."},
        "Cenouras Cantantes": {"preco": 120, "efeito": "atordoar", "quantidade": 3, "desc": "Grito afinado que atordoa inimigos."}
    },
    "khaerun": {
        "Martelo do Eco Profundo": {"preco": 1200, "dado": "2d8", "desc": "Impacto reverberante. Pode derrubar ou atordoar."},
        "Escudo da Vigília Ancestral": {"preco": 1100, "escudo_bonus": 6, "desc": "+6 de Escudo. Resistência extrema."},
        "Machado das Runas de Sangue": {"preco": 1500, "dano_portador": "1d4", "dano_adversario": "1d10", "desc": "-1d4 no portador, 1d10 no adversário + dano perdido."},
        "Elmo da Rocha Silenciosa": {"preco": 950, "presenca_bonus": 2, "agilidade_bonus": 2, "desc": "+2 presença e agilidade. Imunidade a medo e intimidação."},
        "Corrente do Conselho Partido": {"preco": 600, "efeito": "autoridade_ancestral", "desc": "Impõe respeito em assembleias e negociações."},
        "Proibida": {"preco": 1900, "dado_area": "1d30", "alcance": 10, "desc": "+1d30 de dano em área (10m). Mercadoria proibida."}
    },
    "fadas": {
        "Véu da Última Lembrança": {"preco": 450, "efeito": "imunidade_medo", "desc": "Apaga lembrança dolorosa. Imunidade a medo, culpa ou trauma."},
        "Pulseiras do Batimento Lúmino": {"preco": 350, "carisma_bonus": 3, "desc": "+3 de carisma. Aumenta empatia e persuasão."},
        "Frasco de Luz Engarrafada": {"preco": 300, "dado_dano": "1d6", "alvo": "coracoes_corrompidos", "desc": "1d6 de dano em corações corrompidos. Purifica maldições."},
        "Asas de Orvalho Esquecido": {"preco": 520, "efeito": "levitacao", "desc": "Levitação e movimento silencioso."},
        "Colar do Nome Verdadeiro": {"preco": 480, "dt_mentira": 18, "desc": "DT 18 para qualquer um que quiser mentir para o usuário."},
        "Sementes do Recomeço Lento": {"preco": 250, "dado_cura_area": "1d15", "alvos_max": 3, "desc": "+1d15 de cura em área (até 3 criaturas)."}
    },
    "bruxas": {
        "Poção do Amor": {"preco": 266, "efeito": "fascinacao", "duracao": "1 dia", "desc": "Atração intensa. Elo de fascínio por um dia."},
        "Poção do Esquecimento": {"preco": 350, "efeito": "apagar_memoria", "desc": "Apaga lembranças específicas."},
        "Poção da Raiva": {"preco": 300, "efeito": "furia", "duracao": "1 dia", "desc": "Fúria ardente contra um indivíduo por um dia."},
        "Poção da Verdade": {"preco": 550, "efeito": "revelar_verdade", "desc": "Obriga a revelar pensamentos íntimos. Impossibilita mentiras."},
        "Poção da Sorte": {"preco": 170, "efeito": "sorte", "desc": "Ganha moedas ou item aleatório."},
        "Poção do Tempo Velado": {"preco": 500, "dado_cura": "1d10", "desc": "+1d10 de vida. Manipula o próprio tempo."}
    },
    "drows": {
        "Lâminas Irmãs de Ardósia": {"preco": 700, "dado": "2d6", "efeito": "sangramento_cegueira", "desc": "2d6 de dano. Sangramento progressivo e cegueira temporária."},
        "Manto da Penumbra Vingativa": {"preco": 480, "efeito": "invisibilidade_parcial", "desc": "Invisibilidade parcial em sombras. Bônus em ataques surpresa."},
        "Anel do Exílio Antigo": {"preco": 350, "dado_dano": "1d6", "alvos": ["Elfo", "Fada", "Khaerun"], "desc": "+1d6 de dano em Elfos, Fadas, Khaerun."},
        "Veneno da Lua Incerta": {"preco": 200, "efeito_sucesso": "paralisia_inimigo", "efeito_falha": "paralisia_usuario", "desc": "Sucesso/Glória: paralisa inimigo. Falha/Ruína: paralisa usuário."},
        "Oráculo de Obsidiana Quebrada": {"preco": 420, "efeito": "prever_movimento", "desc": "Prevê o próximo movimento de um inimigo."},
        "Capa do Passo Arriscado": {"preco": 400, "efeito": "atravessar_vigiados", "usos_por_noite": 1, "desc": "Atravessa áreas vigiadas sem ser notado. 1 uso por noite."}
    },
    "humanos": {
        "Espada do Juramento Quebrado": {"preco": 650, "dado": "1d8", "desc": "1d8 de dano. Maior dano com culpa/arrependimento."},
        "Broche da Bandeira Invisível": {"preco": 280, "presenca_bonus": 5, "desc": "+5 de presença. Bônus de moral e liderança."},
        "Frascos de Alquimia Errante": {"preco": 400, "dado_cura": "1d4", "efeito": "colateral_aleatorio", "desc": "1d4 de cura + efeito colateral aleatório."},
        "Dado do Destino Ambulante": {"preco": 250, "efeito_sucesso": "bonus_elevado_ou_sucesso_auto", "efeito_falha": "complicacoes_narrativas", "desc": "Teste de Sorte: Sucesso = bônus. Falha = complicações."},
        "Poção do Quase Milagre": {"preco": 3000, "dado_cura": "1d20", "efeito_sucesso": "recuperacao_surpreendente", "efeito_falha": "cura_incompleta", "desc": "1d20 de cura. Teste de Sorte determina eficácia."},
        "Contrato de Areia": {"preco": 200, "efeito_sucesso": "acordo_favoravel", "efeito_falha": "clausulas_ocultas", "desc": "Vantagem em negociações. Teste de Sorte."}
    },
    "fragmentados": {
        "Sino da Repulsão Abissal": {"preco": 800, "efeito": "expulsar_nao_humanos", "desc": "Expulsa criaturas não humanas em área ampla."},
        "Cinzas do Nome Perdido": {"preco": 600, "efeito": "repelir_especies", "desc": "Força criaturas de outras espécies a recuar."},
        "Marca da Exclusão": {"preco": 0, "custo_especial": "asa_fada + olho_dragao", "defesa": 7, "usos": 3, "desc": "+7 de defesa. Protege 3 ataques. Espécies não humanas não se aproximam."}
    }
}

# Itens que podem ser ganhos ao usar a Poção da Sorte (itens de tier baixo/médio)
RECOMPENSAS_SORTE = [
    "Flechas de Sol", 
    "Cenouras Cantantes", 
    "Frascos de Alquimia Errante", 
    "Veneno da Lua Incerta",
    "Sementes do Recomeço Lento"
]

VALOR_SORTE_MOEDAS = (50, 300) # Min e Max de moedas

TABELA_NIVEIS = {
    "1-2":   {"pv": 30, "ca": 5,  "dado": "1d6"},
    "3-5":   {"pv": 30, "ca": 5,  "dado": "1d8"},
    "6-10":  {"pv": 60, "ca": 7,  "dado": "2d6"},
    "11-15": {"pv": 80, "ca": 9,  "dado": "2d8"},
    "16-20": {"pv": 100, "ca": 11, "dado": "3d6"}
}