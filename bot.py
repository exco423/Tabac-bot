import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connecté : {bot.user}")

@bot.tree.command(name="recrute", description="Recruter un membre dans le Tabac")
@app_commands.describe(membre="Le membre à recruter", ticket="Le ticket de la personne")
async def recrute(interaction: discord.Interaction, membre: discord.Member, ticket: discord.TextChannel):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    guild = bot.get_guild(1474559198544138391)
    categorie = guild.get_channel(1474807318997897487)

    role_tabac = guild.get_role(1474565904011497522)
    role_vendeur = guild.get_role(1474562293198098717)

    if not role_tabac or not role_vendeur:
        await interaction.response.send_message("❌ Rôles introuvables !", ephemeral=True)
        return

    # Ajouter les rôles
    await membre.add_roles(role_tabac, role_vendeur)

    # Renommer et déplacer le ticket
    await ticket.edit(name=f"rapport-{membre.display_name.lower()}", category=categorie)

    # Envoyer les 2 messages
    await interaction.response.defer()

    await interaction.followup.send("Les rôles de Tabac ont bien été attribuer ! ✅")

    await interaction.channel.send(
        f"Bien joué {membre.mention}, tu as été recruté dans le Tabac ! 🚬\n"
        f"Maintenant je te laisse aller voir tout ça :\n"
        f"<#1474569375901155448>\n"
        f"<#1495452484418801714>\n"
        f"<#1482797251280638164>\n"
        f"<#1474570039716741282>"
    )

bot.run(os.getenv("TOKEN"))