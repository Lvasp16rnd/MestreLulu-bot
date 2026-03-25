import discord
from discord.ext import commands
import random
from database import carregar_dados, salvar_dados
from cogs.logic import rolar_dado
from utils import eh_admin

def get_guild_id(ctx):
    """Obtém o guild_id do contexto, retorna None se for DM."""
    return str(ctx.guild.id) if ctx.guild else None

class BatalhaView(discord.ui.View):
    def __init__(self, mestre, atacante, defensor, dados_globais, guild_id):
        super().__init__(timeout=300)
        self.mestre = mestre
        self.p1 = atacante 
        self.p2 = defensor 
        self.dados = dados_globais
        self.guild_id = guild_id
        self.turno = atacante["user_id"]

    def processar_dano(self, atacante_obj, defensor_obj, dano_base, bonus_atk):
        """Processa o dano e retorna a mensagem de log."""
        rolagem_acerto = random.randint(1, 20)
        total_ataque = rolagem_acerto + bonus_atk
        ca_defensor = defensor_obj.get("ca", 5)
        dano_final = max(0, dano_base - ca_defensor)
        
        if rolagem_acerto <= 2:
            atacante_obj["pv"] -= 2
            return f"🌑 **RUÍNA!** Ataque falhou e você se machucou (-2 PV)."
        elif total_ataque < ca_defensor:
            return f"🛡️ **DEFESA!** Bloqueado pelo escudo ({ca_defensor})."
        elif rolagem_acerto == 20:
            dano_final = dano_base * 2  # Crítico ignora CA
            defensor_obj["pv"] -= dano_final
            return f"🌟 **GLÓRIA!** Crítico! {defensor_obj['nome']} sofreu **{dano_final}**!"
        else:
            defensor_obj["pv"] -= dano_final
            return f"⚔️ **SUCESSO!** {defensor_obj['nome']} sofreu **{dano_final}**!"

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataque_basico(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if str(interaction.user.id) != self.turno:
                return await interaction.response.send_message("🐾 **Lulu:** Sua vez não chegou!", ephemeral=True)

            ativo = self.p1 if str(interaction.user.id) == self.p1["user_id"] else self.p2
            alvo = self.p2 if ativo == self.p1 else self.p1

            # Pega atributos com valores padrão
            atributos = ativo.get("atributos", {})
            forca = atributos.get("forca", 0)
            agilidade = atributos.get("agilidade", 0)

            # Dano escalonado pelo dado do nível (rolar_dado retorna tupla: resultado, lista, modo)
            resultado_dado, _, _ = rolar_dado(ativo.get("dado_nivel", "1d6"))
            dano = resultado_dado + forca
            log = self.processar_dano(ativo, alvo, dano, agilidade)
            
            salvar_dados(self.guild_id, self.dados)
            self.turno = alvo["user_id"]

            status = f"\n💀 **{alvo['nome']} CAIU!**" if alvo["pv"] <= 0 else ""
            if alvo["pv"] <= 0: 
                self.stop()

            embed = discord.Embed(title="⚔️ Arena ⚔️", description=log + status, color=0xff0000)
            embed.add_field(name=self.p1["nome"], value=f"❤️ {self.p1['pv']} PV")
            embed.add_field(name=self.p2["nome"], value=f"❤️ {self.p2['pv']} PV")
            await interaction.response.edit_message(embed=embed, view=None if status else self)
        except Exception as e:
            print(f"Erro no combate: {e}")
            await interaction.response.send_message(f"🐾 **Lulu:** Algo deu errado no combate! Erro: {e}", ephemeral=True)

class Combate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="batalha", description="Inicia um duelo entre dois jogadores (ADMs apenas)")
    async def batalha(self, ctx, op1: discord.Member, op2: discord.Member):
        """Inicia um duelo entre dois jogadores usando a BatalhaView."""
        if not eh_admin(ctx): 
            return await ctx.send("🐾 **Lulu:** Apenas mestres podem abrir a arena.")
        
        if not ctx.guild:
            return await ctx.send("🐾 **Lulu:** Este comando só funciona em servidores!")
        
        guild_id = get_guild_id(ctx)
        dados = carregar_dados(guild_id)
        p1 = dados["usuarios"].get(str(op1.id))
        p2 = dados["usuarios"].get(str(op2.id))

        if not p1 or not p2:
            return await ctx.send("🐾 **Lulu:** Ambos os duelistas precisam de uma ficha registrada.")

        # Injeta IDs para a View saber quem é quem
        p1["user_id"], p2["user_id"] = str(op1.id), str(op2.id)

        view = BatalhaView(ctx.author, p1, p2, dados, guild_id)
            
        embed = discord.Embed(
            title="⚔️ ARENA DE OCULTA ⚔️",
            description=f"O duelo entre **{p1['nome']}** e **{p2['nome']}** começou!",
            color=0xff0000
        )
        embed.add_field(name=p1['nome'], value=f"❤️ {p1['pv']} PV", inline=True)
        embed.add_field(name=p2['nome'], value=f"❤️ {p2['pv']} PV", inline=True)
            
        await ctx.send(embed=embed, view=view)
    
async def setup(bot):
    await bot.add_cog(Combate(bot))