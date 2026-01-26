import discord
from discord.ext import commands
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import (
    calcular_dano_nivel, 
    rolar_dado, 
    usar_pocao_sorte,
    ATRIBUTOS_DISPLAY,
    normalizar_atributo,
    rolar_teste_atributo,
    formatar_resultado_teste
)
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

        xp_total = p.get("xp", 0)
        nivel_atual = p["nivel"]
        
        xp_piso = (nivel_atual - 1) * 100 
        xp_teto = nivel_atual * 100     
        
        xp_relativo = xp_total - xp_piso
        alcance_nivel = xp_teto - xp_piso 

        percentual = min(max(xp_relativo / alcance_nivel, 0), 1.0) if alcance_nivel > 0 else 0
        
        num_quadrados = int(percentual * 10)
        barra = "◈" * num_quadrados + "◇" * (10 - num_quadrados)
        # ---------------------------------------------

        embed = discord.Embed(title=f"📜 Ficha de {p['nome']}", color=0x71368a)
        embed.add_field(name="🧬 Raça/Nível", value=f"{p['raca']} Lvl {nivel_atual}", inline=True)
        embed.add_field(name="❤️ PV | 🛡️ Escudo | ⛺", value=f"{p['pv']}/{p['pv_max']} | {p['ca']} | ({descansos})", inline=True)
        embed.add_field(name="🍀 Sorte", value=str(sorte), inline=True)

        embed.add_field(name=f"📊 XP ({xp_total}/{xp_teto})", value=f"`{barra}`", inline=False)

        status = "💀 **AZARADO**" if p.get("azarado") else "✨ Normal"
        embed.add_field(name="Status", value=status, inline=True)
        
        from cogs.logic import calcular_dano_nivel 
        dado_atual = calcular_dano_nivel(nivel_atual)
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

    ITENS_BEBIVEIS = [
        "Poção da Sorte",
        "Poção do Tempo Velado", 
        "Poção do Amor",
        "Poção do Esquecimento",
        "Poção da Raiva",
        "Poção da Verdade",
        "Poção do Quase Milagre",
        "Frascos de Alquimia Errante",
        "Sangue do Cupido"
    ]

    async def beber_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocomplete que mostra os itens bebíveis do inventário do jogador."""
        user_id = str(interaction.user.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p:
            return []
        
        inventario = p.get("inventario", [])
        
        itens_disponiveis = [
            item for item in inventario 
            if item in self.ITENS_BEBIVEIS and current.lower() in item.lower()
        ]
        
        itens_unicos = list(dict.fromkeys(itens_disponiveis))
        
        opcoes = [
            discord.app_commands.Choice(name=item, value=item)
            for item in itens_unicos
        ]
        
        return opcoes[:25]

    @commands.hybrid_command(name="beber", description="Usa um item do inventário")
    @discord.app_commands.autocomplete(item=beber_autocomplete)
    async def beber(self, ctx, *, item: str):
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p:
            return await ctx.send("🐾 **Lulu:** Sem alma, sem poções.")
        
        item_real = next((i for i in p["inventario"] if i.lower() == item.lower()), None)
        if not item_real: 
            return await ctx.send("🐾 **Lulu:** Você não tem isso.")

        if item_real not in self.ITENS_BEBIVEIS:
            return await ctx.send("🐾 **Lulu:** Isso não se bebe.")

        p["inventario"].remove(item_real)
        pv_max = p.get("pv_max", 30)

        if item_real == "Poção da Sorte":
            res, _ = usar_pocao_sorte(p)
            salvar_dados(dados)
            return await ctx.send(res)

        elif item_real == "Poção do Tempo Velado":
            cura = random.randint(1, 10)
            p["pv"] = min(pv_max, p["pv"] + cura)
            salvar_dados(dados)
            return await ctx.send(f"⏳ **Tempo manipulado!** Recuperou **+{cura} PV**. ❤️ Vida: {p['pv']}/{pv_max}")

        elif item_real == "Poção do Quase Milagre":
            cura = random.randint(1, 20)
            if cura == 1:
                cura = cura // 2  
                msg = f"💔 **Quase milagre... quase.** A poção falhou parcialmente. Recuperou apenas **+{cura} PV**."
            else:
                msg = f"✨ **Milagre!** Recuperou **+{cura} PV**."
            p["pv"] = min(pv_max, p["pv"] + cura)
            salvar_dados(dados)
            return await ctx.send(f"{msg} ❤️ Vida: {p['pv']}/{pv_max}")

        elif item_real == "Frascos de Alquimia Errante":
            cura = random.randint(1, 4)
            p["pv"] = min(pv_max, p["pv"] + cura)
            
            efeitos_colaterais = [
                "Sua pele ficou levemente azulada por alguns minutos.",
                "Você sentiu um gosto de metal na boca.",
                "Seus olhos brilharam brevemente.",
                "Um leve tremor percorreu seu corpo.",
                "Você soltou uma risada involuntária.",
                "Seu cabelo ficou em pé por um instante."
            ]
            efeito = random.choice(efeitos_colaterais)
            salvar_dados(dados)
            return await ctx.send(f"🧪 **Alquimia Errante!** Recuperou **+{cura} PV**. ❤️ Vida: {p['pv']}/{pv_max}\n*Efeito colateral: {efeito}*")

        elif item_real == "Sangue do Cupido":
            p["buff_dt"] = p.get("buff_dt", 0) - 2
            salvar_dados(dados)
            return await ctx.send("🩸 **Sangue do Cupido consumido!** Seu próximo teste terá **-2 na DT**.")

        elif item_real == "Poção do Amor":
            salvar_dados(dados)
            return await ctx.send("💖 **Poção do Amor bebida!** Por um dia, você emana uma aura de fascínio irresistível. Use com sabedoria (ou não).")

        elif item_real == "Poção do Esquecimento":
            salvar_dados(dados)
            return await ctx.send("☁️ **Poção do Esquecimento bebida!** Você pode apagar uma lembrança específica de alguém (ou sua). Converse com o Mestre.")

        elif item_real == "Poção da Raiva":
            salvar_dados(dados)
            return await ctx.send("💢 **Poção da Raiva bebida!** Por um dia, você sente uma fúria ardente. +2 de dano em ataques corpo-a-corpo, mas -2 em testes de Carisma.")

        elif item_real == "Poção da Verdade":
            salvar_dados(dados)
            return await ctx.send("👁️ **Poção da Verdade bebida!** Quem beber não conseguirá mentir. Ideal para interrogatórios... ou confissões.")

        # Fallback (não deve chegar aqui)
        else:
            p["inventario"].append(item_real)
            salvar_dados(dados)
            return await ctx.send("🐾 **Lulu:** Algo deu errado ao consumir isso.")

    @commands.hybrid_command(name="historico", description="Mostra as últimas missões")
    async def historico(self, ctx):
        missoes = carregar_dados().get("missoes", [])[-5:]
        if not missoes: return await ctx.send("🐾 **Lulu:** Sem história.")
        txt = "\n".join([f"🔹 **{m['missao']}**: {', '.join(m['herois'])}" for m in reversed(missoes)])
        await ctx.send(embed=discord.Embed(title="📖 Crônicas", description=txt))

    @commands.hybrid_command(name="dado", aliases=["roll", "r"], description="Rola dados. Ex: 2d6 ou 3#d12")
    async def dado(self, ctx, formula: str = "1d20"):
        try:
            from cogs.logic import rolar_dado
            
            resultado, dados_rolados, modo = rolar_dado(formula)
            
            if modo == "erro":
                return await ctx.send("🐾 **Lulu:** Formato inválido!")

            embed = discord.Embed(title="🎲 O Dado Rolou!", color=0x9b59b6)
            
            if modo == "maior":
                lista_dados = ", ".join(map(str, dados_rolados))
                embed.description = (
                    f"Foram rolados **{len(dados_rolados)}** dados: `{lista_dados}`\n"
                    f"🏆 **O maior valor foi:** `{resultado}`"
                )
            else:
                embed.description = f"**Resultado:** `{resultado}`\n**Dados:** `{dados_rolados}`"
            
            embed.add_field(name="📋 Fórmula", value=f"`{formula}`")
            embed.set_footer(text=f"Lançado por {ctx.author.name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erro no dado: {e}")
            await ctx.send("🐾 **Lulu:** Formato inválido! Use `2d6` ou `3#d12`.")
    
    async def atributo_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocomplete para os atributos disponíveis."""
        opcoes = [
            discord.app_commands.Choice(name=attr, value=attr)
            for attr in ATRIBUTOS_DISPLAY
            if current.lower() in attr.lower()
        ]
        return opcoes[:25]

    @commands.hybrid_command(name="testar", description="Faz um teste de atributo (FOR, AGI, INT, PRE, CAR)")
    @discord.app_commands.describe(
        atributo="O atributo a ser testado",
        modificador="Bônus ou penalidade adicional (opcional)"
    )
    @discord.app_commands.autocomplete(atributo=atributo_autocomplete)
    async def testar(self, ctx, atributo: str, modificador: int = 0):
        """
        Realiza um teste de atributo seguindo as regras:
        - Atributo 0: Rola 2d20 e pega o MENOR (desvantagem)
        - Atributo 1: Rola 1d20 normal
        - Atributo 2: Rola 2d20 e pega o MAIOR (vantagem)
        - Atributo 3+: Rola 3d20 e pega o MAIOR (super vantagem)
        """
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p:
            return await ctx.send("🐾 **Lulu:** Você não tem uma ficha. Use `/registrar` primeiro.")
        
        attr_interno = normalizar_atributo(atributo)
        if not attr_interno:
            atributos_validos = ", ".join(ATRIBUTOS_DISPLAY)
            return await ctx.send(
                f"🐾 **Lulu:** Atributo inválido! Use um destes: `{atributos_validos}`"
            )
        
        valor_atributo = p["atributos"].get(attr_interno, 0)
        
        mod_total = modificador
        azar_msg = ""
        if p.get("azarado"):
            mod_total -= 5
            azar_msg = "⚠️ **O Azar te atingiu! (-5 no resultado)**\n\n"
            p["azarado"] = False
            salvar_dados(dados)
        
        resultado = rolar_teste_atributo(valor_atributo, mod_total)
        
        nome_bonito = atributo.capitalize()
        embed = discord.Embed(
            title=f"🎯 Teste de {nome_bonito}",
            color=self._cor_por_resultado(resultado["resultado"])
        )
        
        embed.add_field(
            name=f"📊 {nome_bonito}",
            value=f"Valor: **{valor_atributo}**",
            inline=True
        )
        
        embed.add_field(
            name="🎲 Fórmula",
            value=f"`{resultado['quantidade']}#d20`" if resultado["quantidade"] > 1 else "`1d20`",
            inline=True
        )
        
        texto_resultado = formatar_resultado_teste(nome_bonito, valor_atributo, resultado)
        embed.description = f"{azar_msg}{texto_resultado}"
        
        embed.set_footer(text=f"Teste realizado por {p['nome']} | Use /testar <atributo> [modificador]")
        
        await ctx.send(embed=embed)

    def _cor_por_resultado(self, valor: int) -> discord.Color:
        """Retorna uma cor baseada no resultado do dado."""
        if valor == 20:
            return discord.Color.gold()  # Crítico!
        elif valor >= 15:
            return discord.Color.green()  # Bom
        elif valor >= 10:
            return discord.Color.blue()  # Médio
        elif valor > 1:
            return discord.Color.orange()  # Ruim
        else:
            return discord.Color.red()  # Falha crítica!

async def setup(bot):
    await bot.add_cog(Players(bot))