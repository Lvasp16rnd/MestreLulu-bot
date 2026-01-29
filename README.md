# 🐾 Mestre Lulu - Discord RPG Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.6.4-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-CC0%201.0-lightgrey)](LICENSE)

O **Mestre Lulu** é um bot completo de gerenciamento de RPG de mesa para Discord, focado em automação de fichas, progressão por interpretação (XP por texto) e mecânicas de combate dinâmicas.

## ✨ Funcionalidades Principais

### 🎭 Sistema de Roleplay
- **XP por Interpretação:** Ganho automático de 100 XP para mensagens interpretativas (acima de 100000 caracteres) com cooldown de 1 minuto
- **Progressão Inteligente:** Curva de nível dinâmica (50% até lvl 5, 25% até lvl 10 e 15% até o 20)
- **Testes de Atributo:** Sistema de rolagem com FOR, AGI, INT, PRE e CAR

### ⚔️ Combate
- **Sistema de Defesa (CA):** Cálculo automático de armadura e defesa
- **Redução de Dano:** Escudos que escalam com nível (1d6 → 2d8)
- **Arena PvP:** Sistema de combate entre jogadores
- **Ressurreição:** Item especial da raça Fada

### 🧙 Raças e Habilidades
| Raça | Especialidade |
|------|---------------|
| 🧝 **Elfo** | Arqueiros e Magia Natural |
| ⚒️ **Khaerun** | Armas vivas e combate pesado |
| 🧚 **Fada** | Cura e Ilusões |
| 👤 **Humano** | Diplomacia e Alquimia |
| 💀 **Fragmentado** | Magia Sombria |
| 🕷️ **Drow** | Venenos e Espionagem |
| 🔮 **Bruxa** | Maldições e Necromancia |

### 💰 Economia
- **Moeda (Krugs):** Sistema de economia com trabalho e recompensas
- **Loja Dinâmica:** Itens específicos por raça com bônus únicos
- **Inventário:** Gerenciamento de poções e itens mágicos

### 🎮 Ferramentas do Mestre
- Comandos administrativos para controle de atributos e XP
- Sorteio de equipes diversificadas para missões
- Sistema de reset de descansos e maldições

## 🏗️ Arquitetura do Projeto

O projeto segue uma arquitetura modular baseada em **Cogs** do discord.py:

```
MestreLulu-bot/
├── 📄 main.py              # Ponto de entrada e sistema de XP por texto
├── 📄 database.py          # MongoDB Atlas com cache local
├── 📄 constantes.py        # Raças, habilidades, preços e progressão
├── 📄 mecanicas.py         # Lógica de cálculo de nível e XP
├── 📄 views.py             # Menus interativos (Buttons/Selects)
├── 📄 models.py            # Modelos de dados
├── 📄 utils.py             # Funções utilitárias
│
├── 📁 cogs/                # Módulos de comandos
│   ├── players.py          # !ficha, !inventario, !descansar, !trabalhar, !dado
│   ├── mestre.py           # !upar, !dar_xp, !setar, !sorteio_missao (ADMs)
│   ├── sistema.py          # !registrar, !loja, !lulu_ajuda
│   ├── habilidades.py      # Gerenciador de técnicas raciais
│   ├── combate.py          # Sistema de arena PvP
│   └── logic.py            # Motor de combate e rolagem
│
└── 📄 config.json          # Configurações do bot
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.12+
- Conta no [MongoDB Atlas](https://www.mongodb.com/atlas) (gratuito)
- Aplicação no [Discord Developer Portal](https://discord.com/developers/applications)

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/MestreLulu-bot.git
   cd MestreLulu-bot
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   TOKEN=seu_token_do_discord
   MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/
   ```

4. **Inicie o bot:**
   ```bash
   python main.py
   ```

## 📋 Comandos Principais

### 👤 Jogadores
| Comando | Descrição |
|---------|-----------|
| `!registrar` | Registra um novo personagem |
| `!ficha` | Mostra sua ficha de personagem |
| `!inventario` | Exibe itens e saldo |
| `!descansar` | Recupera pontos de vida |
| `!trabalhar` | Trabalha para ganhar Krugs |
| `!dado 2d6` | Rola dados (suporta `3#d12`) |
| `!testar FOR` | Faz teste de atributo |
| `!beber [item]` | Usa um item do inventário |
| `!loja` | Mostra itens disponíveis |

### 🎭 Mestres (ADMs)
| Comando | Descrição |
|---------|-----------|
| `!upar @user` | Sobe o nível de um jogador |
| `!dar_xp @user [qtd]` | Concede XP e processa níveis |
| `!setar @user [attr] [valor]` | Define atributos, nível ou XP |
| `!lulu_reset` | Restaura descansos de todos |
| `!lulu_azar @user` | Aplica maldição (-5 na próxima rolagem) |
| `!sorteio_missao` | Sorteia equipe diversificada |
| `!concluir_missao` | Finaliza missão e distribui recompensas |

## 📊 Sistema de Progressão

### Curva de XP
| Nível | Incremento de XP |
|-------|------------------|
| 1-5   | +50% por nível |
| 6-10  | +25% por nível |
| 11-20 | +15% por nível |

### Progressão de Status
| Nível | PV | Escudo | Dados |
|-------|-----|--------|----------------|
| 1-5   | 30  | 5      | 1d6 |
| 6-10  | 60  | 7      | 1d8 |
| 11-15 | 80  | 9      | 2d6 |
| 16-20 | 100 | 11     | 2d8 |

## 🛠️ Tecnologias

- **[discord.py](https://discordpy.readthedocs.io/)** - Biblioteca principal para Discord
- **[MongoDB Atlas](https://www.mongodb.com/atlas)** - Banco de dados na nuvem
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Gerenciamento de variáveis de ambiente

## 📄 Licença

Este projeto está licenciado sob a **CC0 1.0 Universal** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

*🐾 Lulu observa silenciosamente... boa jornada, aventureiro!*

</div>
