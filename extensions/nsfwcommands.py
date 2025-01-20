import discord
from io import BytesIO
from discord.ext import commands
import aiohttp
import customutilities
import typing
from datetime import timedelta, datetime

class NSFWCommands(commands.Cog, name="NSFW"):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="ntag")
  async def ntag(
    self,
    ctx,
    #*,
    #tags: commands.Greedy[str] = commands.parameter(description="The tags to be added into one of the presets.")
  ):
    """A command to save presets to automatically sort stuff based on what you like."""
    await ctx.reply("This command isn't working... yet! Stay tuned!")

async def setup(bot):
  await bot.add_cog(NSFWCommands(bot))