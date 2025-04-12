
from discord import app_commands
from bot.config import CONFIG

SPOT_CHOICES = [
    app_commands.Choice(name=spot['symbol'], value=spot['symbol'])
    for spot in CONFIG['symbols']['spot']
]