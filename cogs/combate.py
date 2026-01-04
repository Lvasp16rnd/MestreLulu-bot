import discord
import random
from database import salvar_dados
from cogs.logic import rolar_dado

class BatalhaView(discord.ui.View):
    def __init__(self, mestre, atacante, defensor, dados_globais):
        super().__init__(timeout=300)
        self.mestre = mestre
        self.p1 = atacante 
        self.p2 = defensor 
        self.dados = dados_globais
        self.turno = atacante["user_id"]

    async def processar_dano(self, interaction, atacante_obj, defensor_obj, dano_base, bonus_atk):
        rolagem_acerto = random.randint(1, 20)
        total_ataque = rolagem_acerto + bonus_atk
        dano_final = max(0, dano_base - defensor_obj["ca"])
        
        if rolagem_acerto <= 2:
            atacante_obj["pv"] -= 2
            return f"🌑 **RUÍNA!** Ataque falhou e você se machucou (-2 PV)."
        elif total_ataque < defensor_obj["ca"]:
            return f"🛡️ **DEFESA!** Bloqueado pelo escudo ({defensor_obj['ca']})."
        elif rolagem_acerto == 20:
            dano_final *= 2
            defensor_obj["pv"] -= dano_final
            return f"🌟 **GLÓRIA!** Crítico! {defensor_obj['nome']} sofreu **{dano_final}**!"
        else:
            defensor_obj["pv"] -= dano_final
            return f"⚔️ **SUCESSO!** {defensor_obj['nome']} sofreu **{dano_final}**!"

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def ataque_basico(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.turno:
            return await interaction.response.send_message("🐾 **Lulu:** Sua vez não chegou!", ephemeral=True)

        ativo = self.p1 if str(interaction.user.id) == self.p1["user_id"] else self.p2
        alvo = self.p2 if ativo == self.p1 else self.p1

        # Dano escalonado pelo dado do nível
        dano = rolar_dado(ativo.get("dado_nivel", "1d6")) + ativo["atributos"]["forca"]
        log = await self.processar_dano(interaction, ativo, alvo, dano, ativo["atributos"]["agilidade"])
        
        salvar_dados(self.dados)
        self.turno = alvo["user_id"]

        status = f"\n💀 **{alvo['nome']} CAIU!**" if alvo["pv"] <= 0 else ""
        if alvo["pv"] <= 0: self.stop()

        embed = discord.Embed(title="Arena", description=log + status, color=0xff0000)
        embed.add_field(name=self.p1["nome"], value=f"❤️ {self.p1['pv']} PV")
        embed.add_field(name=self.p2["nome"], value=f"❤️ {self.p2['pv']} PV")
        await interaction.response.edit_message(embed=embed, view=None if status else self)