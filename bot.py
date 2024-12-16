import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import cogs
from sqlalchemy import create_engine

import cogs.trading_cog

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure intents and bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="|>", intents=intents)

# Load extensions
async def load():
    await bot.add_cog(cogs.ExampleCog(bot))
    engine = create_engine(DB_URL)
    await bot.add_cog(cogs.SolvexityDataCog(bot, engine))
    await bot.add_cog(cogs.TradingCog(bot, engine))


@bot.event
async def on_ready():  
    logger.info(f"Bot is online as {bot.user}")

@bot.command(name="sync", description="Sync commands")
async def sync(ctx):
    try:
        slash = await bot.tree.sync()
        logger.info(f"Synced {len(slash)} commands: {slash}")
        await ctx.send("Commands synced successfully.")
    except Exception as e:
        logger.error("Error syncing commands", exc_info=True)
        await ctx.send("Failed to sync commands. Check logs for details.")

@bot.tree.command(name="greet", description="Friendly greeting")
async def greet(interaction: discord.Interaction):
    """Responds with a greeting"""
    try:
        await interaction.response.send_message(f"Hello, {interaction.user}!")
        logger.info(f"Responded to /greet from {interaction.user}")
    except Exception as e:
        logger.error("Error handling /hello command", exc_info=True)


async def main():
    try:
        await load()
        await bot.start(BOT_TOKEN)
    except Exception as e:
        logger.critical("Error starting the bot", exc_info=True)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
