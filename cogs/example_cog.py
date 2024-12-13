import discord
from discord.ext import commands
from discord import app_commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Example cog loaded")

    @app_commands.command(name="ping", description="Replies with 'Pong!'")
    async def ping(self,interaction: discord.Interaction):
        """Responds with a greeting"""
        await interaction.response.send_message("Pong!")

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
