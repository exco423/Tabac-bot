import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import re
import unicodedata
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = 1474559198544138391
CATEGORY_RAPPORT_ID = 1474807318997897487
ROLE_TABAC_ID = 1474565904011497522
ROLE_VENDEUR_ID = 1474562293198098717
ROLE_CITOYENS_ID = 1474571994094637157
ROLE_AVERT_1_ID = 1482872715525492807
ROLE_AVERT_2_ID = 1482872877513445396
SALON_SANCTIONS_ID = 1474570131312218313
CLASSEMENT_CHANNEL_ID = 1495810308780982384

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
CLASSEMENT_MESSAGE_FILE = os.path.join(BASE_DIR, "classement_message.json")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_classement_message():
    try:
        with open(CLASSEMENT_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_classement_message(data):
    with open(CLASSEMENT_MESSAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def normalize_text(text: str) -> str:
    text = text.casefold().strip()
    text = unicodedata.normalize("NFKD", text)

    replacements = {
        "\u0131": "i",
        "\u0130": "i",
        "\u00f8": "o",
        "\u0153": "oe",
        "\u00e6": "ae",
        "\u00df": "ss",
    }

    text = "".join(replacements.get(c, c) for c in text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_classement_embed(guild: discord.Guild):
    data = load_data()
    classement_data = [(user_id, points) for user_id, points in data.items() if points > 0]
    classement_data.sort(key=lambda x: x[1], reverse=True)
    classement_data = classement_data[:10]

    if not classement_data:
        description = "Aucun classement disponible pour le moment."
    else:
        lignes = []
        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, points) in enumerate(classement_data, start=1):
            membre = guild.get_member(int(user_id))
            nom = membre.display_name if membre else f"Utilisateur inconnu ({user_id})"

            if index <= 3:
                lignes.append(f"{medals[index - 1]} {nom} - `{points}/4000`")
            else:
                lignes.append(f"**{index}.** {nom} - `{points}/4000`")

        description = "\n".join(lignes)

    embed = discord.Embed(
        title="🏆 Classement Farm",
        description=description,
        color=discord.Color.gold()
    )
    embed.set_footer(text="Top des employés du Tabac")
    return embed


async def update_classement_message(guild: discord.Guild):
    saved = load_classement_message()
    channel_id = saved.get("channel_id")
    message_id = saved.get("message_id")

    if not channel_id or not message_id:
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        return

    try:
        message = await channel.fetch_message(message_id)
        embed = build_classement_embed(guild)
        await message.edit(embed=embed)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return


@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"{len(synced)} commande(s) synchronisée(s) sur le serveur.")
    except Exception as e:
        print(f"Erreur sync : {e}")

    print(f"Bot connecté : {bot.user}")


@bot.tree.command(name="recrute", description="Recruter un membre dans le Tabac")
@app_commands.describe(membre="Le membre à recruter", ticket="Le ticket de la personne")
async def recrute(interaction: discord.Interaction, membre: discord.Member, ticket: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    categorie = guild.get_channel(CATEGORY_RAPPORT_ID)
    role_tabac = guild.get_role(ROLE_TABAC_ID)
    role_vendeur = guild.get_role(ROLE_VENDEUR_ID)

    if not categorie or not role_tabac or not role_vendeur:
        await interaction.followup.send("❌ Catégorie ou rôles introuvables !", ephemeral=True)
        return

    await membre.add_roles(role_tabac, role_vendeur)
    await ticket.edit(name=f"rapport-{normalize_text(membre.display_name)}", category=categorie)

    await interaction.followup.send("✅ Les rôles de Tabac ont bien été attribués !", ephemeral=True)

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

    guild = interaction.guild
    role_tabac = guild.get_role(ROLE_TABAC_ID)
    role_vendeur = guild.get_role(ROLE_VENDEUR_ID)
    role_citoyens = guild.get_role(ROLE_CITOYENS_ID)
    salon = guild.get_channel(SALON_SANCTIONS_ID)

    manquants = []

    if role_tabac is None:
        manquants.append(f"- Rôle Tabac : `{ROLE_TABAC_ID}`")
    if role_vendeur is None:
        manquants.append(f"- Rôle Vendeur : `{ROLE_VENDEUR_ID}`")
    if role_citoyens is None:
        manquants.append(f"- Rôle Citoyens : `{ROLE_CITOYENS_ID}`")
    if salon is None:
        manquants.append(f"- Salon sanctions : `{SALON_SANCTIONS_ID}`")

    if manquants:
        await interaction.response.send_message(
            "❌ Introuvable :\n" + "\n".join(manquants),
            ephemeral=True
        )
        return

    await membre.remove_roles(role_tabac, role_vendeur)
    await membre.add_roles(role_citoyens)

    await salon.send(
        f"# Avertissement :\n"
        f"* Personne : {membre.mention}\n"
        f"* Raison : {raison}\n"
        f"* Sanction : Demote"
    )

    await interaction.response.send_message("✅ Le membre a bien été démote !", ephemeral=True)


@bot.tree.command(name="citoyens", description="Donner le rôle Citoyens à tous les membres du serveur")
async def citoyens(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.followup.send("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    guild = interaction.guild
    if guild is None:
        await interaction.followup.send("❌ Cette commande doit être utilisée dans le serveur.", ephemeral=True)
        return

    role = guild.get_role(ROLE_CITOYENS_ID)

    if role is None:
        await interaction.followup.send(
            f"❌ Rôle introuvable.\nServeur : `{guild.name}` (`{guild.id}`)\nID recherché : `{ROLE_CITOYENS_ID}`",
            ephemeral=True
        )
        return

    ajoutes = 0
    deja = 0
    erreurs = 0

    async for membre in guild.fetch_members(limit=None):
        if membre.bot:
            continue

        if role in membre.roles:
            deja += 1
            continue

        try:
            await membre.add_roles(role, reason=f"Commande /citoyens par {interaction.user}")
            ajoutes += 1
        except (discord.Forbidden, discord.HTTPException):
            erreurs += 1

    await interaction.followup.send(
        f"✅ Terminé !\n"
        f"Ajoutés : **{ajoutes}**\n"
        f"Déjà présents : **{deja}**\n"
        f"Erreurs : **{erreurs}**",
        ephemeral=True
    )


@bot.tree.command(name="avert", description="Donner un avertissement à un membre")
@app_commands.describe(
    membre="Le membre à avertir",
    raison="La raison de l'avertissement",
    numero="Le numéro de l'avertissement"
)
@app_commands.choices(numero=[
    app_commands.Choice(name="Avertissement 1", value="1"),
    app_commands.Choice(name="Avertissement 2", value="2"),
])
async def avert(interaction: discord.Interaction, membre: discord.Member, raison: str, numero: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    guild = interaction.guild
    salon = guild.get_channel(SALON_SANCTIONS_ID)

    if numero == "1":
        role_avert = guild.get_role(ROLE_AVERT_1_ID)
    else:
        role_avert = guild.get_role(ROLE_AVERT_2_ID)

    if not role_avert or not salon:
        await interaction.response.send_message("❌ Rôle ou salon introuvable !", ephemeral=True)
        return

    await membre.add_roles(role_avert)

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
    guild = interaction.guild
    role_tabac = guild.get_role(ROLE_TABAC_ID)

    if not role_tabac:
        await interaction.response.send_message("❌ Le rôle Tabac est introuvable !", ephemeral=True)
        return

    if role_tabac not in interaction.user.roles:
        await interaction.response.send_message("❌ Tu n'as pas le rôle Tabac !", ephemeral=True)
        return

    if quantite <= 0:
        await interaction.response.send_message("❌ La quantité doit être supérieure à 0 !", ephemeral=True)
        return

    pseudo_normalized = normalize_text(interaction.user.display_name)
    expected_channel_name = f"rapport-{pseudo_normalized}"

    rapport_channel = None
    for channel in guild.text_channels:
        if normalize_text(channel.name) == expected_channel_name:
            rapport_channel = channel
            break

    if not rapport_channel:
        await interaction.response.send_message(
            f"❌ Ton salon rapport est introuvable ! Nom recherché : `{expected_channel_name}`",
            ephemeral=True
        )
        return

    if interaction.channel.id != rapport_channel.id:
        await interaction.response.send_message(
            f"❌ Tu dois faire la commande dans ton salon : {rapport_channel.mention}",
            ephemeral=True
        )
        return

    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        data[user_id] = 0

    data[user_id] += quantite
    total = data[user_id]

    save_data(data)
    await update_classement_message(guild)

    await rapport_channel.send(
        f"# Cota\n"
        f"* {total}/4000"
    )

    await interaction.response.send_message(
        f"✅ {quantite} ajouté ! Total : {total}/4000",
        ephemeral=True
    )


@bot.tree.command(name="classement", description="Créer ou mettre à jour le classement du farm")
async def classement(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    channel = guild.get_channel(CLASSEMENT_CHANNEL_ID)

    if not channel:
        await interaction.followup.send("❌ Le salon classement est introuvable.", ephemeral=True)
        return

    embed = build_classement_embed(guild)
    saved = load_classement_message()
    message_id = saved.get("message_id")

    if saved.get("channel_id") == CLASSEMENT_CHANNEL_ID and message_id:
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            await interaction.followup.send("✅ Le classement a été mis à jour.", ephemeral=True)
            return
        except discord.NotFound:
            pass
        except discord.HTTPException:
            pass

    message = await channel.send(embed=embed)
    save_classement_message({
        "channel_id": channel.id,
        "message_id": message.id
    })

    await interaction.followup.send("✅ Le classement automatique a été créé.", ephemeral=True)


@bot.tree.command(name="reset", description="Réinitialiser le cota d'un membre")
@app_commands.describe(membre="Le membre à réinitialiser")
async def reset(interaction: discord.Interaction, membre: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        return

    data = load_data()
    user_id = str(membre.id)

    data[user_id] = 0
    save_data(data)
    await update_classement_message(interaction.guild)

    await interaction.response.send_message(
        f"✅ Le cota de {membre.mention} a été réinitialisé à 0 !",
        ephemeral=True
    )


bot.run(os.getenv("TOKEN"))
