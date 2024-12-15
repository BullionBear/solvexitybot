import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Example cog loaded")

    @app_commands.command(name="ping", description="Replies with 'Pong!'")
    async def ping(self,interaction: discord.Interaction):
        """Responds with a greeting"""
        await interaction.response.send_message("Pong!")

