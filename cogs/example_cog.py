from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Responds with 'Pong!'"""
        await ctx.send("Pong!")

# Setup function to add this cog to the bot
def setup(bot):
    bot.add_cog(ExampleCog(bot))
