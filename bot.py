import discord
import asyncio
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

user_steps = {}

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")

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
            await message.delete()
            reply = await message.channel.send(
                f"{message.author.mention}\n"
                "👁️ *I see you.*\n\n"
                "I have cities, but no houses live there.\n"
                "I have mountains, but no trees grow there.\n"
                "I have water, but no fish swim there.\n\n"
                "Speak my name."
            )
            await asyncio.sleep(30)
            await reply.delete()
        return

    # ---- Red herrings ----
    if any(word in content for word in ["flag", "give flag", "!flag", "gimme", "password"]):
        await message.delete()
        reply = await message.channel.send(f"{message.author.mention} lmao no")
        await asyncio.sleep(5)
        await reply.delete()
        return

    if content == "hi":
        await message.delete()
        reply = await message.channel.send(f"{message.author.mention} close, but not quite 🤔")
        await asyncio.sleep(5)
        await reply.delete()
        return

    # ---- STEP 2: Answer the riddle ----
    if user_steps.get(user_id) == 1 and content == "map":
        user_steps[user_id] = 2
        await message.delete()

        guild = message.guild
        role = discord.utils.get(guild.roles, name=VAULT_ROLE_NAME)
        await message.author.add_roles(role)

        vault = discord.utils.get(guild.text_channels, name=VAULT_CHANNEL_NAME)
        reply = await message.channel.send(
            f"{message.author.mention} ✅ *Correct.* Something has been unlocked. Check your channels."
        )
        await vault.send(
            f"{message.author.mention} you made it.\n\n"
            "You've come a long way. Now say the magic words."
        )
        await asyncio.sleep(5)
        await reply.delete()
        return

    # ---- STEP 3: Magic words in #the-vault ----
    if channel == VAULT_CHANNEL_NAME and user_steps.get(user_id) == 2:
        if content == "please and thank you":
            user_steps[user_id] = 3
            await message.delete()
            await message.author.send(
                "🏁 **Well done.**\n\n"
                "Here is your flag:\n"
                "`CTF{p0lit3n3ss_1s_th3_k3y}`"
            )
            reply = await message.channel.send(
                f"{message.author.mention} 🏁 **Well done.** Check your DMs!"
            )
            await asyncio.sleep(5)
            await reply.delete()
        else:
            await message.delete()
            reply = await message.channel.send(f"{message.author.mention} *not quite...*")
            await asyncio.sleep(5)
            await reply.delete()
        return

client.run(TOKEN)
