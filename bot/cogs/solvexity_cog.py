import discord
from discord.ext import commands
from discord import app_commands
from binance import AsyncClient
from utils import symbol_filter, is_symbol_valid
import decimal
import logging
import bot.cogs.const as const

logger = logging.getLogger(__name__)

class BinanceService:
    """Service class to handle Binance API interactions."""
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = None

    async def initialize_client(self):
        self.client = await AsyncClient.create(self.api_key, self.api_secret)

    async def close_client(self):
        if self.client:
            await self.client.close_connection()

    async def get_spot_balances(self):
        account_info = await self.client.get_account()
        return account_info['balances']

    async def get_futures_balances(self):
        return await self.client.futures_account_balance()

    async def get_futures_positions(self):
        return await self.client.futures_position_information()

class SolvexityDataCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.accounts = const.CONFIG['accounts']
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"SolvexityDataCog loaded")

    async def _send_embed(self, interaction: discord.Interaction, embed: discord.Embed):
        await interaction.followup.send(content=None, embed=embed)

    async def _handle_account(self, interaction: discord.Interaction, account: dict, handler):
        try:
            account_name = account['name']
            api_key = account['api_key']
            api_secret = account['api_secret']
            service = BinanceService(api_key, api_secret)
            await service.initialize_client()

            embed = await handler(service, account_name)
            await self._send_embed(interaction, embed)
        except Exception as e:
            logger.error(f"Error handling account {account['name']}: {e}", exc_info=True)
            await interaction.followup.send(f"Error handling account {account['name']}: {e}")
        finally:
            await service.close_client()

    @app_commands.command(name="balance", description="Get all account balances")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async def handle_balance(service: BinanceService, account_name: str):
            balances = await service.get_spot_balances()
            embed = discord.Embed(
                title=f"{account_name} Spot Balances",
                color=discord.Color.random()
            )
            total_usd_value = decimal.Decimal(0)

            for balance in balances:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    if balance['asset'] in ['USDT', 'USDC']:
                        px = decimal.Decimal(1)
                        free = decimal.Decimal(balance['free']).quantize(decimal.Decimal('0.01'))
                        locked = decimal.Decimal(balance['locked']).quantize(decimal.Decimal('0.01'))
                        amount = free + locked
                    else:
                        symbol = balance['asset'] + 'USDT'
                        free = decimal.Decimal(balance['free'])
                        free, px = symbol_filter(symbol, free, px)
                        locked = decimal.Decimal(balance['locked'])
                        locked, px = symbol_filter(symbol, locked, px)
                        amount = free + locked
                        if is_symbol_valid(symbol):
                            ticker = await service.client.get_symbol_ticker(symbol=symbol)
                            px = decimal.Decimal(ticker['price'])
                            
                        else:
                            px = decimal.Decimal(0)

                    usd_value = amount * px
                    usd_value = usd_value.quantize(decimal.Decimal('0.01'))
                    if usd_value.is_zero():
                        continue

                    embed.add_field(name=balance['asset'], value=f"Free: {free}, Locked: {locked}, USD Value: {usd_value}", inline=False)
                    total_usd_value += usd_value

            embed.set_footer(text="Total USD Value: " + str(total_usd_value))
            return embed

        for account in self.accounts:
            await self._handle_account(interaction, account, handle_balance)

    @app_commands.command(name="fbalance", description="Get futures account balances")
    async def fbalance(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async def handle_fbalance(service: BinanceService, account_name: str):
            balances = await service.get_futures_balances()
            embed = discord.Embed(
                title=f"{account_name} Perp Balances",
                color=discord.Color.random()
            )

            for balance in balances:
                if decimal.Decimal(balance['balance']) > 0:
                    asset = balance['asset']
                    amount = decimal.Decimal(balance['crossWalletBalance'])
                    free = decimal.Decimal(balance['availableBalance'])
                    locked = amount - free

                    if asset in ['USDT', 'USDC']:
                        free = free.quantize(decimal.Decimal('0.01'))
                        locked = locked.quantize(decimal.Decimal('0.01'))
                    else:
                        symbol = asset + 'USDT'
                        dummy = decimal.Decimal(1)
                        free, _ = symbol_filter(symbol, free, dummy)
                        locked, _ = symbol_filter(symbol, locked, dummy)

                    embed.add_field(name=asset, value=f"Free: {free}, Locked: {locked}", inline=False)

            return embed

        for account in self.accounts:
            await self._handle_account(interaction, account, handle_fbalance)

    @app_commands.command(name="position", description="Get perp positions")
    async def position(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async def handle_position(service: BinanceService, account_name: str):
            positions = await service.get_futures_positions()
            embed = discord.Embed(
                title=f"{account_name} Perp Positions",
                color=discord.Color.random()
            )

            for position in positions:
                if decimal.Decimal(position['positionAmt']) != 0:
                    symbol = position['symbol']
                    amount = decimal.Decimal(position['positionAmt'])
                    entry_price = decimal.Decimal(position['entryPrice'])
                    unrealized_profit = decimal.Decimal(position['unRealizedProfit']).quantize(decimal.Decimal('0.01'))
                    embed.add_field(name=symbol, value=f"Position: {amount}, Entry Px: {entry_price}, Unrealized: {unrealized_profit}", inline=False)

            return embed

        for account in self.accounts:
            await self._handle_account(interaction, account, handle_position)

