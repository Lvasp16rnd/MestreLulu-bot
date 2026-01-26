import discord
from discord.ext import commands
from database import carregar_dados, salvar_dados
import constantes
from views import LojaView, SelecaoRacaView, DistribuiPontosView

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="registrar", description="Registra um novo jogador no sistema")
    async def registrar(self, ctx):
        user_id = str(ctx.author.id)
        dados = carregar_dados()
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
        
        salvar_dados(dados)
        await msg.edit(content=f"✨ **Mestre Lulu:** Ficha de {ctx.author.name} gravada! Bem-vindo ao RPG.", embed=None, view=None)

    @commands.hybrid_command(name="loja", description="Mostra a loja de itens disponíveis")
    async def loja(self, ctx):
        await ctx.defer() 
        
        try:
            dados = carregar_dados()
            import copy
            cat = copy.deepcopy(constantes.LOJA_ITENS)
            
            if "loja_custom" in dados:
                for c, it in dados["loja_custom"].items():
                    if c in cat: 
                        cat[c].update(it)
                    else: 
                        cat[c] = it
            
            await ctx.send("🐾 **Mestre Lulu:** Não toque em nada, ou vai perder um dedo.", view=LojaView(cat))
            
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
        
        aventura = (
            "**!ficha** - Veja seu status, atributos e Krugs.\n"
            "**!menu** - Abre o painel interativo (Ficha, Inv, Loja).\n"
            "**!usar <nome>** - Usa uma habilidade (Bônus de itens aplicados automaticamente).\n"
            "**!descansar** - Recupera PV usando uma carga de acampamento (⛺).\n"
            "**!d <expressão>** - Rolagem de dados (ex: `!d 1d20+2`)."
        )
        embed.add_field(name="⚔️ Ação e Aventura", value=aventura, inline=False)

        economia = (
            "**!trabalhar** - Realize tarefas para ganhar K$ (1h de cooldown).\n"
            "**!loja** - Visite as alas do mercado para comprar equipamentos.\n"
            "**!inventario** - Veja o que você carrega na mochila."
        )
        embed.add_field(name="💰 Economia e Itens", value=economia, inline=False)

        regras = (
            "• **Tags de Itens:** Ter itens como *Flechas de Sol* ou *Frasco de Luz* no inventário dá bônus automáticos ao usar certas habilidades.\n"
            "• **Marca da Exclusão:** Troque uma *Asa de Fada* + *Olho de Dragão* no Altar (Loja Fragmentados) por defesa permanente.\n"
            "• **Level Up:** Ao ganhar XP suficiente do Mestre, você sobe de nível e recupera toda sua vida!"
        )
        embed.add_field(name="📜 Regras e Segredos", value=regras, inline=False)

        if ctx.author.guild_permissions.administrator:
            mestre = (
                "**!dar_xp @usuario <qtd>** - Dá XP (processa níveis e sobras automaticamente).\n"
                "**!upar @usuario [n]** - Força o aumento de nível imediato.\n"
                "**!registrar @usuario** - Inicia o processo de criação de ficha.\n"
                "**!lulu_azar @usuario** - Amaldiçoa com -5 no próximo dado."
            )
            embed.add_field(name="👑 Comandos de Mestre", value=mestre, inline=False)

        embed.set_footer(text="Mestre Lulu: 'A sorte favorece os audazes... e quem me trouxer petiscos.'")
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sistema(bot))