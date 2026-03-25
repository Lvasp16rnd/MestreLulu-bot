# 🐾 Mestre Lulu - Discord RPG Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.6.4-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![License](https://img.shields.io/badge/License-CC0%201.0-lightgrey)](LICENSE)

O **Mestre Lulu** é um bot de RPG para Discord com sistema de progressão, combate e ferramentas para mestre, executando em produção em **Oracle Cloud Infrastructure (OCI)**.

## 🚀 Deploy em Oracle Cloud (Ubuntu VM)

### Pré-requisitos
- VM Ubuntu ativa na OCI
- Python 3.12+
- Git
- Aplicação no Discord Developer Portal
- Banco MongoDB Atlas (ou outra instância Mongo compatível)

### 1) Preparar servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

### 2) Clonar projeto

```bash
git clone https://github.com/seu-usuario/MestreLulu-bot.git
cd MestreLulu-bot
```

### 3) Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configurar variáveis de ambiente

Crie o arquivo `.env` na raiz:

```env
TOKEN=seu_token_do_discord
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/
ADMINS=123456789012345678,987654321098765432
ENABLE_HTTP_SERVER=false
```

> `ENABLE_HTTP_SERVER` é opcional. Deixe `false` na OCI se não precisar de endpoint de healthcheck.

### 5) Testar execução manual

```bash
source venv/bin/activate
python3 main.py
```

Se o bot subir corretamente, use `Ctrl + C` para encerrar e siga para serviço persistente.

### 6) Rodar 24/7 com systemd

Crie o serviço:

```bash
sudo nano /etc/systemd/system/mestrelulu.service
```

Conteúdo do arquivo (ajuste usuário/caminho se necessário):

```ini
[Unit]
Description=Mestre Lulu Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MestreLulu-bot
ExecStart=/home/ubuntu/MestreLulu-bot/venv/bin/python3 main.py
Restart=always
RestartSec=10
EnvironmentFile=/home/ubuntu/MestreLulu-bot/.env

[Install]
WantedBy=multi-user.target
```

Ative e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mestrelulu
sudo systemctl start mestrelulu
```

### 7) Operação diária

```bash
sudo systemctl status mestrelulu
sudo journalctl -u mestrelulu -f
sudo systemctl restart mestrelulu
sudo systemctl stop mestrelulu
```

## ✨ Funcionalidades principais

- XP por interpretação com cooldown
- Progressão de nível por curva dinâmica
- Sistema de combate com CA, escudo e efeitos
- Arena PvP
- Economia com Krugs, inventário e loja
- Comandos de administração para mestre

## 🏗️ Estrutura do projeto

```
MestreLulu-bot/
├── main.py
├── database.py
├── constantes.py
├── mecanicas.py
├── views.py
├── models.py
├── utils.py
├── cogs/
└── config.json
```

## 📄 Licença

Este projeto está licenciado sob a **CC0 1.0 Universal**. Consulte [LICENSE](LICENSE).
