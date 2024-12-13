import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.engine import Engine
import pandas as pd
from tabulate import tabulate
import logging

logger = logging.getLogger(__name__)
 
class SolvexityDataCog(commands.Cog):
    def __init__(self, bot: commands.Bot, engine: Engine):
        self.bot = bot
        self.engine = engine

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"SolvexityDataCog loaded")

    @app_commands.command(name="balance", description="Get account balances")
    async def balance(self, interaction: discord.Interaction, account: str):
        """Responds with a balance"""
        try:
            api_key = pd.read_sql_query(f"select * from read_api where account = '{account}' limit 1", self.engine)
            if len(api_key) == 0:
                await interaction.response.send_message(f"Account {account} not found")
                return
            if api_key["exchange"].values[0] == 'BINANCE':
                # await interaction.response.send_message(f"Invalid API key")
                df = pd.read_sql_query(f"""
                                        SELECT dt, token, amount, value_in_usd FROM spot_balance 
                                        WHERE account = '{account}'
                                        AND sid = (
                                            SELECT MAX(sid)
                                            FROM spot_balance
                                            WHERE account = '{account}'
                                        )
                                        """, self.engine)
                table = tabulate(df, headers="keys", tablefmt="github", showindex=False)
                # Wrap the table in a code block for Discord
                formatted_table = f"```\n{table}\n```"
                embed = discord.Embed(
                    title=f"SPOT {account} balance in USD",
                    description=f"Value in USD: {df['value_in_usd'].sum():.2f}",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(formatted_table, embed=embed)

            elif api_key["exchange"].values[0] == 'BINANCEFUTURE':
                # await interaction.response.send_message(f"Invalid API key")
                df = pd.read_sql_query(f"""
                                        SELECT dt, token, amount, value_in_usd FROM perp_balance 
                                        WHERE account = '{account}'
                                        AND sid = (
                                            SELECT MAX(sid)
                                            FROM perp_balance
                                            WHERE account = '{account}'
                                        )
                                        """, self.engine)
                table = tabulate(df, headers="keys", tablefmt="github", showindex=False)
                # Wrap the table in a code block for Discord
                formatted_table = f"```\n{table}\n```"
                embed = discord.Embed(
                    title=f"PERP {account} balance in USD",
                    description=f"Value in USD {df['value_in_usd'].sum():.2f}",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(formatted_table, embed=embed) 
            else:
                await interaction.response.send_message(f"{api_key['exchange']} is not implemented")
        except Exception as e:
            logger.error("Error handling /balance command", exc_info=True)
            await interaction.response.send_message(f"Failed to get balance: {e}")
            
