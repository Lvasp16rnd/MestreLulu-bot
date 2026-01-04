import discord
from discord.ext import commands
import asyncio
import json
import random
import os
from dotenv import load_dotenv

# Imports de Cogs e Views
from cogs.combate import BatalhaView
from views import LojaView, MenuRPG 
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import aplicar_dano_complexo, usar_pocao_sorte, rolar_dado

load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMINS_LIST = [int(id) for id in os.getenv("ADMINS", "").split(",") if id]

# --- CONFIGURAÇÃO ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
usuarios_em_menu = set()

def eh_admin(ctx):
    return ctx.author.id in ADMINS_LIST or ctx.author.guild_permissions.administrator

# --- EVENTOS ---
@bot.event
async def on_ready():
    print(f"🐾 Mestre Lulu online como {bot.user}")

@bot.command()
async def menu(ctx):
    # Verifica se o usuário já tem um menu aberto para não poluir o chat
    if ctx.author.id in usuarios_em_menu:
        return await ctx.reply("🐾 **Lulu:** Você já tem um menu aberto! Use-o ou espere ele expirar.")
    
    view = MenuRPG(ctx)
    usuarios_em_menu.add(ctx.author.id)
    
    # Define o que acontece quando o menu expira (timeout)
    async def on_timeout():
        usuarios_em_menu.discard(ctx.author.id)
    view.on_timeout = on_timeout

    await ctx.send(f"🐾 **Mestre Lulu observa...** O que deseja, {ctx.author.name}?", view=view)

# --- COMANDOS DE PERSONAGEM ---
@bot.command()
async def registrar(ctx):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    if user_id in dados["usuarios"]:
        return await ctx.send("🐾 **Mestre Lulu:** Você já possui uma alma registrada.")

    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.send(f"🐾 **Mestre Lulu:** Escolha sua linhagem:\n`{', '.join(constantes.RACAS.keys())}`")
        msg_raca = await bot.wait_for("message", timeout=60.0, check=check)
        raca_escolhida = msg_raca.content.capitalize()
        if raca_escolhida not in constantes.RACAS:
            return await ctx.send("🐾 **Mestre Lulu:** Essa raça não existe!")

        await ctx.send("🐾 **Mestre Lulu:** Distribua **7 pontos** (Força, Agilidade, Intelecto, Presença, Carisma).\nEx: `1 2 1 2 1`")
        msg_pts = await bot.wait_for("message", timeout=120.0, check=check)
        
        try:
            pts = [int(p) for p in msg_pts.content.split()]
            if len(pts) != 5 or sum(pts) != 7: raise ValueError
        except ValueError:
            return await ctx.send("🐾 **Mestre Lulu:** Matemática errada. Use 5 números que somam 7.")

        dados["usuarios"][user_id] = {
            "nome": ctx.author.name, "raca": raca_escolhida, "nivel": 1, 
            "pv": 30, "ca": 5, "dado_nivel": "1d6", "dinheiro": 500,
            "atributos": {"forca": pts[0], "agilidade": pts[1], "intelecto": pts[2], "presenca": pts[3], "carisma": pts[4]},
            "azarado": False, "inventario": []
        }
        salvar_dados(dados)
        await ctx.send(f"✨ **Mestre Lulu:** Ficha de {ctx.author.name} tecida.")
    except asyncio.TimeoutError:
        await ctx.send("🐾 **Mestre Lulu:** Tempo esgotado.")

@bot.command()
async def ficha(ctx, alvo: discord.Member = None):
    alvo = alvo or ctx.author
    p = carregar_dados()["usuarios"].get(str(alvo.id))
    if not p: return await ctx.send("🐾 **Lulu:** Sem ficha.")

    at = p["atributos"]
    sorte = p["nivel"] + (at.get("presenca", 0) * 2)
    embed = discord.Embed(title=f"📜 Ficha de {p['nome']}", color=0x71368a)
    embed.add_field(name="🧬 Raça/Nível", value=f"{p['raca']} Lvl {p['nivel']}", inline=True)
    embed.add_field(name="❤️ PV | 🛡️ Escudo", value=f"{p['pv']} | {p['ca']}", inline=True)
    embed.add_field(name="🍀 Sorte", value=str(sorte), inline=True)
    
    status = "💀 **AZARADO**" if p.get("azarado") else "✨ Normal"
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="🎲 Dado", value=p.get('dado_nivel', '1d6'), inline=True)
    
    attrs = f"FOR: {at['forca']} | AGI: {at['agilidade']} | INT: {at['intelecto']}\nPRE: {at['presenca']} | CAR: {at['carisma']}"
    embed.add_field(name="📊 Atributos", value=f"```\n{attrs}\n```", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def usar(ctx, *, habilidade: str):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    p = dados["usuarios"].get(user_id)
    if not p: return await ctx.send("🐾 **Lulu:** Sem alma.")

    # Verifica se tem a habilidade por nível
    hab_liberadas = []
    if p["raca"] in constantes.HABILIDADES_RACA:
        for faixa, lista in constantes.HABILIDADES_RACA[p["raca"]].items():
            if p["nivel"] >= int(faixa.split('-')[0]): hab_liberadas.extend(lista)

    if habilidade.title() not in hab_liberadas:
        return await ctx.send("🐾 **Lulu:** Você não conhece essa técnica ou é muito fraco.")

    # Rolagem com Azar Acumulado
    mod = -5 if p.get("azarado") else 0
    if p.get("azarado"): 
        p["azarado"] = False
        await ctx.send("⚠️ **O Azar Acumulado te atingiu! (-5)**")

    roll = random.randint(1, 20)
    total = max(1, roll + mod)
    dano = rolar_dado(p.get("dado_nivel", "1d6")) + p["atributos"]["forca"]

    msg = f"🎲 **{p['nome']}** usou **{habilidade}**! Resultado: **{total}**\n"
    if total <= 2: msg += "🌑 **RUÍNA!** O efeito ricocheteou."
    elif total <= 15: msg += f"⚠️ **COMPLICAÇÃO!** O efeito ocorre, mas com intercorrências. Dano: {dano//2}"
    elif total <= 19: msg += f"✅ **SUCESSO!** Ação realizada! Dano: {dano}"
    else: msg += f"🌟 **GLÓRIA!** Recompensas e efeito máximo! Dano: {dano * 2}"

    salvar_dados(dados)
    await ctx.send(msg)

@bot.command()
async def beber(ctx, *, item: str):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    p = dados["usuarios"].get(user_id)
    item_real = next((i for i in p["inventario"] if i.lower() == item.lower()), None)
    if not item_real: return await ctx.send("🐾 **Lulu:** Você não tem isso.")

    if item_real == "Poção da Sorte":
        p["inventario"].remove(item_real)
        res, _ = usar_pocao_sorte(p)
        salvar_dados(dados)
        await ctx.send(res)
    elif item_real == "Poção do Tempo Velado":
        p["inventario"].remove(item_real)
        cura = random.randint(5, 15)
        p["pv"] += cura
        salvar_dados(dados)
        await ctx.send(f"⏳ Tempo manipulado! Recuperou {cura} PV.")
    else: await ctx.send("🐾 **Lulu:** Isso não se bebe.")

# --- COMANDOS ADMIN ---
@bot.command()
async def upar(ctx, alvo: discord.Member, n: int = 1):
    if not eh_admin(ctx): return
    dados = carregar_dados()
    p = dados["usuarios"].get(str(alvo.id))
    if p:
        p["nivel"] += n
        for faixa, st in constantes.TABELA_NIVEIS.items():
            if int(faixa.split('-')[0]) <= p["nivel"] <= int(faixa.split('-')[1]):
                p["pv"], p["ca"], p["dado_nivel"] = st["pv"], st["ca"], st["dado"]
                break
        salvar_dados(dados)
        await ctx.send(f"✨ {alvo.name} subiu para Lvl {p['nivel']}! Dado: {p['dado_nivel']}")

@bot.command()
async def concluir_missao(ctx):
    if not eh_admin(ctx): return
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        await ctx.send("📝 Nome da Missão?")
        nome = (await bot.wait_for("message", timeout=30, check=check)).content
        await ctx.send("👥 Mencione os heróis:")
        herois = (await bot.wait_for("message", timeout=30, check=check)).mentions
        await ctx.send("💰 Krugs para cada um?")
        valor = int((await bot.wait_for("message", timeout=30, check=check)).content)

        dados = carregar_dados()
        for h in herois:
            if str(h.id) in dados["usuarios"]: dados["usuarios"][str(h.id)]["dinheiro"] += valor
        
        log = {"missao": nome, "herois": [h.name for h in herois], "data": str(discord.utils.utcnow())}
        dados.setdefault("missoes", []).append(log)
        salvar_dados(dados)
        await ctx.send(f"📜 Missão '{nome}' salva!")
    except: await ctx.send("🐾 **Lulu:** Erro no registro.")

@bot.command()
async def sorteio_missao(ctx):
    if not eh_admin(ctx): return
    dados = carregar_dados()
    candidatos = list(dados["usuarios"].values())
    random.shuffle(candidatos)
    equipe, racas = [], set()
    for c in candidatos:
        if c["raca"] not in racas:
            equipe.append(c["nome"])
            racas.add(c["raca"])
        if len(equipe) == 5: break
    if len(equipe) < 5: return await ctx.send("🐾 **Lulu:** Diversidade de raças insuficiente.")
    await ctx.send(f"⚔️ **Escolhidos:**\n" + "\n".join([f"🔸 {n}" for n in equipe]))

@bot.command()
async def loja(ctx):
    dados = carregar_dados()
    cat = constantes.LOJA_ITENS.copy()
    if "loja_custom" in dados:
        for c, it in dados["loja_custom"].items():
            if c in cat: cat[c].update(it)
            else: cat[c] = it
    await ctx.send("🐾 **Mestre Lulu:** Não toque em nada.", view=LojaView(cat))

@bot.command()
async def inventario(ctx):
    p = carregar_dados()["usuarios"].get(str(ctx.author.id))
    if not p: return await ctx.send("🐾 **Lulu:** Registre-se.")
    inv = ", ".join(p["inventario"]) if p["inventario"] else "Vazio"
    await ctx.send(embed=discord.Embed(title=f"🎒 {ctx.author.name}", description=f"**Itens:** {inv}\n**Saldo:** {p['dinheiro']} Krugs"))

@bot.command()
async def historico(ctx):
    missoes = carregar_dados().get("missoes", [])[-5:]
    if not missoes: return await ctx.send("🐾 **Lulu:** Sem história.")
    txt = "\n".join([f"🔹 **{m['missao']}**: {', '.join(m['herois'])}" for m in reversed(missoes)])
    await ctx.send(embed=discord.Embed(title="📖 Crônicas", description=txt))

@bot.command()
async def setar(ctx, alvo: discord.Member, at: str, v: int):
    if not eh_admin(ctx): return
    dados = carregar_dados()
    uid = str(alvo.id)
    if uid in dados["usuarios"]:
        if at.lower() in dados["usuarios"][uid]["atributos"]: dados["usuarios"][uid]["atributos"][at.lower()] = v
        else: dados["usuarios"][uid][at.lower()] = v
        salvar_dados(dados)
        await ctx.send(f"✅ {at} de {alvo.name} setado para {v}.")

bot.run(TOKEN)