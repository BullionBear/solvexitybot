import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "$", intents = intents)

allowed_channels = [1297170481031548931, 1297380883178852484]  # Replace these with your channel IDs

# Check function to restrict commands to specific channels
def is_in_allowed_channel():
    async def predicate(ctx):
        return ctx.channel.id in allowed_channels
    return commands.check(predicate)


@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"load id --> {bot.user}")
    print(f"load {len(slash)} commands")


@bot.hybrid_command()
@is_in_allowed_channel()  # Apply the check to the command
async def hello(ctx):
    """Responds with a greeting"""
    await ctx.send("Hello!")


bot.run(TOKEN)