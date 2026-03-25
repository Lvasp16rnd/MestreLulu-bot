import discord
from discord.ext import commands
from database import carregar_dados, salvar_dados
import constantes
from views import LojaView, SelecaoRacaView, DistribuiPontosView
from utils import eh_admin

def get_guild_id(ctx):
    """Obtém o guild_id do contexto, retorna None se for DM."""
    return str(ctx.guild.id) if ctx.guild else None

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="registrar", description="Registra um novo jogador no sistema")
    async def registrar(self, ctx):
        if not ctx.guild:
            return await ctx.send("🐾 **Lulu:** Este comando só funciona em servidores!")
        
        guild_id = get_guild_id(ctx)
        user_id = str(ctx.author.id)
        dados = carregar_dados(guild_id)
        if user_id in dados["usuarios"]:
            return await ctx.send("🐾 **Mestre Lulu:** Tu já tens uma ficha.")

        view_raca = SelecaoRacaView(list(constantes.RACAS.keys()))
        msg = await ctx.send("🐾 **Mestre Lulu:** Escolha sua linhagem:", view=view_raca)
        await view_raca.wait()
        
        if not view_raca.raca_escolhida:
            return await msg.edit(content="🐾 **Lulu:** Tempo esgotado.", view=None)

        raca = view_raca.raca_escolhida

        view_pts = DistribuiPontosView(ctx, raca)
        await msg.edit(content=None, embed=view_pts.gerar_embed(), view=view_pts)
        await view_pts.wait()

        if not view_pts.finalizado:
            return await msg.edit(content="🐾 **Lulu:** Cancelado por inatividade.", embed=None, view=None)

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
        
        salvar_dados(guild_id, dados)
        await msg.edit(content=f"✨ **Mestre Lulu:** Ficha de {ctx.author.name} gravada! Bem-vindo ao RPG.", embed=None, view=None)

    @commands.hybrid_command(name="loja", description="Mostra a loja de itens disponíveis")
    async def loja(self, ctx):
        if not ctx.guild:
            return await ctx.send("🐾 **Lulu:** Este comando só funciona em servidores!")
        
        await ctx.defer() 
        
        try:
            guild_id = get_guild_id(ctx)
            dados = carregar_dados(guild_id)
            import copy
            cat = copy.deepcopy(constantes.LOJA_ITENS)
            
            if "loja_custom" in dados:
                for c, it in dados["loja_custom"].items():
                    if c in cat: 
                        cat[c].update(it)
                    else: 
                        cat[c] = it
            
            await ctx.send("🐾 **Mestre Lulu:** Não toque em nada, ou vai perder um dedo.", view=LojaView(cat, guild_id))
            
        except Exception as e:
            print(f"Erro na loja: {e}")
            await ctx.send("⚠️ **Mestre Lulu:** Minha loja está bagunçada agora, volte mais tarde.")

    @commands.hybrid_command(name="lulu_ajuda", description="Mostra o manual de ordens do Mestre Lulu")
    async def lulu_ajuda(self, ctx):
        """Mostra o manual de ordens do Mestre Lulu atualizado."""
        embed = discord.Embed(
            title="🐾 Central de Ajuda do Mestre Lulu",
            description="Olá! Eu sou o Mestre Lulu. Não toque em nada, mas se tocar, use estes comandos:",
            color=0x71368a
        )
        
        inicio = (
            "**!registrar** - Cria sua ficha de personagem.\n"
            "**!ficha** - Veja seu status, atributos e Krugs.\n"
            "**!menu** - Abre o painel interativo (Ficha, Inv, Loja)."
        )
        embed.add_field(name="📋 Primeiros Passos", value=inicio, inline=False)
        
        aventura = (
            "**!usar <nome>** - Usa uma habilidade (Bônus de itens aplicados automaticamente).\n"
            "**!testar <atributo>** - Faz um teste de atributo (FOR, AGI, INT, PRE, CAR).\n"
            "**!descansar** - Recupera PV usando uma carga de acampamento (⛺).\n"
            "**!dado <expressão>** - Rolagem de dados (ex: `!dado 2d6+3` ou `!r 1d20`)."
        )
        embed.add_field(name="⚔️ Ação e Aventura", value=aventura, inline=False)

        economia = (
            "**!trabalhar** - Realize tarefas para ganhar K$ (1h de cooldown).\n"
            "**!loja** - Visite as alas do mercado para comprar equipamentos.\n"
            "**!inventario** - Veja o que você carrega na mochila.\n"
            "**!beber <item>** - Usa uma poção ou item bebível do inventário."
        )
        embed.add_field(name="💰 Economia e Itens", value=economia, inline=False)
        
        social = (
            "**!historico** - Mostra as últimas missões concluídas."
        )
        embed.add_field(name="📖 Social", value=social, inline=False)

        regras = (
            "• **Tags de Itens:** Ter itens como *Flechas de Sol* ou *Frasco de Luz* no inventário dá bônus automáticos ao usar certas habilidades.\n"
            "• **Marca da Exclusão:** Troque uma *Asa de Fada* + *Olho de Dragão* no Altar (Loja Fragmentados) por defesa permanente.\n"
            "• **Level Up:** Ao ganhar XP suficiente do Mestre, você sobe de nível e recupera toda sua vida!"
        )
        embed.add_field(name="📜 Regras e Segredos", value=regras, inline=False)

        if eh_admin(ctx):
            mestre = (
                "**!dar_xp @usuario <qtd>** - Dá XP (processa níveis automaticamente).\n"
                "**!upar @usuario [n]** - Força o aumento de nível imediato.\n"
                "**!setar @usuario <atributo> <valor>** - Define atributos, nível ou XP.\n"
                "**!lulu_azar @usuario** - Amaldiçoa com -5 no próximo dado.\n"
                "**!lulu_reset [qtd]** - Dá cargas de descanso para todos."
            )
            embed.add_field(name="👑 Comandos de Mestre", value=mestre, inline=False)
            
            missoes = (
                "**!concluir_missao** - Conclui uma missão e distribui recompensas.\n"
                "**!sorteio_missao** - Sorteia uma equipe diversificada para missão.\n"
                "**!evento <nome> <DT> <atributo> <dano>** - Cria um desafio para todos."
            )
            embed.add_field(name="🗺️ Gestão de Missões", value=missoes, inline=False)
            
            combate = (
                "**!batalha @p1 @p2** - Inicia um duelo entre dois jogadores."
            )
            embed.add_field(name="⚔️ Combate", value=combate, inline=False)

        embed.set_footer(text="Mestre Lulu: 'A sorte favorece os audazes... e quem me trouxer petiscos.'")
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sistema(bot))