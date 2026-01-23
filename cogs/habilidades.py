import discord
from discord.ext import commands
import json
import random 
from database import carregar_dados, salvar_dados
import constantes
from habilidades_logic import processar_uso_habilidade 

class Habilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _obter_habilidades_usuario(self, user_id: str) -> list[str]:
        """Retorna a lista de habilidades disponíveis para o usuário baseado em raça e nível."""
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p:
            return []
        
        raca = p.get("raca")
        nivel = p.get("nivel", 1)
        
        hab_liberadas = []
        if raca in constantes.HABILIDADES_RACA:
            for faixa, lista in constantes.HABILIDADES_RACA[raca].items():
                try:
                    inicio_faixa = int(faixa.split('-')[0])
                    if nivel >= inicio_faixa:
                        hab_liberadas.extend(lista)
                except Exception:
                    pass
        
        return hab_liberadas

    async def habilidade_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        """Autocomplete que mostra as habilidades disponíveis do jogador."""
        user_id = str(interaction.user.id)
        habilidades = self._obter_habilidades_usuario(user_id)
        
        # Filtra as habilidades que correspondem ao texto digitado
        opcoes = [
            discord.app_commands.Choice(name=hab, value=hab)
            for hab in habilidades
            if current.lower() in hab.lower()
        ]
        
        # Discord limita a 25 opções no autocomplete
        return opcoes[:25]

    @commands.hybrid_command(name="usar", description="Usa uma habilidade ou lista as disponíveis")
    @discord.app_commands.describe(habilidade="Nome da habilidade (deixe vazio para ver a lista)")
    @discord.app_commands.autocomplete(habilidade=habilidade_autocomplete)
    async def usar(self, ctx, *, habilidade: str = None):
        # 1. Carregamento de dados frescos
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p: 
            return await ctx.send("🐾 **Lulu:** Você ainda não possui uma ficha registrada.")

        raca = p.get("raca")
        nivel = p.get("nivel", 1)

        # 2. Mapeamento de Habilidades Liberadas (Baseado na sua tabela em constantes.py)
        hab_liberadas = []
        if raca in constantes.HABILIDADES_RACA:
            for faixa, lista in constantes.HABILIDADES_RACA[raca].items():
                try:
                    # Converte "1-2" -> inicio=1
                    inicio_faixa = int(faixa.split('-')[0])
                    # Se o nível do jogador atingiu ou passou o início da faixa, ele conhece as habs
                    if nivel >= inicio_faixa:
                        hab_liberadas.extend(lista)
                except Exception as e:
                    print(f"Erro ao ler faixa {faixa}: {e}")

        # --- LÓGICA DE LISTAGEM (Caso o usuário não digite o nome da habilidade) ---
        if not habilidade or habilidade.strip() == "":
            if not hab_liberadas:
                return await ctx.send(f"🐾 **Lulu:** Como um **{raca}** nível **{nivel}**, você ainda não despertou habilidades.")

            embed_lista = discord.Embed(
                title=f"⚔️ Habilidades Disponíveis - {p['nome']}",
                description=f"Seu sangue **{raca}** (Lvl {nivel}) permite usar:",
                color=0x3498db
            )
            # Formata a lista para o Embed
            texto_formatado = "\n".join([f"✨ **{h}**" for h in hab_liberadas])
            embed_lista.add_field(name="Grimório de Técnicas", value=texto_formatado)
            embed_lista.set_footer(text="Use !usar [nome] para ativar")
            
            return await ctx.send(embed=embed_lista)

        # --- BUSCA DA HABILIDADE DIGITADA ---
        # Remove aspas e espaços extras, busca ignorando maiúsculas
        hab_limpa = habilidade.replace('"', '').replace("'", "").strip().lower()
        hab_nome_original = next((h for h in hab_liberadas if h.lower() == hab_limpa), None)

        if not hab_nome_original:
            opcoes = ", ".join([f"`{h}`" for h in hab_liberadas])
            return await ctx.send(f"🐾 **Lulu:** Você não conhece '{habilidade}'. Disponíveis: {opcoes}")

        # --- PROCESSAMENTO DA HABILIDADE ---
        try:
            import json
            from habilidades_logic import processar_uso_habilidade
            
            with open("habilidades.json", "r", encoding="utf-8") as f:
                biblioteca = json.load(f)
                # O .get(hab_nome_original) garante que usemos o nome com as maiúsculas corretas do JSON
                dados_hab = biblioteca.get(raca, {}).get(hab_nome_original)

            if not dados_hab:
                return await ctx.send(f"⚠️ **Erro:** Detalhes de '{hab_nome_original}' não encontrados em habilidades.json.")

            # Sistema de Azar (Modificador -5)
            mod = -5 if p.get("azarado") else 0
            azar_msg = "⚠️ **O Azar te atingiu! (-5 na rolagem)**\n" if p.get("azarado") else ""
            if p.get("azarado"): p["azarado"] = False

            # Executa a lógica matemática (HabilidadesLogic)
            res = processar_uso_habilidade(p, dados_hab, mod)
            
            embed = discord.Embed(title=f"✨ {p['nome']} usou {hab_nome_original}")
            
            # Detalhes do cálculo visual
            info_calculo = f"🎲 **Teste:** {res['dado_puro']} + {res['atributo_valor']} ({res['atributo_nome']})"
            if mod != 0: info_calculo += f" - 5 (Azar)"
            info_calculo += f" = **{res['total']}**"

            # 5. RESULTADOS (Sucesso)
            if res["sucesso"]:
                embed.color = discord.Color.green()
                if res["cura"] > 0:
                    # Limita a cura ao PV Máximo estático da ficha
                    pv_max = p.get("pv_max", 30)
                    p["pv"] = min(pv_max, p["pv"] + res["cura"])
                    embed.description = f"{azar_msg}✅ **Sucesso!**\n{info_calculo} (DT: {res['dt_applied']})\n\n*{dados_hab['descricao']}*\n\n💖 **Cura:** +{res['cura']} PV | ❤️ **Vida:** {p['pv']}/{pv_max}"
                else:
                    embed.description = f"{azar_msg}✅ **Sucesso!**\n{info_calculo} (DT: {res['dt_applied']})\n\n*{dados_hab['descricao']}*\n\n⚔️ **Dano:** {res['dano']}"
            
            # 6. RESULTADOS (Falha)
            else:
                import random
                d4 = random.randint(1, 4)
                consequencia = dados_hab["falha_1_2"] if d4 <= 2 else dados_hab["falha_3_4"]
                
                dano_falha_texto = ""
                if "1d4" in consequencia:
                    perda = random.randint(1, 4)
                    p["pv"] = max(0, p["pv"] - perda)
                    dano_falha_texto = f"\n💔 **Recuo:** -{perda} PV"

                embed.color = discord.Color.red()
                embed.description = f"{azar_msg}❌ **Falha!**\n{info_calculo} (DT: {res['dt_applied']})\n**Dado de Falha (d4):** {d4}\n\n**O que aconteceu:** {consequencia}{dano_falha_texto}"

            if res["logs"]:
                embed.add_field(name="🎒 Itens Utilizados", value="\n".join([f"• {log}" for log in res["logs"]]), inline=False)

            # Salva todas as alterações (PV, Azar, etc)
            salvar_dados(dados)
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"ERRO NO COMANDO USAR: {e}")
            await ctx.send("🐾 **Lulu:** Tive um problema ao consultar minha biblioteca de magias.")

async def setup(bot):
    await bot.add_cog(Habilidades(bot))