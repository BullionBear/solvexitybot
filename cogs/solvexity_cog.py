import discord
from discord.ext import commands
from discord import app_commands
from binance import AsyncClient
from utils import symbol_filter
import decimal
import logging

logger = logging.getLogger(__name__)

class SolvexityDataCog(commands.Cog):
    def __init__(self, bot: commands.Bot, accounts: list):
        self.accounts = accounts
        self.bot = bot
        self.is_first_msg = True

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"SolvexityDataCog loaded")

    @app_commands.command(name="balance", description="Get all account balances")
    async def balance(self, interaction: discord.Interaction):
        """Responds with a balance"""
        await interaction.response.defer()
        self.is_first_msg = True
        for account in self.accounts:
            try:
                account_name = account['name']
                api_key = account['api_key']
                api_secret = account['api_secret']
                client = await AsyncClient.create(api_key, api_secret)
                account_info = await client.get_account()
                balances = account_info['balances']
                description = ""
                total_usd_value = decimal.Decimal(0)
                embed = discord.Embed(
                    title=f"{account_name} Spot Balances",
                    description=description,
                    color=discord.Color.random()
                )
                for balance in balances:           
                    if float(balance['free']) > 0 or float(balance['locked']) > 0:
                        if balance['asset'] in ['USDT', 'USDC']:
                            px = decimal.Decimal(1)
                            free = decimal.Decimal(balance['free']).quantize(decimal.Decimal('0.01'))
                            locked = decimal.Decimal(balance['locked']).quantize(decimal.Decimal('0.01'))
                            amount = free + locked
                        else:
                            symbol = balance['asset'] + 'USDT'
                            ticker = await client.get_symbol_ticker(symbol=symbol)
                            px = decimal.Decimal(ticker['price'])
                            free = decimal.Decimal(balance['free'])
                            free, px = symbol_filter(symbol, free, px)
                            locked = decimal.Decimal(balance['locked'])
                            locked, px = symbol_filter(symbol, locked, px)
                            amount = free + locked
                        usd_value = amount * px
                        if free.is_zero():
                            free = decimal.Decimal(0)
                        if locked.is_zero():
                            locked = decimal.Decimal(0)
                        usd_value = usd_value.quantize(decimal.Decimal('0.01'))
                        embed.add_field(name=balance['asset'], value=f"Free: {free}, Locked: {locked}, USD Value: {usd_value}", inline=False)
                        total_usd_value += usd_value
                embed.set_footer(text="Total USD Value: " + str(total_usd_value))
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(content=None, embed=embed)
                else:
                    await interaction.followup.send(content=None, embed=embed)
            except Exception as e:
                logger.error(f"Error retrieving spot balance: {e}", exc_info=True)
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(f"Error retrieving spot balance for {account['name']}: {e}")
                else:
                    await interaction.followup.send(f"Error retrieving spot balance for {account['name']}: {e}")         
            finally:
                # if client exists, close the connection
                if 'client' in locals():
                    await client.close_connection()
    
    @app_commands.command(name="fbalance", description="Get futures account balances")
    async def fbalance(self, interaction: discord.Interaction):
        """Responds with a position"""
        self.is_first_msg = True

        for account in self.accounts:
            try:
                account_name = account['name']
                api_key = account['api_key']
                api_secret = account['api_secret']
                client = await AsyncClient.create(api_key, api_secret)
                account_info = await client.futures_account_balance()
                description = ""
                embed = discord.Embed(
                    title=f"{account_name} Perp Balances",
                    description=description,
                    color=discord.Color.random()
                )
                for balance in account_info:
                    if decimal.Decimal(balance['balance']) > 0:
                        asset = balance['asset']
                        amount = decimal.Decimal(balance['crossWalletBalance'])
                        free = decimal.Decimal(balance['availableBalance'])
                        locked = amount - free
                        if asset in ['USDT', 'USDC']:
                            free = decimal.Decimal(free).quantize(decimal.Decimal('0.01'))
                            locked = decimal.Decimal(locked).quantize(decimal.Decimal('0.01'))
                        else:
                            symbol = asset + 'USDT'
                            dummy = decimal.Decimal(1)
                            free, _ = symbol_filter(symbol, decimal.Decimal(free), dummy)
                            locked, _ = symbol_filter(symbol, decimal.Decimal(locked), dummy)
                        if free.is_zero():
                            free = decimal.Decimal(0)
                        if locked.is_zero():
                            locked = decimal.Decimal(0)
                        embed.add_field(name=asset, value=f"Free: {free}, Locked: {locked}", inline=False)
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(content=None, embed=embed)
                else:
                    await interaction.followup.send(content=None, embed=embed)
            except Exception as e:
                logger.error("Error handling /position command", exc_info=True)
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(f"Error retrieving perp balance for {account['name']}: {e}")
                else:
                    await interaction.followup.send(f"Failed to get positions: {e}")
            finally:
                # if client exists, close the connection
                if 'client' in locals():
                    await client.close_connection()


    @app_commands.command(name="position", description="Get perp positions")
    async def position(self, interaction: discord.Interaction):
        """Responds with a position"""
        self.is_first_msg = True
        for account in self.accounts:
            try:
                account_name = account['name']
                api_key = account['api_key']
                api_secret = account['api_secret']
                client = await AsyncClient.create(api_key, api_secret)
                description = ""
                positions = await client.futures_position_information()
                embed = discord.Embed(
                    title=f"{account_name} Perp Positions",
                    description=description,
                    color=discord.Color.random()
                )
                for position in positions:
                    if decimal.Decimal(position['positionAmt']) != 0:
                        symbol = position['symbol']
                        amount = decimal.Decimal(position['positionAmt'])
                        entry_price = decimal.Decimal(position['entryPrice'])
                        unrealized_profit = decimal.Decimal(position['unRealizedProfit']).quantize(decimal.Decimal('0.01'))
                        embed.add_field(name=symbol, value=f"Position: {amount}, Entry Px: {entry_price}, Unrealized: {unrealized_profit}", inline=False)
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(content=None, embed=embed)
                else:
                    await interaction.followup.send(content=None, embed=embed)
            except Exception as e:
                logger.error("Error handling /position command", exc_info=True)
                if self.is_first_msg:
                    self.is_first_msg = False
                    await interaction.response.send_message(f"Error retrieving perp positions for {account['name']}: {e}")
                else:
                    await interaction.followup.send(f"Failed to get positions: {e}")
            finally:
                # if client exists, close the connection
                if 'client' in locals():
                    await client.close_connection()

