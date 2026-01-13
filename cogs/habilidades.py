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

    @commands.hybrid_command(name="usar", description="Usa uma habilidade disponível")
    async def usar(self, ctx, *, habilidade: str):
        user_id = str(ctx.author.id)
        dados = carregar_dados()
        p = dados["usuarios"].get(user_id)
        
        if not p: 
            return await ctx.send("🐾 **Lulu:** Sem alma.")

        # 1. VALIDAÇÃO DE NÍVEL
        hab_liberadas = []
        raca = p.get("raca")
        if raca in constantes.HABILIDADES_RACA:
            for faixa, lista in constantes.HABILIDADES_RACA[raca].items():
                if p["nivel"] >= int(faixa.split('-')[0]): 
                    hab_liberadas.extend([h.lower() for h in lista])

        if habilidade.lower() not in hab_liberadas:
            return await ctx.send(f"🐾 **Lulu:** Você não conhece '{habilidade}' ou seu nível é baixo.")

        # 2. CARREGAR DADOS DO JSON
        try:
            with open("habilidades.json", "r", encoding="utf-8") as f:
                biblioteca = json.load(f)
            dados_hab = biblioteca.get(raca, {}).get(habilidade.title())
        except:
            return await ctx.send("⚠️ **Erro:** Falha ao ler habilidades.json.")

        if not dados_hab:
            return await ctx.send(f"⚠️ **Erro:** Detalhes de '{habilidade}' não encontrados.")

        # 3. SISTEMA DE AZAR
        mod = -5 if p.get("azarado") else 0
        if p.get("azarado"): 
            p["azarado"] = False
            await ctx.send("⚠️ **O Azar Acumulado te atingiu! (-5)**")

        # 4. PROCESSAR LÓGICA (Usando seu arquivo habilidades_logic.py)
        res = processar_uso_habilidade(p, dados_hab, mod)
        
        embed = discord.Embed(title=f"✨ {p['nome']} usou {habilidade.title()}")

        # 5. RESULTADOS (Sucesso)
        if res["sucesso"]:
            embed.color = discord.Color.green()
            if res["cura"] > 0:
                p["pv"] = min(p.get("pv_max", 30), p["pv"] + res["cura"])
                embed.description = f"✅ **Sucesso!** (Rolagem: {res['total']})\n{dados_hab['descricao']}\n\n💖 **Cura:** +{res['cura']} PV | ❤️ **Vida:** {p['pv']}/{p.get('pv_max', 30)}"
            else:
                embed.description = f"✅ **Sucesso!** (Rolagem: {res['total']})\n{dados_hab['descricao']}\n\n⚔️ **Resultado:** {res['dano']}"
        
        # 6. RESULTADOS (Falha)
        else:
            d4 = random.randint(1, 4) # Lógica de falha mantida aqui para facilitar as frases do JSON
            consequencia = dados_hab["falha_1_2"] if d4 <= 2 else dados_hab["falha_3_4"]
            
            dano_falha_texto = ""
            if "1d4" in consequencia:
                perda = random.randint(1, 4)
                p["pv"] = max(0, p["pv"] - perda)
                dano_falha_texto = f"\n💔 **Recuo:** -{perda} PV"

            embed.color = discord.Color.red()
            embed.description = f"❌ **Falha!** (Rolagem: {res['total']})\n**Dado de Falha (d4):** {d4}\n\n**O que aconteceu:** {consequencia}{dano_falha_texto}"

        salvar_dados(dados)
        await ctx.send(embed=embed)

# SETUP FORA DA CLASSE
async def setup(bot):
    await bot.add_cog(Habilidades(bot))