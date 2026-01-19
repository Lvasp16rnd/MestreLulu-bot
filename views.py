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
        lojas = interaction.view.catalogo
        item_info = None
        
        for cat in lojas.values():
            if item_nome in cat:
                item_info = cat[item_nome]
                break

        if item_nome == "Marca da Exclusão":
            inventario = usuario.get("inventario", [])
        
            if "Asa de Fada" in inventario and "Olho de Dragão" in inventario:
                if "Marca da Exclusão" not in inventario:
                    inventario.remove("Asa de Fada")
                    inventario.remove("Olho de Dragão")
                    inventario.append("Marca da Exclusão")
                    salvar_dados(dados)
                    return await interaction.response.send_message(
                        "🔥 **O ritual foi concluído!** Sereth Vaul queimou a Marca em sua pele. Você não é mais um de nós.", 
                        ephemeral=True
                    )
                else:
                    return await interaction.response.send_message("⚠️ Você já carrega a Marca.", ephemeral=True)
            else:
                return await interaction.response.send_message(
                    "❌ **Sereth Vaul rosna:** 'Traga-me uma **Asa de Fada** e um **Olho de Dragão**, ou saia daqui!'", 
                    ephemeral=True
                )
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
            discord.SelectOption(label="O Vel", value="elfos", emoji="🍃"),
            discord.SelectOption(label="Rochas e Runas", value="khaerun", emoji="⚒️"),
            discord.SelectOption(label="Loja de Íris", value="fadas", emoji="✨"),
            discord.SelectOption(label="Casa das Bruxas", value="bruxas", emoji="🧪"),
            discord.SelectOption(label="Veneno Silencioso", value="drows", emoji="💀"),
            discord.SelectOption(label="A Caravna do Deserto", value="humanos", emoji="🏜️"),
            discord.SelectOption(label="O Altar", value="fragmentados", emoji="⛩️")
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

    async def processar_compra(self, interaction, item_nome, dados_item):
        user_id = str(interaction.user.id)
        dados = carregar_dados()
        player = dados["usuarios"][user_id]

        # --- LÓGICA ESPECIAL PARA A MARCA DA EXCLUSÃO ---
        if item_nome == "Marca da Exclusão":
            inventario = player.get("inventario", [])
            
            if "Asa de Fada" in inventario and "Olho de Dragão" in inventario:
                inventario.remove("Asa de Fada")
                inventario.remove("Olho de Dragão")
                
                if "Marca da Exclusão" not in inventario:
                    inventario.append("Marca da Exclusão")
                    salvar_dados(dados)
                    await interaction.response.send_message(
                        "🔥 **O ritual foi concluído!** Sereth Vaul queimou a Marca em sua pele. Você não é mais um de nós.", 
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message("⚠️ Você já carrega a Marca.", ephemeral=True)
                return
            else:
                await interaction.response.send_message(
                    "❌ **Sereth Vaul rosna:** 'Traga-me uma Asa de Fada e um Olho de Dragão, ou saia daqui!'", 
                    ephemeral=True
                )
                return

        # --- LÓGICA DE COMPRA NORMAL (DINHEIRO) ---
        preco = dados_item["preco"]
        if player["dinheiro"] >= preco:
            player["dinheiro"] -= preco
            player["inventario"].append(item_nome)
            salvar_dados(dados)
            await interaction.response.send_message(f"✅ Você comprou **{item_nome}**!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Krugs insuficientes!", ephemeral=True)

class MenuRPG(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        
        self.tem_ficha = user_id in dados["usuarios"]
        self.ajustar_botoes()

    # TRAVA DE SEGURANÇA: Só o dono do menu pode clicar
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("🐾 **Lulu:** Este menu não te pertence, intrometido!", ephemeral=True)
            return False
        return True

    def ajustar_botoes(self):
        self.clear_items()
        if not self.tem_ficha:
            btn_registrar = discord.ui.Button(label="Criar Ficha", style=discord.ButtonStyle.green, emoji="✨")
            btn_registrar.callback = self.registrar_callback
            self.add_item(btn_registrar)
        else:
            # Seus botões de Ficha, Inv e Loja...
            btn_ficha = discord.ui.Button(label="Ficha", style=discord.ButtonStyle.blurple, emoji="📜")
            btn_ficha.callback = self.ver_ficha_callback
            self.add_item(btn_ficha)

            btn_inv = discord.ui.Button(label="Inventário", style=discord.ButtonStyle.gray, emoji="🎒")
            btn_inv.callback = self.ver_inv_callback
            self.add_item(btn_inv)

            btn_loja = discord.ui.Button(label="Loja", style=discord.ButtonStyle.gray, emoji="💰")
            btn_loja.callback = self.ver_loja_callback
            self.add_item(btn_loja)
            
        btn_sair = discord.ui.Button(label="Sair do Menu", style=discord.ButtonStyle.red, emoji="❌")
        btn_sair.callback = self.sair_callback
        self.add_item(btn_sair)

    # --- CALLBACKS ---
    async def registrar_callback(self, interaction: discord.Interaction):
        # Removemos o menu para não dar conflito com o registro por texto/menu
        await interaction.response.edit_message(content="🐾 **Lulu:** Iniciando registro...", view=None)
        await self.ctx.invoke(self.ctx.bot.get_command('registrar'))
        self.stop()

    async def ver_ficha_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.ctx.invoke(self.ctx.bot.get_command('ficha'))

    async def ver_inv_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.ctx.invoke(self.ctx.bot.get_command('inventario'))

    async def ver_loja_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.ctx.invoke(self.ctx.bot.get_command('loja'))

    async def sair_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="🐾 **Mestre Lulu:** O menu foi fechado.", view=None)
        self.stop()

class SelecaoRacaView(discord.ui.View):
    def __init__(self, racas_disponiveis):
        super().__init__(timeout=30.0) 
        self.raca_escolhida = None

        options = [
            discord.SelectOption(label=raca, description=f"Linhagem {raca}") 
            for raca in racas_disponiveis
        ]
        
        self.select = discord.ui.Select(
            placeholder="Escolha sua linhagem...",
            options=options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction: discord.Interaction):
        self.raca_escolhida = self.select.values[0]
        await interaction.response.defer()
        self.stop() 

class DistribuiPontosView(discord.ui.View):
    def __init__(self, ctx, raca):
        super().__init__(timeout=120.0)
        self.ctx = ctx
        self.raca = raca
        self.pontos_restantes = 7
        self.attrs = {
            "Força": 0, "Agilidade": 0, "Intelecto": 0, 
            "Presença": 0, "Carisma": 0
        }
        self.finalizado = False

    def gerar_embed(self):
        embed = discord.Embed(
            title="✨ Distribuição de Atributos",
            description=f"Raça: **{self.raca}**\nDistribua seus **7 pontos** iniciais.",
            color=0x71368a
        )
        texto_attrs = ""
        for k, v in self.attrs.items():
            texto_attrs += f"**{k}:** {v}\n"
        
        embed.add_field(name="📊 Atributos", value=texto_attrs, inline=True)
        embed.add_field(name="💎 Pontos Restantes", value=f"**{self.pontos_restantes}**", inline=True)
        embed.set_footer(text="Use os botões para ajustar. Clique em Confirmar ao terminar.")
        return embed

    async def atualizar(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.gerar_embed(), view=self)

    # --- BOTÕES (FORÇA - Row 0) ---
    @discord.ui.button(label="FOR +", style=discord.ButtonStyle.green, row=0)
    async def for_mais(self, interaction, button):
        if self.pontos_restantes > 0:
            self.attrs["Força"] += 1; self.pontos_restantes -= 1
            await self.atualizar(interaction)
        else: await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="FOR -", style=discord.ButtonStyle.red, row=0)
    async def for_menos(self, interaction, button):
        if self.attrs["Força"] > 0:
            self.attrs["Força"] -= 1; self.pontos_restantes += 1
            await self.atualizar(interaction)
        else: await interaction.response.defer()

    # --- BOTÕES (AGILIDADE - Row 1) ---
    @discord.ui.button(label="AGI +", style=discord.ButtonStyle.green, row=1)
    async def agi_mais(self, interaction, button):
        if self.pontos_restantes > 0:
            self.attrs["Agilidade"] += 1; self.pontos_restantes -= 1
            await self.atualizar(interaction)
        else: await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="AGI -", style=discord.ButtonStyle.red, row=1)
    async def agi_menos(self, interaction, button):
        if self.attrs["Agilidade"] > 0:
            self.attrs["Agilidade"] -= 1; self.pontos_restantes += 1
            await self.atualizar(interaction)
        else: await interaction.response.defer()

    # --- BOTÕES (INTELECTO - Row 2) ---
    @discord.ui.button(label="INT +", style=discord.ButtonStyle.green, row=2)
    async def int_mais(self, interaction, button):
        if self.pontos_restantes > 0:
            self.attrs["Intelecto"] += 1; self.pontos_restantes -= 1
            await self.atualizar(interaction)
        else: await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="INT -", style=discord.ButtonStyle.red, row=2)
    async def int_menos(self, interaction, button):
        if self.attrs["Intelecto"] > 0:
            self.attrs["Intelecto"] -= 1; self.pontos_restantes += 1
            await self.atualizar(interaction)
        else: await interaction.response.defer()

    # --- BOTÕES (PRESENÇA - Row 3) ---
    @discord.ui.button(label="PRE +", style=discord.ButtonStyle.green, row=3)
    async def pre_mais(self, interaction, button):
        if self.pontos_restantes > 0:
            self.attrs["Presença"] += 1; self.pontos_restantes -= 1
            await self.atualizar(interaction)
        else: await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="PRE -", style=discord.ButtonStyle.red, row=3)
    async def pre_menos(self, interaction, button):
        if self.attrs["Presença"] > 0:
            self.attrs["Presença"] -= 1; self.pontos_restantes += 1
            await self.atualizar(interaction)
        else: await interaction.response.defer()

    # --- BOTÕES (CARISMA - Row 4) ---
    @discord.ui.button(label="CAR +", style=discord.ButtonStyle.green, row=4)
    async def car_mais(self, interaction, button):
        if self.pontos_restantes > 0:
            self.attrs["Carisma"] += 1; self.pontos_restantes -= 1
            await self.atualizar(interaction)
        else: await interaction.response.send_message("Sem pontos!", ephemeral=True)

    @discord.ui.button(label="CAR -", style=discord.ButtonStyle.red, row=4)
    async def car_menos(self, interaction, button):
        if self.attrs["Carisma"] > 0:
            self.attrs["Carisma"] -= 1; self.pontos_restantes += 1
            await self.atualizar(interaction)
        else: await interaction.response.defer()

    # --- BOTÃO FINAL (Abaixo de todos) ---
    @discord.ui.button(label="Confirmar Ficha", style=discord.ButtonStyle.primary, row=4)
    async def confirmar(self, interaction, button):
        if self.pontos_restantes == 0:
            self.finalizado = True
            await interaction.response.send_message("✅ Atributos confirmados!", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message(f"Ainda restam {self.pontos_restantes} pontos para distribuir!", ephemeral=True)