import discord
from discord.ext import commands
from discord import app_commands
import logging
from binance import AsyncClient
from decimal import Decimal
import textwrap
import bot.cogs.const as const

logger = logging.getLogger(__name__)

class AccountValidator:
    def __init__(self, accounts):
        self.accounts = accounts

    def validate_account(self, account_name):
        if account_name not in [acc['name'] for acc in self.accounts]:
            return None
        return [acc for acc in self.accounts if acc['name'] == account_name][0]

class BinanceClientFactory:
    @staticmethod
    async def create_client(api_key, api_secret):
        return await AsyncClient.create(api_key, api_secret)

class OrderExecutor:
    def __init__(self, client):
        self.client = client

    async def execute_spot_order(self, symbol, quantity, side):
        if side == "BUY":
            return await self.client.order_market_buy(symbol=symbol, quantity=quantity)
        elif side == "SELL":
            return await self.client.order_market_sell(symbol=symbol, quantity=quantity)

    async def execute_futures_order(self, symbol, quantity, side):
        return await self.client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)

class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.accounts = const.CONFIG['accounts']
        self.account_validator = AccountValidator(self.accounts)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"TradingCog loaded")

    async def process_order(self, interaction, account, symbol, quantity, side, order_type):
        account_data = self.account_validator.validate_account(account.value)
        if not account_data:
            await interaction.response.send_message(f"Account {account.value} not found")
            return

        api_key = account_data['api_key']
        api_secret = account_data['api_secret']
        client = await BinanceClientFactory.create_client(api_key, api_secret)

        try:
            executor = OrderExecutor(client)
            if order_type == "SPOT":
                res = await executor.execute_spot_order(symbol.value, quantity, side)
                average_px = Decimal(res['cummulativeQuoteQty']) / Decimal(res['executedQty'])
                qty = Decimal(res['executedQty'])
            elif order_type == "FUTURES":
                res = await executor.execute_futures_order(symbol.value, quantity, side)
                average_px = Decimal(res['avgPrice'])
                qty = Decimal(res['origQty'])

            logger.info(f"Order result {res}")
            description = textwrap.dedent(f"""\
                ID: {res['orderId']}
                Symbol: {res['symbol']}
                Side: {res['side']}
                Qty: {qty}
                Average Price: {average_px}
            """)
            embed = discord.Embed(
                title=f"{order_type} {account_data['name']} {side}",
                description=description,
                color=discord.Color.green()
            )
            await interaction.response.send_message(content=None, embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
        finally:
            await client.close_connection()

    @app_commands.command(name="buy", description="Buy a token/Long a position")
    @app_commands.choices(account=const.ACCOUNT_CHOICES, symbol=const.SPOT_CHOICES)
    @app_commands.default_permissions(administrator=True)
    async def buy(self, interaction: discord.Interaction, account: app_commands.Choice[str], symbol: app_commands.Choice[str], quantity: str):
        await self.process_order(interaction, account, symbol, quantity, "BUY", "SPOT")

    @app_commands.command(name="sell", description="Sell a token")
    @app_commands.choices(account=const.ACCOUNT_CHOICES, symbol=const.SPOT_CHOICES)
    @app_commands.default_permissions(administrator=True)
    async def sell(self, interaction: discord.Interaction, account: app_commands.Choice[str], symbol: app_commands.Choice[str], quantity: str):
        await self.process_order(interaction, account, symbol, quantity, "SELL", "SPOT")

    @app_commands.command(name="long", description="Long a position")
    @app_commands.choices(account=const.ACCOUNT_CHOICES, symbol=const.PERP_CHOICES)
    @app_commands.default_permissions(administrator=True)
    async def long(self, interaction: discord.Interaction, account: app_commands.Choice[str], symbol: app_commands.Choice[str], quantity: str):
        await self.process_order(interaction, account, symbol, quantity, "BUY", "FUTURES")

    @app_commands.command(name="short", description="Short a position")
    @app_commands.choices(account=const.ACCOUNT_CHOICES, symbol=const.PERP_CHOICES)
    @app_commands.default_permissions(administrator=True)
    async def short(self, interaction: discord.Interaction, account: app_commands.Choice[str], symbol: app_commands.Choice[str], quantity: str):
        await self.process_order(interaction, account, symbol, quantity, "SELL", "FUTURES")
