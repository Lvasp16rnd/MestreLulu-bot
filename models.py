import json
import random

class Raca:
    def __init__(self, nome, descricao, especialidade, fraqueza=None):
        self.nome = nome
        self.descricao = descricao
        self.especialidade = especialidade
        self.fraqueza = fraqueza

class Item:
    def __init__(self, nome, valor, descricao, atributos=None, consumo=None):
        self.nome = nome
        self.valor = valor
        self.descricao = descricao
        self.atributos = atributos or {}  # Ex: {"forca": 2}
        self.consumo = consumo or {}      # Ex: {"vida": 10}

class Personagem:
    def __init__(self, user_id, nome, raca, idade=20, classe_social="Errante"):
        self.user_id = user_id
        self.nome = nome
        self.raca = raca  # Objeto da classe Raca
        self.idade = idade
        self.nivel = 1
        self.dinheiro = 500
        self.vida_max = 30
        self.vida_atual = 30
        self.magia = 10
        self.inventario = []
        # Atributos (Sistema Ordem Paranormal - 10 pontos iniciais)
        self.atributos = {
            "presenca": 0,
            "forca": 0,
            "agilidade": 0,
            "intelecto": 0,
            "carisma": 0
        }

    def calcular_sorte(self):
        # A sorte depende do nível e bônus de raça/itens
        base_sorte = self.nivel + (self.atributos["presenca"] * 2)
        return base_sorte

    def to_dict(self):
        """Converte o objeto para dicionário para salvar no JSON"""
        return {
            "user_id": self.user_id,
            "nome": self.nome,
            "raca": self.raca.nome,
            "nivel": self.nivel,
            "dinheiro": self.dinheiro,
            "atributos": self.atributos,
            "inventario": [item.nome for item in self.inventario]
        }
    
    