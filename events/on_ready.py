from discord.ext import commands

class OnReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Event triggered when the bot has connected"""
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        print("------")

# Setup function to add this event handler to the bot
def setup(bot):
    bot.add_cog(OnReadyEvent(bot))
