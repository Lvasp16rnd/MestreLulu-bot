import discord
from discord.ext import commands
import asyncio
import json
import random
import os
from dotenv import load_dotenv
from views import SelecaoRacaView, DistribuiPontosView

# Imports de Cogs e Views
from cogs.combate import BatalhaView
from views import LojaView, MenuRPG 
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import aplicar_dano_complexo, calcular_dano_nivel, usar_pocao_sorte, rolar_dado

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
    if ctx.author.id in usuarios_em_menu:
        return await ctx.reply("🐾 **Lulu:** Você já tem um menu aberto! Use-o ou espere ele expirar.")
    
    view = MenuRPG(ctx)
    usuarios_em_menu.add(ctx.author.id)
    
    async def on_timeout():
        usuarios_em_menu.discard(ctx.author.id)
    view.on_timeout = on_timeout

    await ctx.send(f"🐾 **Mestre Lulu observa...** O que deseja, {ctx.author.name}?", view=view)

    await view.wait()
    usuarios_em_menu.discard(ctx.author.id)

# --- COMANDOS DE PERSONAGEM ---
@bot.command()
async def registrar(ctx):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    if user_id in dados["usuarios"]:
        return await ctx.send("🐾 **Mestre Lulu:** Tu já tens uma ficha.")

    # 1. Seleção de Raça
    view_raca = SelecaoRacaView(list(constantes.RACAS.keys()))
    msg = await ctx.send("🐾 **Mestre Lulu:** Escolha sua linhagem:", view=view_raca)
    await view_raca.wait()
    
    if not view_raca.raca_escolhida:
        return await msg.edit(content="🐾 **Lulu:** Tempo esgotado.", view=None)

    raca = view_raca.raca_escolhida

    # 2. Distribuição de Pontos
    view_pts = DistribuiPontosView(ctx, raca)
    await msg.edit(content=None, embed=view_pts.gerar_embed(), view=view_pts)
    await view_pts.wait()

    if not view_pts.finalizado:
        return await msg.edit(content="🐾 **Lulu:** Cancelado por inatividade.", embed=None, view=None)

    # 3. Salvando Tudo
    # Mapeamos os nomes da View para as chaves do Banco de Dados
    res = view_pts.attrs
    dados["usuarios"][user_id] = {
        "nome": ctx.author.name,
        "raca": raca,
        "nivel": 1, 
        "pv": 30,
        "descansos": 3,
        "ca": 5, 
        "dado_nivel": "1d6", 
        "dinheiro": 500,
        "atributos": {
            "forca": res["Força"], 
            "agilidade": res["Agilidade"], 
            "intelecto": res["Intelecto"], 
            "presenca": res["Presença"], 
            "carisma": res["Carisma"]
        },
        "azarado": False, 
        "inventario": []
    }
    
    salvar_dados(dados)
    await msg.edit(content=f"✨ **Mestre Lulu:** Ficha de {ctx.author.name} gravada! Bem-vindo ao RPG.", embed=None, view=None)
      
@bot.command()
async def ficha(ctx, alvo: discord.Member = None):
    alvo = alvo or ctx.author
    p = carregar_dados()["usuarios"].get(str(alvo.id))
    if not p: return await ctx.send("🐾 **Lulu:** Sem ficha.")

    at = p["atributos"]
    sorte = p["nivel"] + (at.get("presenca", 0) * 2)
    descansos = p.get("descansos", 0)

    embed = discord.Embed(title=f"📜 Ficha de {p['nome']}", color=0x71368a)
    embed.add_field(name="🧬 Raça/Nível", value=f"{p['raca']} Lvl {p['nivel']}", inline=True)
    
    embed.add_field(name="❤️ PV | 🛡️ Escudo | ⛺", value=f"{p['pv']} | {p['ca']} | ({descansos})", inline=True)
    embed.add_field(name="🍀 Sorte", value=str(sorte), inline=True)
    
    status = "💀 **AZARADO**" if p.get("azarado") else "✨ Normal"
    embed.add_field(name="Status", value=status, inline=True)
    
    dado_atual = calcular_dano_nivel(p["nivel"])
    embed.add_field(name="🎲 Dado Atual", value=dado_atual, inline=True)
    
    attrs = f"FOR: {at['forca']} | AGI: {at['agilidade']} | INT: {at['intelecto']}\nPRE: {at['presenca']} | CAR: {at['carisma']}"
    embed.add_field(name="📊 Atributos", value=f"```\n{attrs}\n```", inline=False)
    embed.set_footer(text="Use !descansar para recuperar fôlego (consome ⛺)")
    
    await ctx.send(embed=embed)

@bot.command()
async def usar(ctx, *, habilidade: str):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    p = dados["usuarios"].get(user_id)
    if not p: return await ctx.send("🐾 **Lulu:** Sem alma.")

    # 1. VALIDAÇÃO DE NÍVEL (Seu código mantido)
    hab_liberadas = []
    if p["raca"] in constantes.HABILIDADES_RACA:
        for faixa, lista in constantes.HABILIDADES_RACA[p["raca"]].items():
            if p["nivel"] >= int(faixa.split('-')[0]): 
                hab_liberadas.extend([h.lower() for h in lista])

    if habilidade.lower() not in hab_liberadas:
        return await ctx.send(f"🐾 **Lulu:** Você não conhece '{habilidade}' ou seu nível ({p['nivel']}) é baixo demais.")

    # 2. CARREGAR DADOS DO JSON
    try:
        with open("habilidades.json", "r", encoding="utf-8") as f:
            biblioteca = json.load(f)
        dados_hab = biblioteca.get(p["raca"], {}).get(habilidade.title())
    except Exception:
        return await ctx.send("⚠️ **Erro:** Verifique o arquivo habilidades.json.")

    if not dados_hab:
        return await ctx.send(f"⚠️ **Erro:** '{habilidade}' não detalhada no JSON.")

    # 3. SISTEMA DE AZAR (Seu código mantido)
    mod = -5 if p.get("azarado") else 0
    if p.get("azarado"): 
        p["azarado"] = False
        await ctx.send("⚠️ **O Azar Acumulado te atingiu! (-5)**")

    # 4. ROLAGENS
    roll = random.randint(1, 20)
    total = max(1, roll + mod)
    dt_alvo = dados_hab["dt"]
    
    embed = discord.Embed(title=f"✨ {p['nome']} usou {habilidade.title()}", color=0x3498db)
    
    # 5. RESULTADOS (Sucesso)
    if total >= dt_alvo:
        # Verifica se a habilidade tem um dado fixo (ex: 1d6) ou usa o dano por nível
        formato_dado = dados_hab.get("valor_fixo", calcular_dano_nivel(p["nivel"]))
        valor_base = rolar_dado(formato_dado)
        total_gerado = valor_base + p["atributos"]["forca"]
        
        embed.color = discord.Color.green()
        
        # Se for tipo Cura, aplica no PV automaticamente
        if dados_hab.get("tipo") == "cura":
            p["pv"] = min(p["pv_max"], p["pv"] + total_gerado)
            embed.description = f"✅ **Sucesso!** (Rolagem: {total})\n{dados_hab['descricao']}\n\n💖 **Cura:** +{total_gerado} PV | ❤️ **Vida:** {p['pv']}/{p['pv_max']}"
        else:
            embed.description = f"✅ **Sucesso!** (Rolagem: {total})\n{dados_hab['descricao']}\n\n⚔️ **Resultado:** {total_gerado}"
            
    # 6. RESULTADOS (Falha)
    else:
        d4 = random.randint(1, 4)
        consequencia = dados_hab["falha_1_2"] if d4 <= 2 else dados_hab["falha_3_4"]
        
        # Se a falha causar dano (1d4), aplica no PV automaticamente
        dano_falha_texto = ""
        if "1d4" in consequencia:
            perda = random.randint(1, 4)
            p["pv"] = max(0, p["pv"] - perda)
            dano_falha_texto = f"\n💔 **Recuo:** -{perda} PV"

        embed.color = discord.Color.red()
        embed.description = f"❌ **Falha!** (Rolagem: {total})\n**Dado de Falha (d4):** {d4}\n\n**O que aconteceu:** {consequencia}{dano_falha_texto}"

    salvar_dados(dados)
    await ctx.send(embed=embed)

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
        # BÔNUS DE DESCANSO: Ganha 1 carga por nível subido
        p["descansos"] = p.get("descansos", 0) + n
        
        for faixa, st in constantes.TABELA_NIVEIS.items():
            f_inicio = int(faixa.split('-')[0])
            f_fim = int(faixa.split('-')[1])
            
            if f_inicio <= p["nivel"] <= f_fim:
                # Atualiza PV Máximo e CA conforme a tabela
                p["pv_max"] = st["pv"] 
                p["ca"] = st["ca"]
                p["dado_nivel"] = st["dado"]
                
                # Opcional: Curar o jogador totalmente ao upar
                p["pv"] = p["pv_max"] 
                break
        
        salvar_dados(dados)
        
        embed = discord.Embed(
            title="🎊 NOVO NÍVEL ALCANÇADO!",
            description=f"**{alvo.name}** agora é Nível **{p['nivel']}**!",
            color=0x00ff00
        )
        embed.add_field(name="🎲 Novo Dado", value=p['dado_nivel'], inline=True)
        embed.add_field(name="⛺ Bônus", value=f"+{n} Carga de Descanso", inline=True)
        embed.add_field(name="❤️ Vida Atualizada", value=f"{p['pv']}/{p['pv_max']}", inline=False)
        embed.set_footer(text="A Lulu está orgulhosa do seu progresso!")
        
        await ctx.send(embed=embed)

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

# --- SISTEMA DE COMBATE (ARENA) ---
@bot.command()
async def batalha(ctx, op1: discord.Member, op2: discord.Member):
    """Inicia um duelo entre dois jogadores usando a BatalhaView."""
    if not eh_admin(ctx): 
        return await ctx.send("🐾 **Lulu:** Apenas mestres podem abrir a arena.")
        
    dados = carregar_dados()
    p1 = dados["usuarios"].get(str(op1.id))
    p2 = dados["usuarios"].get(str(op2.id))

    if not p1 or not p2:
        return await ctx.send("🐾 **Lulu:** Ambos os duelistas precisam de uma ficha registrada.")

    # Injetamos os IDs para a View saber quem é quem
    p1["user_id"], p2["user_id"] = str(op1.id), str(op2.id)

    # Criamos a arena (Aqui o BatalhaView é finalmente acessado!)
    view = BatalhaView(ctx.author, p1, p2, dados)
    
    embed = discord.Embed(
        title="⚔️ ARENA DE OCULTA ⚔️",
        description=f"O duelo entre **{p1['nome']}** e **{p2['nome']}** começou!",
        color=0xff0000
    )
    embed.add_field(name=p1['nome'], value=f"❤️ {p1['pv']} PV", inline=True)
    embed.add_field(name=p2['nome'], value=f"❤️ {p2['pv']} PV", inline=True)
    
    await ctx.send(embed=embed, view=view)

# --- SISTEMA DE EVENTOS NARRATIVOS ---
@bot.command()
async def evento(ctx, nome: str, dt: int, atributo: str, dano: int):
    """
    Cria um desafio para TODOS os jogadores com ficha.
    Ex: !evento "Ponte Caindo" 15 agilidade 10
    """
    if not eh_admin(ctx): return
    
    dados = carregar_dados()
    resumo = [f"🌋 **EVENTO: {nome}**", f"🎯 **Teste:** {atributo.upper()} (DT {dt})", "---"]
    
    # Atributo informado deve ser um dos 5 válidos
    at_busca = atributo.lower()
    
    for uid, p in dados["usuarios"].items():
        # Bônus do atributo do jogador
        bonus = p["atributos"].get(at_busca, 0)
        roll = random.randint(1, 20)
        total = roll + bonus
        
        if total >= dt:
            resumo.append(f"✅ **{p['nome']}** passou! ({roll} + {bonus} = {total})")
        else:
            # Aqui o aplicar_dano_complexo é finalmente acessado!
            # Ele calcula o escudo e verifica se a Fada salva o jogador
            log_dano, morto = aplicar_dano_complexo(p, dano)
            resumo.append(f"❌ **{p['nome']}** falhou! {log_dano}")

    # Salva as alterações de PV/Itens (Fadas) de todos os jogadores
    salvar_dados(dados)
    
    embed = discord.Embed(description="\n".join(resumo), color=0xffa500)
    await ctx.send(embed=embed)

@bot.command()
async def descansar(ctx):
    user_id = str(ctx.author.id)
    dados = carregar_dados()
    p = dados["usuarios"].get(user_id)
    if not p: return await ctx.send("🐾 **Lulu:** Sem alma, sem sono.")

    # Verifica se tem cargas de descanso (padrão 0 se não existir no JSON ainda)
    cargas = p.get("descansos", 0)

    if cargas <= 0:
        return await ctx.send(f"🐾 **Lulu:** {p['nome']}, você está exausto, mas não tem mais tempo para pausas agora! (0 descansos restantes)")

    if p["pv"] >= p["pv_max"]:
        return await ctx.send(f"🐾 **Lulu:** Por que dormir se você está inteiro? Vá lutar!")

    # Lógica de Cura
    dado_cura = calcular_dano_nivel(p["nivel"])
    cura = rolar_dado(dado_cura)
    p["pv"] = min(p["pv_max"], p["pv"] + cura)
    
    # Consome uma carga
    p["descansos"] -= 1

    # Frases da Lulu vigiando
    frases_lulu = [
        "Fiquem tranquilos, meus olhinhos estão atentos a qualquer sombra...",
        "Podem babar à vontade, eu aviso se algo tentar devorar vocês.",
        "Aproveitem o silêncio. Se eu sentir um cheiro de perigo, eu mordo!",
        "Vou ficar aqui polindo minhas garras enquanto vocês roncam.",
        "Descansar é para os fracos... mas eu deixo, só desta vez."
    ]
    vigilancia = random.choice(frases_lulu)

    embed = discord.Embed(
        title=f"💤 {p['nome']} montou acampamento",
        description=f"O cansaço diminui enquanto você recupera as forças.\n\n"
                    f"💖 **Recuperado:** +{cura} PV\n"
                    f"❤️ **Vida Atual:** {p['pv']}/{p['pv_max']}\n"
                    f"⛺ **Descansos Restantes:** {p['descansos']}\n\n"
                    f"🐾 **Vigilância da Lulu:** *\"{vigilancia}\"*",
        color=0x2c3e50
    )
    
    salvar_dados(dados)
    await ctx.send(embed=embed)

@bot.command()
async def lulu_ajuda(ctx):
    embed = discord.Embed(
        title="🐾 Central de Ajuda da Lulu",
        description="Olá! Eu sou a Lulu, a guardiã da sua jornada. Aqui estão as ordens que eu entendo:",
        color=0x71368a
    )
    
    # Seção de Aventura
    aventura = (
        "**!ficha** [@usuario] - Veja sua ficha, vida e atributos.\n"
        "**!habilidades** - Liste as técnicas que você já liberou.\n"
        "**!usar <nome>** - Use uma habilidade da sua raça.\n"
        "**!descansar** - Use uma carga de acampamento (⛺) para curar PV.\n"
        "**!d <expressão>** - Rola dados genéricos (ex: !d 2d10+5)."
    )
    embed.add_field(name="⚔️ Ação e Aventura", value=aventura, inline=False)

    # Seção de Regras Lulu (Interação)
    regras = (
        "• **Sucesso:** Tire um valor igual ou maior que a DT.\n"
        "• **Azar:** Se você estiver azarado (💀), sua próxima rolagem tem -5.\n"
        "• **Cura:** O descanso recupera PV baseado no seu nível atual."
    )
    embed.add_field(name="📜 Regras Rápidas", value=regras, inline=False)

    # Seção para o Mestre (Só aparece se quem digitou for Admin)
    if ctx.author.guild_permissions.administrator:
        mestre = (
            "**!registrar @usuario <raça>** - Cria uma nova ficha.\n"
            "**!upar @usuario [n]** - Sobe o nível e dá bônus.\n"
            "**!lulu_reset [n]** - Dá cargas de descanso para todos.\n"
            "**!lulu_azar @usuario** - Amaldiçoa um jogador com -5."
        )
        embed.add_field(name="👑 Comandos de Mestre", value=mestre, inline=False)

    embed.set_footer(text="A Lulu está de olho em você! Boa sorte na mesa.")
    embed.set_thumbnail(url="URL_DE_UMA_IMAGEM_DA_LULU_SE_TIVER") # Opcional

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def lulu_azar(ctx, alvo: discord.Member):
    dados = carregar_dados()
    p = dados["usuarios"].get(str(alvo.id))
    if p:
        p["azarado"] = True
        salvar_dados(dados)
        await ctx.send(f"💀 **Lulu rosnou para {alvo.name}!** A nuvem do azar agora te persegue (-5 na próxima rolagem).")

@bot.command()
@commands.has_permissions(administrator=True) # Só você ou ADMs podem usar
async def lulu_reset(ctx, quantidade: int = 1):
    dados = carregar_dados()
    
    # Dá 'quantidade' de descansos para TODOS os jogadores registrados
    for user_id in dados["usuarios"]:
        p = dados["usuarios"][user_id]
        p["descansos"] = p.get("descansos", 0) + quantidade
    
    salvar_dados(dados)
    await ctx.send(f"🐾 **Lulu:** Recuperei o fôlego de todos! Adicionei **{quantidade}** carga(s) de descanso para o grupo.")

bot.run(TOKEN)