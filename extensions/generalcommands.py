import discord
from io import BytesIO
from discord.ext import commands
import aiohttp
import customutilities
import typing
from datetime import timedelta, datetime
from PIL import Image

class ModerationCommands(commands.Cog, name="Moderation"):
  """Simple moderation commands to keep the server safe!"""
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="timeout")
  @commands.has_permissions(moderate_members=True)
  async def timeout(
    self, 
    ctx, 
    members: commands.Greedy[discord.Member] = commands.parameter(
      description="The member(s) to be timeoutted."
    ), 
    duration: customutilities.Duration = commands.parameter(
      description="The duration the member will be timeoutted for. Example of the duration format: `3h`, `3m`, `3s`, `2h2m`."
    ), 
    *, 
    reason: str = commands.parameter(
      description="The reason to timeout the user. Will be inputted into the Audit Log. Due to Discord limitations, timeout may not be longer than 28 days.",
      default="No reason provided."
    )
  ):
    """Timeouts a member."""
    customutilities.roleIsHigher(ctx, ctx.author, members)
    timeoutted = ", ".join(member.name for member in members)
    
    for member in members:
      await member.timeout(duration, reason=reason)
      print(member)

    await ctx.reply(f"{timeoutted} have been timeoutted for {duration}. Reason: {reason}")

class GeneralCommands(commands.Cog, name="General"):
  """General commands for general purpose use."""
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name="nick")
  async def nick(
    self,
    ctx,
    nick: str = commands.parameter(description="The nickname you want to change into.")
  ):
    """Changes your nickname in a server."""
    await ctx.author.edit(nick=nick)
    await ctx.reply(":white_check_mark:")

  @commands.command(name="invite")
  async def invite(self, ctx):
    """Sends an invite link for you to invite me."""
    inviteEmbed = discord.Embed(
      title="Invite for SarcAceTic",
      description="""[Invite (admin perms)](https://discord.com/oauth2/authorize?client_id=1317325643217899633&permissions=8&integration_type=0&scope=bot)
      \n[Invite (moderator perms, recommended)](https://discord.com/oauth2/authorize?client_id=1317325643217899633&permissions=584006530624710&integration_type=0&scope=bot)
      \n[Invite (basic perms)](https://discord.com/oauth2/authorize?client_id=1317325643217899633&permissions=2355991796928&integration_type=0&scope=bot)""",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    inviteEmbed.set_footer(
      text=ctx.author.name,
      icon_url=ctx.author.avatar.url
    )

    await ctx.reply(embed=inviteEmbed)

async def setup(bot):
  await bot.add_cog(ModerationCommands(bot))
  await bot.add_cog(GeneralCommands(bot))