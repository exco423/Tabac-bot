import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import json
import re
import unicodedata

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
ROLE_TABAC_ID = 1474565904011497522
ROLE_VENDEUR_ID = 1474562293198098717
ROLE_CITOYENS_ID = 1474571994094637157
ROLE_CITOYENS_ALL_ID = 1499759422954799204
ROLE_AVERT_1_ID = 1482872715525492807
ROLE_AVERT_2_ID = 1482872877513445396
SALON_SANCTIONS_ID = 1474570131312218313
CLASSEMENT_CHANNEL_ID = 1495810308780982384
CLASSEMENT_MESSAGE_FILE = "classement_message.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
CLASSEMENT_MESSAGE_FILE = os.path.join(BASE_DIR, "classement_message.json")

intents = discord.Intents.default()
intents.members = True


def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_classement_message():
    try:
        with open(CLASSEMENT_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        with open(CLASSEMENT_MESSAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_classement_message(data):
    with open(CLASSEMENT_MESSAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    with open(CLASSEMENT_MESSAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def normalize_text(text: str) -> str:
        "ß": "ss",
    }

    text = "".join(replacements.get(c, c) for c in text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = "".join(replacements.get(char, char) for char in text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def build_classement_embed(guild: discord.Guild):
    data = load_data()
    classement_data = [(user_id, points) for user_id, points in data.items() if points > 0]
    classement_data.sort(key=lambda x: x[1], reverse=True)
    classement_data.sort(key=lambda item: item[1], reverse=True)
    classement_data = classement_data[:10]

    if not classement_data:
        description = "\n".join(lignes)

    embed = discord.Embed(
        title="🏆 Classement Farm",
        title="Classement Farm",
        description=description,
        color=discord.Color.gold()
        color=discord.Color.gold(),
    )
    embed.set_footer(text="Top des employés du Tabac")
    embed.set_footer(text="Top des employes du Tabac")
    return embed


        return

    channel = guild.get_channel(channel_id)
    if not channel:
    if channel is None:
        return

    try:
        message = await channel.fetch_message(message_id)
        embed = build_classement_embed(guild)
        await message.edit(embed=embed)
        await message.edit(embed=build_classement_embed(guild))
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"{len(synced)} commande(s) synchronisée(s) sur le serveur.")
    except Exception as e:
        print(f"Erreur sync : {e}")
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"{len(synced)} commande(s) synchronisee(s) sur le serveur.")
    except Exception as error:
        print(f"Erreur sync : {error}")

    print(f"Bot connecté : {bot.user}")
    print(f"Bot connecte : {bot.user}")


@bot.tree.command(name="recrute", description="Recruter un membre dans le Tabac")
@app_commands.describe(membre="Le membre à recruter", ticket="Le ticket de la personne")
@app_commands.describe(membre="Le membre a recruter", ticket="Le ticket de la personne")
async def recrute(interaction: discord.Interaction, membre: discord.Member, ticket: discord.TextChannel):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    categorie = guild.get_channel(CATEGORY_RAPPORT_ID)
    role_tabac = guild.get_role(ROLE_TABAC_ID)
    role_vendeur = guild.get_role(ROLE_VENDEUR_ID)

    if not categorie or not role_tabac or not role_vendeur:
        await interaction.response.send_message("❌ Catégorie ou rôles introuvables !", ephemeral=True)
    if categorie is None or role_tabac is None or role_vendeur is None:
        await interaction.followup.send("Categorie ou roles introuvables.", ephemeral=True)
        return

    await membre.add_roles(role_tabac, role_vendeur)
    await ticket.edit(name=f"rapport-{normalize_text(membre.display_name)}", category=categorie)

    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("✅ Les rôles de Tabac ont bien été attribués !", ephemeral=True)
    await interaction.followup.send("Les roles de Tabac ont bien ete attribues.", ephemeral=True)

    await interaction.channel.send(
        f"Bien joué {membre.mention}, tu as été recruté dans le Tabac ! 🚬\n"
        f"Maintenant je te laisse aller voir tout ça :\n"
        f"Bien joue {membre.mention}, tu as ete recrute dans le Tabac.\n"
        f"Maintenant je te laisse aller voir tout ca :\n"
        f"<#1474569375901155448>\n"
        f"<#1495452484418801714>\n"
        f"<#1482797251280638164>\n"
    )


@bot.tree.command(name="demote", description="Retirer les rôles Tabac d'un membre")
@app_commands.describe(membre="Le membre à démoter", raison="La raison du demote")
@bot.tree.command(name="demote", description="Retirer les roles Tabac d'un membre")
@app_commands.describe(membre="Le membre a demoter", raison="La raison du demote")
async def demote(interaction: discord.Interaction, membre: discord.Member, raison: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    guild = interaction.guild
    role_citoyens = guild.get_role(ROLE_CITOYENS_ID)
    salon = guild.get_channel(SALON_SANCTIONS_ID)

    if not role_tabac or not role_vendeur or not role_citoyens or not salon:
        await interaction.response.send_message("❌ Rôles ou salon introuvables !", ephemeral=True)
    manquants = []
    if role_tabac is None:
        manquants.append(f"- Role Tabac : `{ROLE_TABAC_ID}`")
    if role_vendeur is None:
        manquants.append(f"- Role Vendeur : `{ROLE_VENDEUR_ID}`")
    if role_citoyens is None:
        manquants.append(f"- Role Citoyens : `{ROLE_CITOYENS_ID}`")
    if salon is None:
        manquants.append(f"- Salon sanctions : `{SALON_SANCTIONS_ID}`")

    if manquants:
        await interaction.response.send_message("Introuvable :\n" + "\n".join(manquants), ephemeral=True)
        return

    await membre.remove_roles(role_tabac, role_vendeur)
        f"* Sanction : Demote"
    )

    await interaction.response.send_message("✅ Le membre a bien été démote !", ephemeral=True)
    await interaction.response.send_message("Le membre a bien ete demote.", ephemeral=True)


@bot.tree.command(name="citoyens", description="Donner le rôle Citoyens à tous les membres du serveur")
@bot.tree.command(name="citoyens", description="Donner le role Citoyens a tous les membres du serveur")
async def citoyens(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.followup.send("❌ Tu n'as pas la permission !", ephemeral=True)
        await interaction.followup.send("Tu n'as pas la permission.", ephemeral=True)
        return

    guild = interaction.guild
    role_citoyens = guild.get_role(ROLE_CITOYENS_ALL_ID)
    if guild is None:
        await interaction.followup.send("Cette commande doit etre utilisee dans le serveur.", ephemeral=True)
        return

    if not role_citoyens:
        await interaction.followup.send("❌ Le rôle Citoyens est introuvable !", ephemeral=True)
    role = guild.get_role(ROLE_CITOYENS_ID)
    if role is None:
        await interaction.followup.send(
            f"Role introuvable.\nServeur : `{guild.name}` (`{guild.id}`)\nID recherche : `{ROLE_CITOYENS_ID}`",
            ephemeral=True,
        )
        return

    ajoutes = 0
    deja = 0
    erreurs = 0

    for membre in guild.members:
        if role_citoyens in membre.roles:
    async for membre in guild.fetch_members(limit=None):
        if membre.bot:
            continue

        if role in membre.roles:
            deja += 1
            continue

        try:
            await membre.add_roles(role_citoyens, reason=f"Commande /citoyens par {interaction.user}")
            await membre.add_roles(role, reason=f"Commande /citoyens par {interaction.user}")
            ajoutes += 1
        except (discord.Forbidden, discord.HTTPException):
            erreurs += 1

    await interaction.followup.send(
        f"✅ Terminé !\n"
        f"Rôle ajouté à **{ajoutes}** membre(s).\n"
        f"Déjà présent sur **{deja}** membre(s).\n"
        f"Erreur sur **{erreurs}** membre(s).",
        ephemeral=True
        f"Termine.\n"
        f"Ajoutes : **{ajoutes}**\n"
        f"Deja presents : **{deja}**\n"
        f"Erreurs : **{erreurs}**",
        ephemeral=True,
    )


@bot.tree.command(name="avert", description="Donner un avertissement à un membre")
@app_commands.describe(membre="Le membre à avertir", raison="La raison de l'avertissement", numero="Le numéro de l'avertissement")
@app_commands.choices(numero=[
    app_commands.Choice(name="Avertissement 1", value="1"),
    app_commands.Choice(name="Avertissement 2", value="2"),
])
@bot.tree.command(name="avert", description="Donner un avertissement a un membre")
@app_commands.describe(
    membre="Le membre a avertir",
    raison="La raison de l'avertissement",
    numero="Le numero de l'avertissement",
)
@app_commands.choices(
    numero=[
        app_commands.Choice(name="Avertissement 1", value="1"),
        app_commands.Choice(name="Avertissement 2", value="2"),
    ]
)
async def avert(interaction: discord.Interaction, membre: discord.Member, raison: str, numero: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    guild = interaction.guild
    salon = guild.get_channel(SALON_SANCTIONS_ID)
    role_avert = guild.get_role(ROLE_AVERT_1_ID if numero == "1" else ROLE_AVERT_2_ID)

    if numero == "1":
        role_avert = guild.get_role(ROLE_AVERT_1_ID)
    else:
        role_avert = guild.get_role(ROLE_AVERT_2_ID)

    if not role_avert or not salon:
        await interaction.response.send_message("❌ Rôle ou salon introuvable !", ephemeral=True)
    if role_avert is None or salon is None:
        await interaction.response.send_message("Role ou salon introuvable.", ephemeral=True)
        return

    await membre.add_roles(role_avert)
        f"* Sanction : Avertissement {numero}"
    )

    await interaction.response.send_message(f"✅ Avertissement {numero} donné !", ephemeral=True)
    await interaction.response.send_message(f"Avertissement {numero} donne.", ephemeral=True)


@bot.tree.command(name="farm", description="Ajouter des points de farm")
@app_commands.describe(quantite="La quantité farmée")
@app_commands.describe(quantite="La quantite farmee")
async def farm(interaction: discord.Interaction, quantite: int):
    guild = interaction.guild
    role_tabac = guild.get_role(ROLE_TABAC_ID)

    if not role_tabac:
        await interaction.response.send_message("❌ Le rôle Tabac est introuvable !", ephemeral=True)
    if role_tabac is None:
        await interaction.response.send_message("Le role Tabac est introuvable.", ephemeral=True)
        return

    if role_tabac not in interaction.user.roles:
        await interaction.response.send_message("❌ Tu n'as pas le rôle Tabac !", ephemeral=True)
        await interaction.response.send_message("Tu n'as pas le role Tabac.", ephemeral=True)
        return

    if quantite <= 0:
        await interaction.response.send_message("❌ La quantité doit être supérieure à 0 !", ephemeral=True)
        await interaction.response.send_message("La quantite doit etre superieure a 0.", ephemeral=True)
        return

    pseudo_normalized = normalize_text(interaction.user.display_name)
            rapport_channel = channel
            break

    if not rapport_channel:
    if rapport_channel is None:
        await interaction.response.send_message(
            f"❌ Ton salon rapport est introuvable ! Nom recherché : `{expected_channel_name}`",
            ephemeral=True
            f"Ton salon rapport est introuvable. Nom recherche : `{expected_channel_name}`",
            ephemeral=True,
        )
        return

    if interaction.channel.id != rapport_channel.id:
        await interaction.response.send_message(
            f"❌ Tu dois faire la commande dans ton salon : {rapport_channel.mention}",
            ephemeral=True
            f"Tu dois faire la commande dans ton salon : {rapport_channel.mention}",
            ephemeral=True,
        )
        return

    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        data[user_id] = 0
    data[user_id] = data.get(user_id, 0) + quantite
    total = data[user_id]

    data[user_id] += quantite
    save_data(data)
    await update_classement_message(guild)

    total = data[user_id]

    await rapport_channel.send(
        f"# Cota\n"
        f"* {total}/4000"
    )

    await interaction.response.send_message(
        f"✅ {quantite} ajouté ! Total : {total}/4000",
        ephemeral=True
    )
    await rapport_channel.send(f"# Cota\n* {total}/4000")
    await interaction.response.send_message(f"{quantite} ajoute. Total : {total}/4000", ephemeral=True)


@bot.tree.command(name="classement", description="Créer ou mettre à jour le classement du farm")
@bot.tree.command(name="classement", description="Creer ou mettre a jour le classement du farm")
async def classement(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    channel = guild.get_channel(CLASSEMENT_CHANNEL_ID)

    if not channel:
        await interaction.followup.send("❌ Le salon classement est introuvable.", ephemeral=True)
    if channel is None:
        await interaction.followup.send("Le salon classement est introuvable.", ephemeral=True)
        return

    embed = build_classement_embed(guild)
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            await interaction.followup.send("✅ Le classement a été mis à jour.", ephemeral=True)
            await interaction.followup.send("Le classement a ete mis a jour.", ephemeral=True)
            return
        except discord.NotFound:
            pass
        except discord.HTTPException:
        except (discord.NotFound, discord.HTTPException):
            pass

    message = await channel.send(embed=embed)
    save_classement_message({
        "channel_id": channel.id,
        "message_id": message.id
    })

    await interaction.followup.send("✅ Le classement automatique a été créé.", ephemeral=True)
    save_classement_message({"channel_id": channel.id, "message_id": message.id})
    await interaction.followup.send("Le classement automatique a ete cree.", ephemeral=True)


@bot.tree.command(name="reset", description="Réinitialiser le cota d'un membre")
@app_commands.describe(membre="Le membre à réinitialiser")
@bot.tree.command(name="reset", description="Reinitialiser le cota d'un membre")
@app_commands.describe(membre="Le membre a reinitialiser")
async def reset(interaction: discord.Interaction, membre: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Tu n'as pas la permission !", ephemeral=True)
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    data = load_data()
    user_id = str(membre.id)

    data[user_id] = 0
    data[str(membre.id)] = 0
    save_data(data)
    await update_classement_message(interaction.guild)

    await interaction.response.send_message(
        f"✅ Le cota de {membre.mention} a été réinitialisé à 0 !",
        ephemeral=True
    )
    await interaction.response.send_message(f"Le cota de {membre.mention} a ete reinitialise a 0.", ephemeral=True)


bot.run(os.getenv("TOKEN"))
