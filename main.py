import discord
from discord.ext import commands
import asyncio
import json
import random
import os, time
import sys
from dotenv import load_dotenv

print("🚀 Iniciando bot...", flush=True)

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ERRO: TOKEN não encontrado no ambiente!", flush=True)
    sys.exit(1)

print(f"✅ Token carregado (primeiros 10 chars): {TOKEN[:10]}...", flush=True)

# Testa imports
try:
    from cogs.logic import processar_xp_acumulado
    print("✅ cogs.logic importado", flush=True)
except Exception as e:
    print(f"❌ Erro ao importar cogs.logic: {e}", flush=True)

try:
    from database import carregar_dados, salvar_dados
    print("✅ database importado", flush=True)
except Exception as e:
    print(f"❌ Erro ao importar database: {e}", flush=True)

try:
    from mecanicas import adicionar_xp 
    print("✅ mecanicas importado", flush=True)
except Exception as e:
    print(f"❌ Erro ao importar mecanicas: {e}", flush=True)

try:
    from views import MenuRPG
    print("✅ views importado", flush=True)
except Exception as e:
    print(f"❌ Erro ao importar views: {e}", flush=True)

# --- CONFIGURAÇÃO ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
usuarios_em_menu = set()
cooldown_xp = {}

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
    # Inicia keep-alive loop
    bot.loop.create_task(keep_alive_loop())

async def keep_alive_loop():
    """Mantém o bot ativo logando a cada 10 minutos."""
    while True:
        await asyncio.sleep(600)  # 10 minutos
        print(f"💓 Keep-alive: Bot ainda online - {time.strftime('%H:%M:%S')}")

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
    
    if agora - cooldown_xp.get(user_id, 0) > 60:
        dados = carregar_dados()
        if user_id in dados["usuarios"]:
            p = dados["usuarios"][user_id]
            
            p.setdefault("palavras_acumuladas", 0)
            p.setdefault("xp", 0)
            
            todas_palavras = message.content.split()
            palavras_filtradas = [palavra for palavra in todas_palavras if len(palavra) >= 4]
            contagem_valida = len(palavras_filtradas)
            
            if contagem_valida > 0:
                p["palavras_acumuladas"] += contagem_valida
                
                META_PALAVRAS = 100000 
                XP_RECOMPENSA = 100

                if p["palavras_acumuladas"] >= META_PALAVRAS:
                    premios = p["palavras_acumuladas"] // META_PALAVRAS
                    xp_total_ganho = premios * XP_RECOMPENSA
                    
                    p["palavras_acumuladas"] %= META_PALAVRAS
                    
                    upou = processar_xp_acumulado(p, xp_total_ganho)
                    
                    cooldown_xp[user_id] = agora
                    salvar_dados(dados)

                    if upou:
                        await message.channel.send(f"🎊 **{p['nome']}** atingiu a meta de escrita e subiu para o nível **{p['nivel']}**!")
                    else:
                        await message.channel.send(f"📖 **RP Acumulado!** {p['nome']} completou {META_PALAVRAS} palavras relevantes e ganhou {xp_total_ganho} XP.", delete_after=10)
                else:
                    salvar_dados(dados)

    await bot.process_commands(message)

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Comandos sincronizados!")

# === SERVIDOR HTTP FAKE PARA RENDER ===
from aiohttp import web

async def health_check(request):
    return web.Response(text="🐾 Mestre Lulu está online!")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Servidor HTTP rodando na porta {port}")

async def main():
    print("🔄 Entrando em main()...", flush=True)
    try:
        async with bot:
            print("🔄 Carregando extensões...", flush=True)
            await load_extensions()
            print("🔄 Iniciando servidor web...", flush=True)
            await run_web_server()
            print("🔄 Iniciando bot Discord...", flush=True)
            await bot.start(TOKEN)
    except Exception as e:
        print(f"❌ ERRO FATAL em main(): {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔄 Executando asyncio.run(main())...", flush=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass