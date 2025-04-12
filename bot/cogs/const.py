
from discord import app_commands
from bot.config import CONFIG

ACCOUNT_CHOICES = [
    app_commands.Choice(name=account['name'], value=account['name'])
    for account in CONFIG['accounts']
]

SPOT_CHOICES = [
    app_commands.Choice(name=spot['symbol'], value=spot['symbol'])
    for spot in CONFIG['symbols']['spot']
]

PERP_CHOICES = [
    app_commands.Choice(name=perp['symbol'], value=perp['symbol'])
    for perp in CONFIG['symbols']['perp']
]