import discord
from discord.ext import commands
from discord import app_commands
import logging
from binance import AsyncClient
from decimal import Decimal
import textwrap
import bot.cogs.const as const

logger = logging.getLogger(__name__)

class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts = const.CONFIG['accounts']

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"TradingCog loaded")

    @app_commands.command(name="buy", description="Buy a token/Long a position")
    @app_commands.choices(symbol=const.SPOT_CHOICES)
    @app_commands.default_permissions(administrator=True)
    async def buy(self, interaction: discord.Interaction, account: str, symbol: app_commands.Choice[str], quantity: str):
        """Buy a token/Long a position on Binance"""
        try:
            if account not in [acc['name'] for acc in self.accounts]:
                await interaction.response.send_message(f"Account {account} not found")
                return
            account = [acc for acc in self.accounts if acc['name'] == account][0]
            account_name = account['name']
            api_key = account['api_key']
            api_secret = account['api_secret']
            client = await AsyncClient.create(api_key, api_secret)
            res = await client.order_market_buy(symbol=symbol, quantity=quantity)
            logger.info(f"Order result {res}")
            description = textwrap.dedent(f"""\
                ID: {res['orderId']}
                Symbol: {res['symbol']}
                Side: {res['side']}
                Qty: {res['executedQty']}
                Average Price: {Decimal(res['cummulativeQuoteQty']) / Decimal(res['executedQty'])}
            """)
            embed = discord.Embed(
                title=f"SPOT {account_name} Buy",
                description=description,
                color=discord.Color.green()
            )
            await interaction.response.send_message(content=None, embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            if 'client' in locals():
                await client.close_connection()
    
    @app_commands.command(name="long", description="Long a position")
    @app_commands.default_permissions(administrator=True)
    async def long(self, interaction: discord.Interaction, account: str, symbol: str, quantity: str):
        """Long a position on Binance"""
        try:
            if account not in [acc['name'] for acc in self.accounts]:
                await interaction.response.send_message(f"Account {account} not found")
                return
            account = [acc for acc in self.accounts if acc['name'] == account][0]
            account_name = account['name']
            api_key = account['api_key']
            api_secret = account['api_secret']
            client = await AsyncClient.create(api_key, api_secret)
            order = await client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantity)
            order_id = order['orderId']
            res = await client.futures_get_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order result {res}")
            description = textwrap.dedent(f"""\
                ID: {order_id}
                Symbol: {res['symbol']}
                Side: {res['side']}
                Qty: {res['executedQty']}
                Average Price: {Decimal(res['avgPrice'])}
            """)
            embed = discord.Embed(
                title=f"PERP {account_name} Long",
                description=description,
                color=discord.Color.green()
            )
            await interaction.response.send_message(content=None, embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
             # if client exists, close the connection
            if 'client' in locals():
                await client.close_connection()

    @app_commands.command(name="sell", description="Sell a token")
    @app_commands.default_permissions(administrator=True)
    async def sell(self, interaction: discord.Interaction, account: str, symbol: str, quantity: str):
        """Sell a token on Binance"""
        try:
            if account not in [acc['name'] for acc in self.accounts]:
                await interaction.response.send_message(f"Account {account} not found")
                return
            account = [acc for acc in self.accounts if acc['name'] == account][0]
            account_name = account['name']
            api_key = account['api_key']
            api_secret = account['api_secret']
            client = await AsyncClient.create(api_key, api_secret)
            res = await client.order_market_sell(symbol=symbol, quantity=quantity)
            logger.info(f"Order result {res}")
            average_price = str(Decimal(res['cummulativeQuoteQty']) / Decimal(res['executedQty'])).rstrip('0').rstrip('.')
            description = textwrap.dedent(f"""\
                ID: {res['orderId']}
                Symbol: {res['symbol']}
                Side: {res['side']}
                Qty: {res['executedQty']}
                Average Price: {average_price}
            """)
            embed = discord.Embed(
                title=f"SPOT {account_name} Sell",
                description=description,
                color=discord.Color.green()
            )
            await interaction.response.send_message(content=None, embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            if 'client' in locals():
                await client.close_connection()

    @app_commands.command(name="short", description="Short a position")
    @app_commands.default_permissions(administrator=True)
    async def short(self, interaction: discord.Interaction, account: str, symbol: str, quantity: str):
        """Short a position on Binance Futures"""
        try:
            if account not in [acc['name'] for acc in self.accounts]:
                await interaction.response.send_message(f"Account {account} not found")
                return
            account = [acc for acc in self.accounts if acc['name'] == account][0]
            account_name = account['name']
            api_key = account['api_key']
            api_secret = account['api_secret']
            client = await AsyncClient.create(api_key, api_secret)
            order = await client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
            order_id = order['orderId']
            res = await client.futures_get_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order result {res}")
            average_price = str(Decimal(res['avgPrice'])).rstrip('0').rstrip('.')
            description = textwrap.dedent(f"""\
                ID: {order_id}
                Symbol: {res['symbol']}
                Side: {res['side']}
                Qty: {res['executedQty']}
                Average Price: {average_price}
            """)
            embed = discord.Embed(
                title=f"PERP {account_name} Short",
                description=description,
                color=discord.Color.green()
            )
            await interaction.response.send_message(content=None, embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            if 'client' in locals():
                await client.close_connection()