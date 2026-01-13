import discord
from discord.ext import commands
import asyncio
import json
import random
import os, time
from dotenv import load_dotenv

# Imports de banco e lógica
from database import carregar_dados, salvar_dados
from mecanicas import adicionar_xp # Mantendo apenas este
from views import MenuRPG 

load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMINS_LIST = [int(id) for id in os.getenv("ADMINS", "").split(",") if id]

# --- CONFIGURAÇÃO ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
usuarios_em_menu = set()
cooldown_xp = {}

def eh_admin(ctx):
    return ctx.author.id in ADMINS_LIST or ctx.author.guild_permissions.administrator

# --- CARREGAMENTO DE COGS ---
async def load_extensions():
    extensions = ["cogs.players", "cogs.mestre", "cogs.combate", "cogs.sistema", "cogs.habilidades"]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Cog {ext} carregada!")
        except Exception as e:
            print(f"❌ Erro ao carregar {ext}: {e}")

# --- EVENTOS ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🐾 Mestre Lulu online como {bot.user}")

@bot.command()
async def menu(ctx):
    if ctx.author.id in usuarios_em_menu:
        return await ctx.reply("🐾 **Lulu:** Você já tem um menu aberto!")
    
    view = MenuRPG(ctx)
    usuarios_em_menu.add(ctx.author.id)
    
    async def on_timeout():
        usuarios_em_menu.discard(ctx.author.id)
    view.on_timeout = on_timeout

    await ctx.send(f"🐾 **Mestre Lulu observa...** O que deseja, {ctx.author.name}?", view=view)
    await view.wait()
    usuarios_em_menu.discard(ctx.author.id)

@bot.event
async def on_message(message):
    if message.author.bot: return

    user_id = str(message.author.id)
    agora = time.time()
    
    # Sistema de XP por texto
    if agora - cooldown_xp.get(user_id, 0) > 60:
        dados = carregar_dados()
        if user_id in dados["usuarios"]:
            p = dados["usuarios"][user_id]
            if len(message.content) >= 1000:
                cooldown_xp[user_id] = agora 
                
                # Garante que os campos existem
                if "xp" not in p: p["xp"] = 0
                if "xp_max" not in p: p["xp_max"] = 500
                
                if adicionar_xp(p, 150): # Usa a lógica do mecanicas.py
                    await message.channel.send(f"🎊 **{p['nome']}** subiu para o nível **{p['nivel']}**!")
                else:
                    await message.channel.send(f"📖 **RP Recompensado!** {p['nome']} ganhou 150 XP.", delete_after=10)
                
                salvar_dados(dados)

    await bot.process_commands(message)

async def main():
    async with bot:
        await load_extensions() 
        await bot.start(TOKEN)  

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass