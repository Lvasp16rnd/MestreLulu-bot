# 🐾 Mestre Lulu - Discord RPG Bot

A **Lulu** é um bot de gerenciamento de RPG de mesa para Discord, focado em automação de fichas, progressão por interpretação (XP por texto) e mecânicas de combate dinâmicas.

## 🌟 Funcionalidades Principais

* **Sistema de XP por RP:** Ganho automático de 150 XP para mensagens interpretativas (acima de 1000 caracteres) com cooldown de 1 minuto.
* **Progressão Inteligente:** Curva de nível dinâmica (50% até lvl 5, 25% até lvl 10 e 15% até o 20).
* **Combate Automatizado:** Sistema de defesa (CA), redução de dano por escudo e item de ressurreição (Fada).
* **Gestão de Fichas:** Criação de personagens com distribuição de pontos e escolha de raças únicas.
* **Economia e Loja:** Sistema de Krugs (moeda), inventário e poções de sorte/tempo.
* **Ferramentas do Mestre:** Comandos para criar eventos globais, sorteios de missão e controle de atributos.

## 🏗️ Estrutura do Projeto

O projeto segue uma arquitetura modular baseada em **Cogs**:

📂 **Core**
- `main.py`: Ponto de entrada e sistema de XP por texto.
- `database.py`: Persistência de dados via JSON.
- `constantes.py`: Tabelas de preços, níveis, raças e habilidades.

📂 **Mecânicas (Cogs & Logics)**
- `mecanicas.py`: Lógica de cálculo de nível e XP.
- `logic.py`: Motor de combate, rolagem de dados e poções.
- `habilidades_logic.py`: Processamento técnico do uso de magias.

📂 **Comandos**
- `players.py`: Comandos de ficha, descanso e inventário.
- `mestre.py`: Comandos administrativos e narrativos.
- `sistema.py`: Registro, ajuda e loja.
- `habilidades.py`: Gerenciador de técnicas raciais.
- `combate.py`: Sistema de arena (PvP).

## 🚀 Como Executar

1. **Requisitos:** Python 3.8+ e uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications).

2. **Instalação:**
   ```bash
   pip install discord.py python-dotenv
   ```

3. **Configuração:** Crie um arquivo `.env` na raiz do projeto:
   ```env
   TOKEN=seu_token_aqui
   ADMINS=seu_id_aqui,outro_id
   ```

4. **Iniciar:**
   ```bash
   python main.py
   ```

## 📜 Regras de Progressão (XP)

O bot utiliza uma curva de aprendizado suave para manter o engajamento:

| Nível | XP Necessário |
|-------|---------------|
| 1-5   | +50% por nível |
| 6-10  | +25% por nível |
| 11-20 | +15% por nível |

---

*Lulu observa silenciosamente... boa jornada, aventureiro! 🐾*
