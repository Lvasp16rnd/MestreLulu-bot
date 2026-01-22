import discord
from discord.ext import commands
import constantes
from database import carregar_dados, salvar_dados
from cogs.logic import aplicar_dano_complexo, processar_xp_acumulado
from mecanicas import adicionar_xp
import random

from main import eh_admin

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
            p["nivel"] = p.get("nivel", 1) + n
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
                description=f"**{alvo.display_name}** agora é Nível **{p['nivel']}**!",
                color=0x00ff00
            )
            embed.add_field(name="🎲 Novo Dado", value=p.get('dado_nivel', '1d6'), inline=True)
            embed.add_field(name="⛺ Bônus", value=f"+{n} Carga de Descanso", inline=True)
            embed.add_field(name="❤️ Vida Máxima", value=f"{p['pv_max']} PV", inline=False)
            embed.set_footer(text="A Lulu está orgulhosa do seu progresso!")
            
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

        nivel_anterior = p.get("nivel", 1)
        upou = processar_xp_acumulado(p, quantidade)
        salvar_dados(dados)
        
        if upou:
            embed = discord.Embed(
                title="🎊 GRANDE PROGRESSO!",
                description=f"**{alvo.display_name}** recebeu **{quantidade} XP** e saltou do nível {nivel_anterior} para o **{p['nivel']}**!",
                color=0x00ff00
            )
            embed.add_field(name="❤️ Vida Atualizada", value=f"{p['pv_max']} PV", inline=True)
            embed.add_field(name="✨ XP Atual", value=f"{p['xp']} (Próximo nível: {p['nivel'] * 100})", inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"✨ **{alvo.display_name}** ganhou **{quantidade} XP**! (Total: {p['xp']}/{p['nivel']*100})")

    @commands.hybrid_command(name="lulu_reset", description="Dá cargas de descanso para todos (ADMs apenas)")
    @commands.has_permissions(administrator=True) 
    async def lulu_reset(self, ctx, quantidade: int = 1):
        dados = carregar_dados()
        
        for user_id in dados["usuarios"]:
            p = dados["usuarios"][user_id]
            p["descansos"] = p.get("descansos", 0) + quantidade
        
        salvar_dados(dados)
        await ctx.send(f"🐾 **Lulu:** Recuperei o fôlego de todos! Adicionei **{quantidade}** carga(s) de descanso para o grupo.")

    @commands.hybrid_command(name="lulu_azar", description="Amaldiçoa um jogador com azar (-5 na próxima rolagem) (ADMs apenas)")
    @commands.has_permissions(administrator=True)
    async def lulu_azar(self, ctx, alvo: discord.Member):
        dados = carregar_dados()
        p = dados["usuarios"].get(str(alvo.id))
        if p:
            p["azarado"] = True
            salvar_dados(dados)
            await ctx.send(f"💀 **Lulu rosnou para {alvo.name}!** A nuvem do azar agora te persegue (-5 na próxima rolagem).")

    @commands.hybrid_command(name="setar", description="Define um atributo ou valor para um jogador (ADMs apenas)")
    async def setar(self, ctx, alvo: discord.Member, at: str, v: int):
        if not eh_admin(ctx): return
        dados = carregar_dados()
        uid = str(alvo.id)
        if uid in dados["usuarios"]:
            if at.lower() in dados["usuarios"][uid]["atributos"]: dados["usuarios"][uid]["atributos"][at.lower()] = v
            else: dados["usuarios"][uid][at.lower()] = v
            salvar_dados(dados)
            await ctx.send(f"✅ {at} de {alvo.name} setado para {v}.")

    @commands.hybrid_command(name="concluir_missao", description="Conclui uma missão e distribui recompensas (ADMs apenas)")
    @commands.has_permissions(administrator=True)
    async def concluir_missao(self, ctx):
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
