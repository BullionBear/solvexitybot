import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from PIL import Image, ImageDraw
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


    @app_commands.command(name="image", description="Send a static image")
    async def image(self, interaction: discord.Interaction):
        """Send a static image created with Pillow"""
        # Create a static image
        img = Image.new("RGB", (400, 200), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle((50, 50, 350, 150), fill=(255, 255, 255), outline=(0, 0, 0))
        draw.text((120, 90), "Static Image", fill=(0, 0, 0))

        # Save the image to a BytesIO object
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Send the image as a Discord file
        await interaction.response.send_message("Here is a static image!", file=discord.File(fp=buffer, filename="static_image.png"))


