import discord
from discord.ext import commands
from discord import app_commands
from binance import AsyncClient
import pandas as pd
import logging
import bot.cogs.const as const
import mplfinance as mpf
import matplotlib
from io import BytesIO

matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib 

logger = logging.getLogger(__name__)

class AnalyticBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("AnalyticBot loaded")

    async def _fetch_and_plot_klines(self, interaction: discord.Interaction, symbol: str, interval: str, limit: int, is_futures: bool):
        client = await AsyncClient.create()
        buffer = BytesIO()

        try:
            # Fetch Kline data
            if is_futures:
                klines = await client.futures_klines(symbol=symbol, interval=interval, limit=limit)
            else:
                klines = await client.get_klines(symbol=symbol, interval=interval, limit=limit)

            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df = df[["open", "high", "low", "close", "volume"]].astype(float)

            # Plot Kline chart
            mpf.plot(
                df,
                type="candle",
                style="charles",
                title=f"{symbol} {interval} Klines",
                ylabel="Price",
                volume=True,
                savefig=buffer,
                figratio=(4, 3)
            )
            buffer.seek(0)
            await interaction.response.send_message(
                content=f"Kline chart for {symbol} ({interval}):",
                file=discord.File(fp=buffer, filename="kline.png")
            )
        except Exception as e:
            logger.error(f"Error fetching or plotting klines: {e}")
            await interaction.response.send_message(
                content=f"Error fetching or plotting klines: {e}",
                ephemeral=True
            )
        finally:
            await client.close_connection()
            buffer.close()

    @app_commands.command(name="kline", description="Get spot klines data")
    @app_commands.choices(symbol=const.SPOT_CHOICES, interval=const.INTERVAL_CHOICES)
    async def kline(self, interaction: discord.Interaction, symbol: app_commands.Choice[str], interval: app_commands.Choice[str], limit: int = 100):
        await self._fetch_and_plot_klines(interaction, symbol.value, interval.value, limit, is_futures=False)

    @app_commands.command(name="fkline", description="Get futures klines data")
    @app_commands.choices(symbol=const.SPOT_CHOICES, interval=const.INTERVAL_CHOICES)
    async def fkline(self, interaction: discord.Interaction, symbol: app_commands.Choice[str], interval: app_commands.Choice[str], limit: int = 100):
        await self._fetch_and_plot_klines(interaction, symbol.value, interval.value, limit, is_futures=True)

    