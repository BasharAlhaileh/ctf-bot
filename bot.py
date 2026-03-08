import discord
import os

TOKEN = os.environ.get("TOKEN")
VAULT_ROLE_NAME = "Vault Access"
SEEKER_ROLE_NAME = "Seeker"
VAULT_CHANNEL_NAME = "the-vault"
GENERAL_CHANNEL = "general"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Track each user's current step
user_steps = {}

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

# ---- AUTO ASSIGN SEEKER ROLE ON JOIN ----
@client.event
async def on_member_join(member):
    guild = member.guild
    seeker_role = discord.utils.get(guild.roles, name=SEEKER_ROLE_NAME)
    if seeker_role:
        await member.add_roles(seeker_role)
        print(f"✅ Gave Seeker role to {member.name}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    content = message.content.strip().lower()
    channel = message.channel.name

    # ---- STEP 1: Say hello in #general ----
    if channel == GENERAL_CHANNEL and content == "hello":
        step = user_steps.get(user_id, 0)
        if step == 0:
            user_steps[user_id] = 1
            await message.reply(
                "👁️ *I see you.*\n\n"
                "I have cities, but no houses live there.\n"
                "I have mountains, but no trees grow there.\n"
                "I have water, but no fish swim there.\n\n"
                "Speak my name."
            )
        return

    # ---- Red herrings ----
    if any(word in content for word in ["flag", "give flag", "!flag", "gimme", "password"]):
        await message.reply("lmao no")
        return

    if content == "hi":
        await message.reply("close, but not quite 🤔")
        return

    # ---- STEP 2: Answer the riddle ----
    if user_steps.get(user_id) == 1 and content == "map":
        user_steps[user_id] = 2

        guild = message.guild
        role = discord.utils.get(guild.roles, name=VAULT_ROLE_NAME)
        await message.author.add_roles(role)

        vault = discord.utils.get(guild.text_channels, name=VAULT_CHANNEL_NAME)
        await message.reply(
            "✅ *Correct.*\n\nSomething has been unlocked. Check your channels."
        )
        await vault.send(
            f"{message.author.mention} you made it.\n\n"
            "You've come a long way. Now say the magic words."
        )
        return

    # ---- STEP 3: Magic words in #the-vault ----
    if channel == VAULT_CHANNEL_NAME and user_steps.get(user_id) == 2:
        if content == "please and thank you":
            user_steps[user_id] = 3
            await message.reply(
                "🏁 **Well done.**\n\n"
                "||`CTF{p0lit3n3ss_1s_th3_k3y}`||"
            )
        else:
            await message.reply("*not quite...*")
        return

client.run(TOKEN)