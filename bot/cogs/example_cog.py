import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

async def color_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplete handler for the 'color' parameter"""
    colors = ["green", "red", "blue"]
    return [
        app_commands.Choice(name=color, value=color)
        for color in colors if current.lower() in color.lower()
    ]

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

    @app_commands.command(name="select", description="Select an option")
    @app_commands.choices(
        option=[
            discord.app_commands.Choice(name="Option 1", value="option_1"),
            discord.app_commands.Choice(name="Option 2", value="option_2"),
            discord.app_commands.Choice(name="Option 3", value="option_3"),
        ]
    )
    async def select(self, interaction: discord.Interaction, option: discord.app_commands.Choice[str]):
        """Select an option from a dropdown"""
        await interaction.response.send_message(f"You selected: {option.name}")

    

    @app_commands.command(name="auto", description="Autocomplete a command")
    @app_commands.autocomplete(color=color_autocomplete)
    async def auto(self, interaction: discord.Interaction, color: str):
        """Autocomplete a command"""
        await interaction.response.send_message(f"You input: {color}")


