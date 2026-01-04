import discord
from database import carregar_dados, salvar_dados

class LojaCompraSelect(discord.ui.Select):
    def __init__(self, itens_categoria):
        options = [
            discord.SelectOption(label=nome, description=f"Preço: {info['preco']} Krugs", emoji="💰")
            for nome, info in itens_categoria.items()
        ]
        super().__init__(placeholder="Escolha um item para comprar...", options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        dados = carregar_dados()
        usuario = dados["usuarios"].get(user_id)

        if not usuario:
            return await interaction.response.send_message("🐾 **Lulu:** Você não tem uma alma registrada.", ephemeral=True)

        item_nome = self.values[0]
        # Aqui buscamos o item em todas as categorias para achar o preço
        lojas = interaction.view.catalogo
        item_info = None
        for cat in lojas.values():
            if item_nome in cat:
                item_info = cat[item_nome]
                break

        if usuario["dinheiro"] >= item_info["preco"]:
            usuario["dinheiro"] -= item_info["preco"]
            usuario["inventario"].append(item_nome)
            salvar_dados(dados)
            await interaction.response.send_message(f"✨ **Lulu:** Você adquiriu `{item_nome}`! Use com sabedoria (ou não).", ephemeral=True)
        else:
            await interaction.response.send_message("🐾 **Lulu:** Você é pobre demais para este item.", ephemeral=True)

class LojaView(discord.ui.View):
    def __init__(self, catalogo):
        super().__init__(timeout=60)
        self.catalogo = catalogo

    @discord.ui.select(
        placeholder="Escolha a ala da loja...",
        options=[
            discord.SelectOption(label="Elfos de Elandor", value="elfos", emoji="🍃"),
            discord.SelectOption(label="Khaerun de Kharr-Dum", value="khaerun", emoji="⚒️"),
            discord.SelectOption(label="Fadas de Íris", value="fadas", emoji="✨"),
            discord.SelectOption(label="Casa das Bruxas", value="bruxas", emoji="🧪")
        ]
    )
    async def select_categoria(self, interaction: discord.Interaction, select: discord.ui.Select):
        categoria = select.values[0]
        itens = self.catalogo.get(categoria, {})
        
        # Criamos um novo menu para os itens desta categoria
        view = discord.ui.View()
        view.add_item(LojaCompraSelect(itens))
        view.catalogo = self.catalogo # Passamos o catálogo adiante
        
        embed = discord.Embed(title=f"Loja: {categoria.capitalize()}", color=discord.Color.gold())
        for nome, info in itens.items():
            embed.add_field(name=nome, value=f"💰 {info['preco']} Krugs\n*{info['desc']}*", inline=False)
            
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)