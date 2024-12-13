import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="|>", intents=intents)
"""
allowed_channels = [1297170481031548931, 1297380883178852484]  # Replace these with your channel IDs

# Check function to restrict commands to specific channels
def is_in_allowed_channel():
    async def predicate(ctx):
        return ctx.channel.id in allowed_channels
    return commands.check(predicate)
"""

async def load():
    await bot.load_extension(f'cogs.example_cog')


@bot.event
async def on_ready():  
    print(f"load id --> {bot.user}")

@bot.command(name = "sync", description = "sync commands")
async def sync(ctx):
    slash = await bot.tree.sync()
    print(f"load {len(slash)} commands")
    print(f"{slash}")
    await ctx.send("synced")




@bot.tree.command(name = "hello", description = "Hello, world!")
async def hello(interaction: discord.Interaction):
    """Responds with a greeting"""
    await interaction.response.send_message("Hello, world!")

@bot.tree.command(name = "test", description = "Test, world!")
async def test(interaction: discord.Interaction):
    """Responds with a greeting"""
    await interaction.response.send_message("Test, world!")


async def main():
    await load()
    await bot.start(TOKEN)

asyncio.run(main())