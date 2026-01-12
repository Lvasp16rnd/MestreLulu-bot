import discord
from discord.ext import commands
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import aplicar_dano_complexo
from mecanicas import adicionar_xp
import random

from main import eh_admin

class Mestre(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def upar(self, self_ctx, alvo: discord.Member, n: int = 1): # Adicionado self
        ctx = self_ctx # Apenas para manter seu código igual abaixo
        if not eh_admin(ctx): return
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        
        if p:
            p["nivel"] += n
            p["descansos"] = p.get("descansos", 0) + n
            
            for faixa, st in constantes.TABELA_NIVEIS.items():
                f_inicio = int(faixa.split('-')[0])
                f_fim = int(faixa.split('-')[1])
                
                if f_inicio <= p["nivel"] <= f_fim:
                    p["pv_max"] = st["pv"] 
                    p["ca"] = st["ca"]
                    p["dado_nivel"] = st["dado"]
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dar_xp(self, ctx, alvo: discord.Member, quantidade: int):
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        
        if p:
            upou = adicionar_xp(p, quantidade)
            salvar_dados(dados)
            
            msg = f"✨ **{alvo.name}** recebeu {quantidade} de XP!"
            if upou:
                msg += f"\n🎊 **LEVEL UP!** Agora você é nível {p['nivel']}!"
            
            await ctx.send(msg)

    @commands.command()
    @commands.has_permissions(administrator=True) # Só você ou ADMs podem usar
    async def lulu_reset(self, ctx, quantidade: int = 1):
        dados = carregar_dados()
        
        # Dá 'quantidade' de descansos para TODOS os jogadores registrados
        for user_id in dados["usuarios"]:
            p = dados["usuarios"][user_id]
            p["descansos"] = p.get("descansos", 0) + quantidade
        
        salvar_dados(dados)
        await ctx.send(f"🐾 **Lulu:** Recuperei o fôlego de todos! Adicionei **{quantidade}** carga(s) de descanso para o grupo.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lulu_azar(self, ctx, alvo: discord.Member):
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        if p:
            p["azarado"] = True
            salvar_dados(dados)
            await ctx.send(f"💀 **Lulu rosnou para {alvo.name}!** A nuvem do azar agora te persegue (-5 na próxima rolagem).")

    @commands.command()
    async def setar(self, ctx, alvo: discord.Member, at: str, v: int):
        if not eh_admin(ctx): return
        dados = carregar_dados()
        uid = str(alvo.id)
        if uid in dados["usuarios"]:
            if at.lower() in dados["usuarios"][uid]["atributos"]: dados["usuarios"][uid]["atributos"][at.lower()] = v
            else: dados["usuarios"][uid][at.lower()] = v
            salvar_dados(dados)
            await ctx.send(f"✅ {at} de {alvo.name} setado para {v}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def concluir_missao(self, ctx): # Adicionado self
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        try:
            await ctx.send("📝 Nome da Missão?")
            # MUDANÇA AQUI: de bot.wait_for para self.bot.wait_for
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

    @commands.command()
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

    @commands.command()
    async def evento(self, ctx, nome: str, dt: int, atributo: str, dano: int):
        """
        Cria um desafio para TODOS os jogadores com ficha.
        Ex: !evento "Ponte Caindo" 15 agilidade 10
        """
        # 1. Ajuste de Permissão: 
        # Como eh_admin está na main, usamos o check nativo do discord ou self.bot
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("🐾 **Lulu:** Apenas mestres podem invocar eventos catastróficos!")
        
        dados = carregar_dados()
        # Se o seu JSON tiver uma lista vazia, evitamos erro
        if not dados.get("usuarios"):
            return await ctx.send("🐾 **Lulu:** Não há ninguém no mundo para sofrer este evento.")

        resumo = [f"🌋 **EVENTO: {nome}**", f"🎯 **Teste:** {atributo.upper()} (DT {dt})", "---"]
        at_busca = atributo.lower()
        
        for uid, p in dados["usuarios"].items():
            # 2. Segurança de Atributo:
            attrs = p.get("atributos", {})
            bonus = attrs.get(at_busca, 0)
            
            roll = random.randint(1, 20)
            total = roll + bonus
            
            if total >= dt:
                resumo.append(f"✅ **{p['nome']}** passou! ({roll} + {bonus} = {total})")
            else:
                # Aqui usamos a função que unificamos no logic.py
                log_dano, morto = aplicar_dano_complexo(p, dano)
                resumo.append(f"❌ **{p['nome']}** falhou! {log_dano}")

        # Salva as alterações de PV e Fadas consumidas
        salvar_dados(dados)
        
        # 3. Gerenciamento de Tamanho:
        embed = discord.Embed(
            title="⚠️ O Destino se Manifesta!",
            description="\n".join(resumo), 
            color=0xffa500
        )
        embed.set_footer(text=f"Evento mestre por {ctx.author.name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mestre(bot))
