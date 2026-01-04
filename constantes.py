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
    "Elfo": {
        "1-2": ["Visão da Floresta", "Reflexos Élficos"],
        "3-5": ["Caminho das Folhas", "Luz das Estrelas"],
        "6-10": ["Controle Vegetal", "Comunhão Ancestral"]
    },
    "Khaerun": {
        "1-2": ["Pele de Obsidiana", "Canto da Pedra Desperta"],
        "3-5": ["Olhos de Forja", "Forja Vivo-Ferro"],
        "6-10": ["Punho Rachado", "Pulso Mineral"]
    }
    # ... Adicionar as outras conforme sua lista
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