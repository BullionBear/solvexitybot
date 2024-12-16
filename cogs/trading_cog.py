import discord
from discord.ext import commands
from discord import app_commands
import pandas as pd
from sqlalchemy.engine import Engine
from binance import AsyncClient
from decimal import Decimal
import textwrap
import logging

logger = logging.getLogger(__name__)
 
class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, engine: Engine):
        self.bot = bot
        self.engine = engine

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"TradingCog loaded")

    @app_commands.command(name="buy", description="Buy a token/Long a position")
    @app_commands.default_permissions(administrator=True)
    async def buy(self, interaction: discord.Interaction, account: str, symbol: str, quantity: str):
        """Buy a token/Long a position on Binance"""
        try:
            api_key = pd.read_sql_query(f"select * from read_api where account = '{account}' limit 1", self.engine)
            if len(api_key) == 0:
                await interaction.response.send_message(f"Account {account} not found")
                return
            client = await AsyncClient.create(api_key["api_key"].values[0], api_key["api_secret"].values[0])
            if api_key["exchange"].values[0] == 'BINANCE':
                # await interaction.response.send_message(f"Invalid API key")
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
                    title=f"SPOT {account} Buy",
                    description=description,
                    color=discord.Color.green()
                )
                await interaction.response.send_message(content=None, embed=embed)

            elif api_key["exchange"].values[0] == 'BINANCEFUTURE':
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
                    title=f"PERP {account} Buy",
                    description=description,
                    color=discord.Color.green()
                )
                await interaction.response.send_message(content=None, embed=embed)
            else:
                await interaction.response.send_message(f"Unknown exchange {api_key['exchange'].values[0]}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            await client.close_connection()

    @app_commands.command(name="sell", description="Sell a token/Short a position")
    @app_commands.default_permissions(administrator=True)
    async def sell(self, interaction: discord.Interaction, account: str, symbol: str, quantity: str):
        """Sell a token/Short a position on Binance"""
        try:
            api_key = pd.read_sql_query(f"select * from read_api where account = '{account}' limit 1", self.engine)
            if len(api_key) == 0:
                await interaction.response.send_message(f"Account {account} not found")
                return
            client = await AsyncClient.create(api_key["api_key"].values[0], api_key["api_secret"].values[0])
            if api_key["exchange"].values[0] == 'BINANCE':
                # await interaction.response.send_message(f"Invalid API key")
                res = await client.order_market_sell(symbol=symbol, quantity=quantity)
                logger.info(f"Order result {res}")
                description = textwrap.dedent(f"""\
                    ID: {res['orderId']}
                    Symbol: {res['symbol']}
                    Side: {res['side']}
                    Qty: {res['executedQty']}
                    Average Price: {Decimal(res['cummulativeQuoteQty']) / Decimal(res['executedQty'])}
                """)
                embed = discord.Embed(
                    title=f"SPOT {account} Sell",
                    description=description,
                    color=discord.Color.green()
                )
                await interaction.response.send_message(content=None, embed=embed)

            elif api_key["exchange"].values[0] == 'BINANCEFUTURE':
                order = await client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantity)
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
                    title=f"PERP {account} Sell",
                    description=description,
                    color=discord.Color.green()
                )
                await interaction.response.send_message(content=None, embed=embed)
            else:
                await interaction.response.send_message(f"Unknown exchange {api_key['exchange'].values[0]}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            await client.close_connection()