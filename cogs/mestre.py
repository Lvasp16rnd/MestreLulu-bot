import discord
from discord.ext import commands
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import aplicar_dano_complexo, aplicar_status_nivel, processar_xp_acumulado
from mecanicas import adicionar_xp
import random

from utils import eh_admin

class Mestre(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="upar", description="Sobe o nível de um jogador (ADMs apenas)")
    async def upar(self, ctx, alvo: discord.Member, n: int = 1):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para isso!")
            
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        
        if p:
            nivel_atual = p.get("nivel", 1)
            
            # Verifica se já está no nível máximo
            if nivel_atual >= 20:
                return await ctx.send(f"🐾 **Lulu:** **{alvo.display_name}** já atingiu o nível máximo (20)!")
            
            # Limita para não passar de 20
            novo_nivel = min(20, nivel_atual + n)
            niveis_ganhos = novo_nivel - nivel_atual
            
            p["nivel"] = novo_nivel
            p["descansos"] = p.get("descansos", 0) + niveis_ganhos
            
            aplicar_status_nivel(p)
            
            from cogs.logic import calcular_xp_necessario
            if "xp_max" not in p:
                p["xp_max"] = 100  
            for _ in range(niveis_ganhos):
                p["xp_max"] = calcular_xp_necessario(p["nivel"], p["xp_max"])
            
            # No nível 20, XP fica em 0 (não precisa mais)
            if p["nivel"] >= 20:
                p["xp"] = 0
                p["xp_max"] = 0
            
            salvar_dados(dados)
            
            xp_atual = p.get("xp", 0)
            xp_max = p["xp_max"]
            
            embed = discord.Embed(
                title="🎊 NOVO NÍVEL ALCANÇADO!",
                description=f"**{alvo.display_name}** agora é Nível **{p['nivel']}**!",
                color=0x00ff00
            )
            embed.add_field(name="🎲 Dado", value=p.get('dado_nivel', '1d6'), inline=True)
            
            # Exibe MAX se atingiu nível 20
            if p["nivel"] >= 20:
                embed.add_field(name="✨ Experiência", value="🌟 **NÍVEL MÁXIMO!**", inline=True)
            else:
                embed.add_field(name="✨ Experiência", value=f"{xp_atual}/{xp_max}", inline=True)
            
            embed.add_field(name="❤️ Vida Máxima", value=f"{p['pv_max']} PV", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("🐾 **Lulu:** Esse humano nem tem ficha ainda.")

    @commands.hybrid_command(name="dar_xp", description="Dá XP e processa níveis (ADMs)")
    async def dar_xp(self, ctx, alvo: discord.Member, quantidade: int):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para distribuir conhecimento.")

        await ctx.defer()
        
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        
        if not p:
            return await ctx.send("🐾 **Lulu:** Esse alvo não tem alma registrada.")

        # Verifica se já está no nível máximo
        if p.get("nivel", 1) >= 20:
            return await ctx.send(f"🐾 **Lulu:** **{alvo.display_name}** já é nível 20! Não precisa de mais XP.")

        nivel_anterior = p.get("nivel", 1)
        upou = processar_xp_acumulado(p, quantidade)
        
        # Se atingiu nível 20 após o XP, zera o contador
        if p["nivel"] >= 20:
            p["xp"] = 0
            p["xp_max"] = 0
        
        salvar_dados(dados)
        
        if upou:
            embed = discord.Embed(
                title="🎊 GRANDE PROGRESSO!",
                description=f"**{alvo.display_name}** recebeu **{quantidade} XP** e saltou do nível {nivel_anterior} para o **{p['nivel']}**!",
                color=0x00ff00
            )
            embed.add_field(name="❤️ Vida Atualizada", value=f"{p['pv_max']} PV", inline=True)
            
            if p["nivel"] >= 20:
                embed.add_field(name="✨ XP Atual", value="🌟 **NÍVEL MÁXIMO!**", inline=True)
            else:
                embed.add_field(name="✨ XP Atual", value=f"{p['xp']}/{p['xp_max']}", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"✨ **{alvo.display_name}** ganhou **{quantidade} XP**! (Total: {p['xp']}/{p['xp_max']})")

    @commands.hybrid_command(name="lulu_reset", description="Dá cargas de descanso para todos (ADMs apenas)")
    async def lulu_reset(self, ctx, quantidade: int = 1):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para isso!")
        
        dados = carregar_dados()
        
        for user_id in dados["usuarios"]:
            p = dados["usuarios"][user_id]
            p["descansos"] = p.get("descansos", 0) + quantidade
        
        salvar_dados(dados)
        await ctx.send(f"🐾 **Lulu:** Recuperei o fôlego de todos! Adicionei **{quantidade}** carga(s) de descanso para o grupo.")

    @commands.hybrid_command(name="lulu_azar", description="Amaldiçoa um jogador com azar (-5 na próxima rolagem) (ADMs apenas)")
    async def lulu_azar(self, ctx, alvo: discord.Member):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para isso!")
        
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        if p:
            p["azarado"] = True
            salvar_dados(dados)
            await ctx.send(f"💀 **Lulu rosnou para {alvo.name}!** A nuvem do azar agora te persegue (-5 na próxima rolagem).")

    @commands.hybrid_command(name="setar", description="Define atributos, nível ou XP (ADMs apenas)")
    async def setar(self, ctx, alvo: discord.Member, at: str, v: int):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para isso!")
            
        dados = carregar_dados()
        uid = str(alvo.id)
        
        if uid in dados["usuarios"]:
            p = dados["usuarios"][uid]
            atributo = at.lower()

            if atributo == "xp":
                p["xp"] = max(0, v)
                # Garante xp_max existe
                if "xp_max" not in p:
                    p["xp_max"] = 100
                msg = f"✨ XP de {alvo.name} setado para {v}/{p['xp_max']}."

            elif atributo == "nivel":
                nivel_anterior = p.get("nivel", 1)
                p["nivel"] = max(1, min(20, v))  
                p["xp"] = 0 
                
                from cogs.logic import calcular_xp_necessario, aplicar_status_nivel
                
                # Recalcula xp_max desde o nível 1 até o nível atual
                xp_acumulado = 100  # Base para nível 1→2
                for n in range(1, p["nivel"]):
                    xp_acumulado = calcular_xp_necessario(n, xp_acumulado)
                p["xp_max"] = xp_acumulado
                
                # Se nível 20, não precisa mais de XP
                if p["nivel"] >= 20:
                    p["xp_max"] = 0
                
                aplicar_status_nivel(p)
                
                if p["nivel"] >= 20:
                    msg = f"🧬 Nível de {alvo.name} setado para {p['nivel']} 🌟 **NÍVEL MÁXIMO!**"
                else:
                    msg = f"🧬 Nível de {alvo.name} setado para {p['nivel']} (XP: 0/{p['xp_max']})."

            elif atributo in p["atributos"]:
                p["atributos"][atributo] = v
                msg = f"✅ Atributo {at.upper()} de {alvo.name} setado para {v}."

            else:
                p[atributo] = v
                msg = f"✅ Campo {at} de {alvo.name} setado para {v}."

            salvar_dados(dados)
            await ctx.send(f"🐾 **Lulu:** {msg}")
        else:
            await ctx.send("🐾 **Lulu:** Usuário não encontrado.")

    @commands.hybrid_command(name="concluir_missao", description="Conclui uma missão e distribui recompensas (ADMs apenas)")
    async def concluir_missao(self, ctx):
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Você não tem autoridade para isso!")
        
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        try:
            await ctx.send("📝 Nome da Missão?")
            msg_nome = await self.bot.wait_for("message", timeout=30, check=check)
            nome = msg_nome.content
            
            await ctx.send("👥 Mencione os heróis:")
            msg_herois = await self.bot.wait_for("message", timeout=30, check=check)
            herois = msg_herois.mentions
            
            await ctx.send("💰 Krugs para cada um?")
            msg_valor = await self.bot.wait_for("message", timeout=30, check=check)
            valor = int(msg_valor.content)

            dados = carregar_dados()
            for h in herois:
                if str(h.id) in dados["usuarios"]: 
                    dados["usuarios"][str(h.id)]["dinheiro"] += valor
            
            salvar_dados(dados)
            await ctx.send(f"📜 Missão '{nome}' salva!")
        except Exception as e: 
            print(e)
            await ctx.send("🐾 **Lulu:** Erro no registro ou tempo esgotado.")

    @commands.hybrid_command(name="sorteio_missao", description="Sorteia uma equipe diversificada para uma missão (ADMs apenas)")
    async def sorteio_missao(self, ctx):
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

    @commands.hybrid_command(name="evento", description="Cria um desafio para todos os jogadores com ficha (ADMs apenas)")
    async def evento(self, ctx, nome: str, dt: int, atributo: str, dano: int):
        """
        Cria um desafio para TODOS os jogadores com ficha.
        Ex: !evento "Ponte Caindo" 15 agilidade 10
        """
        if not eh_admin(ctx):
            return await ctx.send("🐾 **Lulu:** Apenas mestres podem invocar eventos catastróficos!")
        
        dados = carregar_dados()
        if not dados.get("usuarios"):
            return await ctx.send("🐾 **Lulu:** Não há ninguém no mundo para sofrer este evento.")

        resumo = [f"🌋 **EVENTO: {nome}**", f"🎯 **Teste:** {atributo.upper()} (DT {dt})", "---"]
        at_busca = atributo.lower()
        
        for uid, p in dados["usuarios"].items():
            attrs = p.get("atributos", {})
            bonus = attrs.get(at_busca, 0)
            
            roll = random.randint(1, 20)
            total = roll + bonus
            
            if total >= dt:
                resumo.append(f"✅ **{p['nome']}** passou! ({roll} + {bonus} = {total})")
            else:
                log_dano, morto = aplicar_dano_complexo(p, dano)
                resumo.append(f"❌ **{p['nome']}** falhou! {log_dano}")

        salvar_dados(dados)
        
        embed = discord.Embed(
            title="⚠️ O Destino se Manifesta!",
            description="\n".join(resumo), 
            color=0xffa500
        )
        embed.set_footer(text=f"Evento mestre por {ctx.author.name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mestre(bot))
