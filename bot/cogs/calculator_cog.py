import discord
from discord.ext import commands
from discord import app_commands
from binance import AsyncClient
import pandas as pd
import logging
import bot.cogs.const as const


logger = logging.getLogger(__name__)

class AnalyticBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("AnalyticBot loaded")

#     @app_commands.command(name="calcorder", description="Calculate order details")
#     @app_commands.choices(
#         side=const.SIDE_CHOICES,
#         instrument_type=const.INSTRUMENT_TYPE_CHOICES,
#         symbol=const.SYMBOL_CHOICES,
#     )
#     async def calcorder(self, interaction: discord.Interaction, 
#                         symbol: app_commands.Choice[str], 
#                         side: app_commands.Choice[str], 
#                         instrument_type: app_commands.Choice[str], 
#                         support_px: str, resistance_px: str, stop_loss: str):
#         """Calculate order details"""
#         px = float(support_px)
#         stop_loss = float(stop_loss)
#         resistance_px = float(resistance_px)
#         if side.value == "BUY":
#             
#         elif side.value == "SELL":
# 
#         else:
