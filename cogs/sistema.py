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
        """Mostra o manual de ordens do Mestre Lulu."""
        embed = discord.Embed(
            title="🐾 Central de Ajuda do Mestre Lulu",
            description="Olá! Eu sou o Mestre Lulu, o guardião da sua jornada. Aqui estão as ordens que eu entendo:",
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

        # Seção de Regras (Interação)
        regras = (
            "• **Sucesso:** Tire um valor igual ou maior que a DT.\n"
            "• **Azar:** Se você estiver azarado (💀), sua próxima rolagem tem -5.\n"
            "• **Cura:** O descanso recupera PV baseado no seu nível atual."
        )
        embed.add_field(name="📜 Regras Rápidas", value=regras, inline=False)

        # Seção para o Mestre
        if ctx.author.guild_permissions.administrator:
            mestre = (
                "**!registrar @usuario <raça>** - Cria uma nova ficha.\n"
                "**!upar @usuario [n]** - Sobe o nível e dá bônus.\n"
                "**!lulu_reset [n]** - Dá cargas de descanso para todos.\n"
                "**!lulu_azar @usuario** - Amaldiçoa um jogador com -5."
            )
            embed.add_field(name="👑 Comandos de Mestre", value=mestre, inline=False)

        embed.set_footer(text="O Mestre Lulu está de olho em você! Boa sorte na mesa.")
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sistema(bot))