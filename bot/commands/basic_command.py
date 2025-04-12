from discord.ext import commands

class BasicCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx):
        """Responds with a greeting"""
        await ctx.send(f"Hello, {ctx.author}!")

# Setup function to add this command to the bot
def setup(bot):
    bot.add_cog(BasicCommand(bot))
