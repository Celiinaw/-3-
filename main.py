import nextcord
import os
import random
import datetime
import asyncio
from nextcord.ext import commands
from keep_alive import keep_alive
import json

custom_color = 0xd3aad0  # Set the overall custom color here
free_gen_channel = 1192496538535067673  # Channel ID for /fgen
exclusive_gen_channel = 1192496538535067675  # Channel ID for /egen
free_cooldowns = {}

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, help_command=None)

# Load cooldowns from a JSON file
def load_cooldowns():
    try:
        with open("cooldown.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save cooldowns to a JSON file
def save_cooldowns(cooldowns):
    with open("cooldown.json", "w") as file:
        json.dump(cooldowns, file)

# Load cooldowns when the bot starts
free_cooldowns = load_cooldowns()

server_name = "moved to discord.gg/cyYnGWGu"
server_logo = "https://cdn.discordapp.com/icons/1169673653747720292/a_501f0333a093d3836447bcd77a3a37e9.gif"

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=server_name))
    print("Running")

@bot.slash_command(name="egen", description="Exclusive Generate")
async def exclusive_gen(inter, stock: nextcord.ApplicationCommandOptionChoice(choices={
    "Roblox 2023": "Roblox2023.txt",
    "Roblox 2010": "Roblox2010.txt",
    "Roblox Realistic": "RobloxRealistic.txt",
    "Valorant": "Valorant.txt",
    "Steam": "Steam.txt",
    "EpicGames": "EpicGames.txt"
})):
    user = inter.user
    user_id = inter.user.id

    # Set cooldown to 1 minute for the "egen" command
    cooldown_duration = 60

    if user_id in free_cooldowns and "egen" in free_cooldowns[user_id]:
        remaining_cooldown = free_cooldowns[user_id]["egen"]
        embed = nextcord.Embed(
            title="Cooldown",
            description=f"You still have {remaining_cooldown} seconds remaining.",
            color=custom_color
        )
        await inter.send(embed=embed, ephemeral=True)
        return
    if inter.channel.id != exclusive_gen_channel:
        embed = nextcord.Embed(
            title=f"Wrong Channel! Use <#{exclusive_gen_channel}>",
            color=custom_color
        )
        await inter.send(embed=embed, ephemeral=True)
        return

    stock_color = custom_color
    stock_file = stock.lower()
    if not os.path.isfile(f"{stock_file}.txt"):
        embed = nextcord.Embed(
            title="The stock that you are trying to generate does not exist.",
            color=custom_color
        )
        await inter.send(embed=embed, ephemeral=True)
        return

    with open(f"{stock_file}.txt") as file:
        lines = file.read().splitlines()
        if len(lines) == 0:
            embed = nextcord.Embed(
                title="Out of stock!",
                description="Please wait until we restock.",
                color=custom_color
            )
            await inter.send(embed=embed, ephemeral=True)
            return

    account = random.choice(lines)
    combo = account.split(':')
    User = combo[0]
    Pass = combo[1]
    Password = Pass.rstrip()

    try:
        await user.send(embed=nextcord.Embed(
            title=server_name,
            color=stock_color
        ).set_footer(
            text=f"{server_name}",
            icon_url=server_logo
        ).set_thumbnail(
            url=server_logo
        ).add_field(
            name="Username:",
            value=f"```{str(User)}```"
        ).add_field(
            name="Password:",
            value=f"```{str(Password)}```"
        ).add_field(
            name="Combo:",
            value=f"```{str(User)}:{str(Password)}```",
            inline=False
        ))
    except nextcord.errors.Forbidden:
        embed = nextcord.Embed(
            title="DMs Closed!",
            description="I cannot send messages to you. Please make sure your DMs are open.",
            color=0xff0000  # Red color for error
        )
        await inter.send(embed=embed, ephemeral=True)
        return

    name = stock_file.capitalize().replace(".txt", "")

    embed1 = nextcord.Embed(
        title=f" <:emoji_3:1185233432645742592> {name} Account Generated!",
        description="> Check your DMs for your account.",
        color=0x3ba55d  # Green color for success
    )
    embed1.set_footer(text=f"{server_name}", icon_url=server_logo)
    embed1.set_thumbnail(url=server_logo)
    await inter.send(embed=embed1)
    lines.remove(account)
    with open(f"{stock_file}.txt", "w", encoding='utf-8') as file:
        file.write("\n".join(lines))

    # Set cooldown for "egen" command
    free_cooldowns.setdefault(user_id, {})["egen"] = cooldown_duration

    # Save cooldowns to the JSON file
    save_cooldowns(free_cooldowns)

    await asyncio.sleep(1)
    while free_cooldowns[user_id]["egen"] > 0:
        free_cooldowns[user_id]["egen"] -= 1
        await asyncio.sleep(1)

    del free_cooldowns[user_id]["egen"]

@bot.slash_command(name="stock", description="View free stock!")
async def freestock(inter: nextcord.Interaction):   
    embed = nextcord.Embed(title="Account Stock", color=custom_color, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=server_name, icon_url=server_logo)
    embed.set_thumbnail(url=server_logo)
    embed.description = ""
    for filename in os.listdir("freestock/"):
        with open(f"freestock/{filename}") as f: 
            amount = len(f.read().splitlines())
            name = (filename[0].upper() + filename[1:].lower()).replace(".txt","") 
            embed.description += f"* **{name}**: `{amount}`\n"
    await inter.send(embed=embed, ephemeral=True)

@bot.slash_command(name="help", description="Show all available commands!")
async def help(ctx):
    embed = nextcord.Embed(title=server_name, color=custom_color)
    embed.set_footer(text=f"{server_name}", icon_url=server_logo)
    embed.set_thumbnail(url=server_logo)
    embed.add_field(name="/help", value="Shows this command", inline=False)
    embed.add_field(name="/generate", value="Generate free accounts", inline=False)
    embed.add_field(name="/stock", value="View free stock", inline=False)

    await ctx.send(embed=embed)

keep_alive()
bot.run(os.environ["token"])
