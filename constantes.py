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
        "Presilhas Trevo": {"preco": 550, "mod_dt_global": -3, "desc": "Diminui 3 da DT de todos os testes."}
    },
    "khaerun": {
        "Martelo do Eco Profundo": {"preco": 1200, "dado": "2d8", "desc": "Impacto reverberante."},
        "Escudo da Vigília Ancestral": {"preco": 1100, "escudo_bonus": 6, "desc": "+6 de Escudo."},
        "Marca da Exclusão": {"preco": 0, "custo_especial": "asa_fada + olho_dragao", "defesa": 7, "usos": 3}
    }
    # ... as outras seguem o mesmo padrão
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