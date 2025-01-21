import discord
from io import BytesIO
from discord.ext import commands
import aiohttp
import customutilities
import typing
import asyncio
import asqlite
from datetime import timedelta, datetime
import random
from PIL import Image

async def fumoDbCheck():
  async with asqlite.connect("fumo.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("""
      CREATE TABLE IF NOT EXISTS players (
      id INTEGER PRIMARY KEY,
      username TEXT,
      balance INTEGER DEFAULT 100                     
      )
      """)
      await db.commit()

class FumoCommands(commands.Cog, name="Fumo"):
  """Take care of your Fumos here in this simple pet economy game!"""
  def __init__(self, bot):
    self.bot = bot
  
  async def cog_before_invoke(self, ctx):
    async with asqlite.connect("fumo.db") as db:
      async with db.cursor() as cursor:
        await cursor.execute(
          """
          INSERT INTO players (id, username)
          VALUES (?, ?)
          ON CONFLICT (id)
          DO UPDATE SET 
            username = excluded.username
          """, (ctx.author.id, ctx.author.name)
        )
  
  @commands.command(name="collection")
  async def collection(self, ctx, user: discord.User = commands.parameter(default=None, description="The user to be inputted.")):
    """Find out a user's / your Fumo collection!"""
    user = user or ctx.author
  
  @commands.command(name="balance", aliases=["bal", "points"])
  async def balance(self, ctx, user: discord.User = commands.parameter(default=None, description="The user to be inputted.")):
    """Check a user's balance / power."""
    user = user or ctx.author
    row = await customutilities.checkBalance(user.id)

    if row is None:
      await ctx.reply(embed=discord.Embed(
        description=f"**Balance**:\n<:power_item:1329068042650386518> 0",
        timestamp=datetime.now(),
        color=discord.Color.purple(),
      ).set_footer(
        text=ctx.author.name,
        icon_url=ctx.author.avatar.url
      ).set_author(
        name=user.name, 
        icon_url=user.avatar.url
      ))
      return
          
    balanceEmbed = discord.Embed(
      description=f"**Balance**:\n<:power_item:1329068042650386518> {row[0]}",
      timestamp=datetime.now(),
      color=discord.Color.purple(),
    )
    balanceEmbed.set_footer(
      text=ctx.author.name,
      icon_url=ctx.author.avatar.url
    )
    balanceEmbed.set_author(name=user.name, icon_url=user.avatar.url)

    await ctx.reply(embed=balanceEmbed)
  
  @commands.command(name="dice")
  async def dice(self, ctx, power: int = commands.parameter(description="The amount of power to be put on bet.")):
    """Gambles your power away. You win everytime you don't roll a 6. Pays out 0.2x of your original bet."""
    await customutilities.lowBalance(ctx, power=power)
    if power <= 2:
      raise commands.BadArgument("You cannot bet less than <:power_item:1329068042650386518> 2!")

    diceEmojis = [
      "<:DiceOne:1331122935322382437>",
      "<:DiceTwo:1331122981635756042>",
      "<:DiceThree:1331123022962233414>",
      "<:DiceFour:1331123084597530624>",
      "<:DiceFive:1331123131116687403>",
      "<:DiceSix:1331123203661107284>"
      ]
    rollingEmbed = discord.Embed(
      description=f"<a:DiceAnimation:1331122379128045670> | Rolling a dice for <:Power:1331214328774529025> {power}...",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    rollingEmbed.set_footer(
      text=ctx.author.name,
      icon_url=ctx.author.avatar.url
    )
    rolled = await ctx.reply(embed=rollingEmbed)
    roll = random.randint(1, 6)
    winnings = round(power * 0.2) if roll != 6 else power * -1
    rolledEmbed = discord.Embed(
      description=f"{diceEmojis[roll - 1]} | {"Good job!" if roll != 6 else "Oh no..."} You rolled a {roll}! You {"won" if roll != 6 else "lost"} <:power_item:1329068042650386518> {winnings if roll != 6 else winnings * -1}{"!" if roll != 6 else "..."}",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    rolledEmbed.set_footer(
      text=ctx.author.name,
      icon_url=ctx.author.avatar.url
    )
    await asyncio.sleep(4.5)

    await customutilities.updateBalance(ctx.author.id, winnings)
    await rolled.edit(embed=rolledEmbed)
  
  @commands.command(name="blackjack", aliases=["bj"])
  async def blackjack(self, ctx, power: int = commands.parameter(description="The amount of power to be put on bet.")):
    pass

async def setup(bot):
  await bot.add_cog(FumoCommands(bot))