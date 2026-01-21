import discord
from discord.ext import commands
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import calcular_dano_nivel, rolar_dado, usar_pocao_sorte
import random
import datetime

class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ficha", description="Mostra sua ficha de personagem")
    async def ficha(self, ctx, alvo: discord.Member = None):
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

        xp_atual = p.get("xp", 0)
        xp_max = p.get("xp_max", 500)
        barra = "◈" * int((xp_atual/xp_max)*10) + "◇" * (10 - int((xp_atual/xp_max)*10))

        embed.add_field(name=f"📊 XP ({xp_atual}/{xp_max})", value=f"`{barra}`", inline=False)

        status = "💀 **AZARADO**" if p.get("azarado") else "✨ Normal"
        embed.add_field(name="Status", value=status, inline=True)
        
        dado_atual = calcular_dano_nivel(p["nivel"])
        embed.add_field(name="🎲 Dado Atual", value=dado_atual, inline=True)
        
        attrs = f"FOR: {at['forca']} | AGI: {at['agilidade']} | INT: {at['intelecto']}\nPRE: {at['presenca']} | CAR: {at['carisma']}"
        embed.add_field(name="📊 Atributos", value=f"```\n{attrs}\n```", inline=False)
        embed.set_footer(text="Use !descansar para recuperar fôlego (consome ⛺)")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="descansar", description="Recupera pontos de vida usando descansos")
    async def descansar(self, ctx):
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p: 
            return await ctx.send("🐾 **Lulu:** Sem alma, sem sono.")
        
        nivel_str = str(p.get("nivel", 1))
        info_nivel = constantes.TABELA_NIVEIS.get(nivel_str, {"pv": 30})
        pv_max = info_nivel["pv"]

        cargas = p.get("descansos", 0)
        pv_atual = p.get("pv", 0)

        if cargas <= 0:
            return await ctx.send(f"🐾 **Lulu:** {p['nome']}, você está exausto, mas não tem mais tempo para pausas agora! (0 descansos restantes)")

        if pv_atual >= pv_max:
            return await ctx.send(f"🐾 **Lulu:** Por que dormir se você está inteiro? Vá lutar!")

        dado_cura = p.get("dado", "1d6") 
        cura = rolar_dado(dado_cura)
        
        p["pv"] = min(pv_max, pv_atual + cura)
        p["descansos"] = cargas - 1

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
            description=(
                f"O cansaço diminui enquanto você recupera as forças.\n\n"
                f"💖 **Recuperado:** +{cura} PV\n"
                f"❤️ **Vida Atual:** {p['pv']}/{pv_max}\n"
                f"⛺ **Descansos Restantes:** {p['descansos']}\n\n"
                f"🐾 **Vigilância da Lulu:** *\"{vigilancia}\"*"
            ),
            color=0x2c3e50
        )
    
        salvar_dados(dados)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="trabalhar", description="Trabalhe para ganhar Krugs K$")
    async def trabalhar(self, ctx):
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p: 
            return await ctx.send("🐾 **Lulu:** Sem alma, sem trabalho. Registre-se primeiro.")

        agora = datetime.datetime.now()
        ultimo_trabalho_str = p.get("ultimo_trabalho")
        
        if ultimo_trabalho_str:
            ultimo_trabalho = datetime.datetime.fromisoformat(ultimo_trabalho_str)
            diferenca = agora - ultimo_trabalho
            
            if diferenca.total_seconds() < 3600:
                segundos_restantes = int(3600 - diferenca.total_seconds())
                minutos = segundos_restantes // 60
                return await ctx.send(f"⏳ **Lulu:** Você já trabalhou demais por agora! Volte em **{minutos} minutos**.")

        ganhos = random.randint(50, 150) + (p.get("nivel", 1) * 2)
        
        p["dinheiro"] = p.get("dinheiro", 0) + ganhos
        p["ultimo_trabalho"] = agora.isoformat()
        
        profissoes = [
            "ajudou na forja de Rochas e Runas",
            "caçou pragas nos jardins de O Vel",
            "limpou os frascos na Casa das Bruxas",
            "carregou fardos na Caravana do Último Pacto",
            "vigiou as fronteiras de Veneno Silencioso",
            "coletou essências de sonhos para as Fadas de Íris",
            "poliu as joias raras no Altar dos Fragmentados",
            "ajudou na colheita das frutas luminescentes de Lúmen",
            "extraiu minérios raros das cavernas profundas de Kharr-Dum" 
        ]
        servico = random.choice(profissoes)

        salvar_dados(dados)
        
        await ctx.send(
            f"💼 **{p['nome']}** {servico} e recebeu **{ganhos} K$**!\n"
            f"💰 **Saldo Atual:** {p['dinheiro']} K$"
        )     

    @commands.hybrid_command(name="inventario", description="Mostra seu inventário e saldo")
    async def inventario(self, ctx):
        p = carregar_dados()["usuarios"].get(str(ctx.author.id))
        if not p: return await ctx.send("🐾 **Lulu:** Registre-se.")
        inv = ", ".join(p["inventario"]) if p["inventario"] else "Vazio"
        await ctx.send(embed=discord.Embed(title=f"🎒 {ctx.author.name}", description=f"**Itens:** {inv}\n**Saldo:** {p['dinheiro']} Krugs"))

    @commands.hybrid_command(name="beber", description="Usa um item do inventário")
    async def beber(self,ctx, *, item: str):
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

    @commands.hybrid_command(name="historico", description="Mostra as últimas missões")
    async def historico(self, ctx):
        missoes = carregar_dados().get("missoes", [])[-5:]
        if not missoes: return await ctx.send("🐾 **Lulu:** Sem história.")
        txt = "\n".join([f"🔹 **{m['missao']}**: {', '.join(m['herois'])}" for m in reversed(missoes)])
        await ctx.send(embed=discord.Embed(title="📖 Crônicas", description=txt))

    @commands.hybrid_command(name="dado", aliases=["roll", "r"], description="Rola dados. Ex: !dado 2d6 ou !dado 1d100")
    async def dado(self, ctx, formula: str = "1d20"):
        """Rola dados. Ex: !dado 2d6 ou !dado 1d100"""
        try:
            from cogs.logic import rolar_dado
            
            resultado = rolar_dado(formula)
            embed = discord.Embed(
                title="🎲 O Dado Rolou!",
                description=f"**Resultado:** `{resultado}`\n**Fórmula:** `{formula}`",
                color=0x9b59b6
            )
            embed.set_footer(text=f"Lançado por {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("🐾 **Lulu:** Formato inválido! Use algo como `!dado 1d20`.")

async def setup(bot):
    await bot.add_cog(Players(bot))