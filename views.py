import discord
from database import carregar_dados, salvar_dados

class LojaCompraSelect(discord.ui.Select):
    def __init__(self, itens_categoria):
        options = [
            discord.SelectOption(label=nome, description=f"💰 {info['preco']} Krugs")
            for nome, info in itens_categoria.items()
        ]
        super().__init__(placeholder="Escolha um item...", options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            item_nome = self.values[0]
            item_info = None
            
            # Debug: mostrar o catálogo disponível
            print(f"[DEBUG] Item selecionado: {item_nome}")
            print(f"[DEBUG] Catálogo disponível: {list(self.view.catalogo.keys())}")
            
            for cat in self.view.catalogo.values():
                if item_nome in cat:
                    item_info = cat[item_nome]
                    print(f"[DEBUG] Item encontrado: {item_info}")
                    break
            
            if item_info:
                await self.view.processar_compra(interaction, item_nome, item_info)
            else:
                print(f"[DEBUG] Item NÃO encontrado no catálogo!")
                await interaction.followup.send("⚠️ Item não encontrado.", ephemeral=True)
        except Exception as e:
            print(f"[ERRO] Callback LojaCompraSelect: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f"⚠️ Erro ao processar compra: {e}", ephemeral=True)
            except:
                pass

class ItensView(discord.ui.View):
    def __init__(self, catalogo, guild_id):
        super().__init__(timeout=60)
        self.catalogo = catalogo
        self.guild_id = guild_id

    async def processar_compra(self, interaction, item_nome, item_info):
        try:
            print(f"[DEBUG] processar_compra iniciado para item: {item_nome}")
            user_id = str(interaction.user.id)
            dados = carregar_dados(self.guild_id)
            player = dados["usuarios"].get(user_id)

            if not player:
                print(f"[DEBUG] Player não encontrado: {user_id}")
                return await interaction.followup.send("🐾 **Lulu:** Sem alma, sem compras.", ephemeral=True)

            print(f"[DEBUG] Player encontrado: {player.get('nome')}, dinheiro: {player.get('dinheiro')}")

            if item_nome == "Marca da Exclusão":
                inv = player.get("inventario", [])
                if "Asa de Fada" in inv and "Olho de Dragão" in inv:
                    if "Marca da Exclusão" not in inv:
                        inv.remove("Asa de Fada")
                        inv.remove("Olho de Dragão")
                        inv.append("Marca da Exclusão")
                        salvar_dados(self.guild_id, dados)
                        return await interaction.followup.send("🔥 **Ritual concluído!** A Marca arde em sua pele.", ephemeral=True)
                    return await interaction.followup.send("⚠️ Você já tem a Marca.", ephemeral=True)
                return await interaction.followup.send("❌ **Sereth Vaul:** 'Traga os ingredientes!'", ephemeral=True)

            preco = item_info["preco"]
            print(f"[DEBUG] Preço do item: {preco}")
            
            if player.get("dinheiro", 0) >= preco:
                player["dinheiro"] -= preco
                player.setdefault("inventario", []).append(item_nome)
                salvar_dados(self.guild_id, dados)
                print(f"[DEBUG] Compra realizada! Novo saldo: {player['dinheiro']}")
                await interaction.followup.send(f"✅ **Lulu:** Você adquiriu `{item_nome}`!", ephemeral=True)
            else:
                print(f"[DEBUG] Krugs insuficientes")
                await interaction.followup.send("❌ **Lulu:** Krugs insuficientes!", ephemeral=True)
        except Exception as e:
            print(f"[ERRO] processar_compra: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f"⚠️ Erro na compra: {e}", ephemeral=True)
            except:
                pass

class LojaView(discord.ui.View):
    def __init__(self, catalogo, guild_id):
        super().__init__(timeout=60)
        self.catalogo = catalogo
        self.guild_id = guild_id

    @discord.ui.select(
        placeholder="Escolha a ala da loja...",
        options=[
            discord.SelectOption(label="O Vel", value="elfos", emoji="🍃"),
            discord.SelectOption(label="Rochas e Runas", value="khaerun", emoji="⚒️"),
            discord.SelectOption(label="Loja de Íris", value="fadas", emoji="✨"),
            discord.SelectOption(label="Casa das Bruxas", value="bruxas", emoji="🧪"),
            discord.SelectOption(label="Veneno Silencioso", value="drows", emoji="💀"),
            discord.SelectOption(label="Caravana do Último Pacto", value="humanos", emoji="🏜️"),
            discord.SelectOption(label="O Altar", value="fragmentados", emoji="⛩️")
        ]
    )
    async def select_categoria(self, interaction: discord.Interaction, select: discord.ui.Select):
        categoria = select.values[0]
        itens = self.catalogo.get(categoria, {})
        
        view = ItensView(self.catalogo, self.guild_id) 
        view.add_item(LojaCompraSelect(itens))
        
        embed = discord.Embed(title=f"Loja: {categoria.capitalize()}", color=discord.Color.gold())
        for nome, info in itens.items():
            embed.add_field(name=nome, value=f"💰 {info['preco']} Krugs\n*{info['desc']}*", inline=False)
            
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MenuRPG(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.guild_id = str(ctx.guild.id) if ctx.guild else None
        user_id = str(ctx.author.id)
        
        if self.guild_id:
            dados = carregar_dados(self.guild_id)
            self.tem_ficha = user_id in dados["usuarios"]
        else:
            self.tem_ficha = False
        
        self.ajustar_botoes()

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

    async def registrar_callback(self, interaction: discord.Interaction):
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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "🐾 **Lulu:** Ei! Não toque nos atributos dos outros. Crie sua própria ficha!", 
                ephemeral=True
            )
            return False
        return True    

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

    @discord.ui.button(label="Confirmar Ficha", style=discord.ButtonStyle.primary, row=4)
    async def confirmar(self, interaction, button):
        if self.pontos_restantes == 0:
            self.finalizado = True
            await interaction.response.edit_message(content="✅ **Ficha Finalizada!** Seus atributos foram salvos.", view=None, embed=self.gerar_embed())
            self.stop()
        else:
            await interaction.response.send_message(f"Ainda restam {self.pontos_restantes} pontos para distribuir!", ephemeral=True)