import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=1474559198544138391))
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

    await membre.add_roles(role_tabac, role_vendeur)
    await ticket.edit(name=f"rapport-{membre.display_name.lower()}", category=categorie)

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

@bot.tree.command(name="demote", description="Retirer les rôles Tabac d'un membre")
@app_commands.describe(membre="Le membre à démoter", raison="La raison du demote")
async def demote(interaction: discord.Interaction, membre: discord.Member, raison: str):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    guild = bot.get_guild(1474559198544138391)

    role_tabac = guild.get_role(1474565904011497522)
    role_vendeur = guild.get_role(1474562293198098717)
    role_citoyens = guild.get_role(1474571994094637157)

    await membre.remove_roles(role_tabac, role_vendeur)
    await membre.add_roles(role_citoyens)

    salon = guild.get_channel(1474570131312218313)

    await salon.send(
        f"# Avertissement :\n"
        f"* Personnes : {membre.mention}\n"
        f"* Raison : {raison}\n"
        f"* Sanction : Demote"
    )

    await interaction.response.send_message("✅ Le membre a bien été démote !", ephemeral=True)

@bot.tree.command(name="avert", description="Donner un avertissement à un membre")
@app_commands.describe(membre="Le membre à avertir", raison="La raison de l'avertissement", numero="Le numéro de l'avertissement")
@app_commands.choices(numero=[
    app_commands.Choice(name="Avertissement 1", value="1"),
    app_commands.Choice(name="Avertissement 2", value="2"),
])
async def avert(interaction: discord.Interaction, membre: discord.Member, raison: str, numero: str):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    guild = bot.get_guild(1474559198544138391)

    if numero == "1":
        role_avert = guild.get_role(1482872715525492807)
    else:
        role_avert = guild.get_role(1482872877513445396)

    await membre.add_roles(role_avert)

    salon = guild.get_channel(1474570131312218313)

    await salon.send(
        f"# Avertissement :\n"
        f"* Personne : {membre.mention}\n"
        f"* Raison : {raison}\n"
        f"* Sanction : Avertissement {numero}"
    )

    await interaction.response.send_message(f"✅ Avertissement {numero} donné !", ephemeral=True)

@bot.tree.command(name="farm", description="Ajouter des points de farm")
@app_commands.describe(quantite="La quantité farmée")
async def farm(interaction: discord.Interaction, quantite: int):

    guild = bot.get_guild(1474559198544138391)
    role_tabac = guild.get_role(1474565904011497522)

    if role_tabac not in interaction.user.roles:
        await interaction.response.send_message("❌ Tu n'as pas le rôle Tabac !", ephemeral=True)
        return

    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        data[user_id] = 0

    data[user_id] += quantite
    save_data(data)

    total = data[user_id]

    rapport_channel = None
    import unicodedata
    pseudo = interaction.user.display_name.lower()
    pseudo = unicodedata.normalize('NFKD', pseudo)
    pseudo = ''.join(c for c in pseudo if unicodedata.category(c) != 'Mn')
    pseudo = pseudo.replace(' ', '-').replace('.', '')
    pseudo = ''.join(c if c.isalnum() or c == '-' else '' for c in pseudo)
    for channel in guild.text_channels:
        if channel.name == f"rapport-{pseudo}":
            rapport_channel = channel
            break

    if not rapport_channel:
        await interaction.response.send_message("❌ Ton salon rapport est introuvable !", ephemeral=True)
        return

    await rapport_channel.send(
        f"# Cota\n"
        f"* {total}/4000"
    )

    await interaction.response.send_message(f"✅ {quantite} ajouté ! Total : {total}/4000", ephemeral=True)
@bot.tree.command(name="reset", description="Réinitialiser le cota d'un membre")
@app_commands.describe(membre="Le membre à réinitialiser")
async def reset(interaction: discord.Interaction, membre: discord.Member):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    data = load_data()
    user_id = str(membre.id)

    if user_id in data:
        data[user_id] = 0
        save_data(data)

    await interaction.response.send_message(f"✅ Le cota de {membre.mention} a été réinitialisé !", ephemeral=True)
bot.run(os.getenv("TOKEN"))
