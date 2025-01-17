from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union, Optional
import asqlite
import discord
import io
from io import BytesIO
import pyautogui
from discord.ext import commands
import aiohttp
from contextlib import redirect_stdout
import typing
import traceback
import textwrap
from PIL import Image

class DevCommands(commands.Cog, name="Developer"):
  """These commands are for testing / debugging purposes, that help in the development of the bot. 
  Only Sarc can access this. Shoo!"""
  def __init__(self, bot):
    self.bot = bot
    self._last_result: Optional[Any] = None

  def cleanup_code(self, content: str) -> str:
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
      return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')

  
  @commands.command(name="takess")
  @commands.is_owner()
  async def takess(self, ctx):
    """Takes a screenshot of my screen. Please do not stalk me..."""
    ss = pyautogui.screenshot()
    with BytesIO() as screenshotter:
      ss.save(screenshotter, 'PNG')
      screenshotter.seek(0)
      await ctx.reply(file=discord.File(screenshotter, 'backshotter.png'))

  @commands.command(name="movemouse")
  @commands.is_owner()
  async def movemouse(self, ctx, coordX: int = commands.parameter(description="The X coordinate."), coordY: int = commands.parameter(description="The Y coordinate.")):
    """Moves my mouse cursor to the desired position."""
    pyautogui.move(coordX, coordY)
    await ctx.reply(f"Moved your mouse position to {coordX, coordY}")

  @commands.command(name="mousepos")
  @commands.is_owner()
  async def mousepos(self, ctx):
    """Provides the exact coordinates of my mouse cursor."""
    await ctx.reply(f"Your mouse position is: {pyautogui.position()}")

  @commands.command(name="rext")
  @commands.is_owner()
  async def rext(self, ctx, extension: str = commands.parameter(description="The extension to be reloaded.")):
    """Reloads a Python extension."""
    await self.bot.reload_extension(extension)
    await ctx.reply(f"Reloaded the extension `{extension}`!")
  
  @commands.command(name="openpfp")
  @commands.is_owner()
  async def openpfp(self, ctx):
    member = ctx.author
    pfp = member.avatar.url

    async with aiohttp.ClientSession() as session:
      async with session.get(pfp) as response:
        if response.status == 200:
          pfpBytes = await response.read()
          pfpImg = Image.open(BytesIO(pfpBytes))
          pfpImg.show()

          await ctx.reply("Showed PFP")
  
  @commands.command(name="eval")
  @commands.is_owner()
  async def eval(self, ctx, *, code: str = commands.parameter(description="The code to be executed.")):
    """Executes Python code with the given argument."""
    env = {
      'bot': self.bot,
      'ctx': ctx,
      'channel': ctx.channel,
      'author': ctx.author,
      'guild': ctx.guild,
      'message': ctx.message,
      '_': self._last_result,
    }

    env.update(globals())

    code = self.cleanup_code(code)
    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

    try:
      exec(to_compile, env)
    except Exception as e:
      return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

    func = env['func']
    try:
      with redirect_stdout(stdout):
        ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass

        if ret is None:
            if value:
                await ctx.send(f'```py\n{value}\n```')
        else:
            self._last_result = ret
            await ctx.send(f'```py\n{value}{ret}\n```')
  
  @commands.command(name="generate")
  @commands.is_owner()
  async def generate(
     self, 
     ctx,
     amount: typing.Optional[int] = commands.parameter(description="The amount to be generated.", default=1), 
     user: discord.User = commands.parameter(
      description="The user to be inputted to generate coins for.",
      default=None
     ),
    ):
     """Generate / give points to a user."""
     user = user or ctx.author
     async with asqlite.connect("fumo.db") as db:
        async with db.cursor() as cursor:
          result = await cursor.execute(
              """
              INSERT INTO players (id, username, balance) VALUES (?, ?, ?)
              ON CONFLICT (id) 
              DO UPDATE SET balance = balance + ?
              """,
              (user.id, user.name, amount, amount)
           )
          await db.commit()
          resultBalance = await cursor.execute(
             """
             SELECT balance FROM players WHERE id = ? 
             """,
            (user.id)
          )
          row = await resultBalance.fetchone() 
          await ctx.send(f":white_check_mark: | Successfully generated! {user.mention} now has <:power_item:1329068042650386518> {row[0]} ")
           

async def setup(bot):
  await bot.add_cog(DevCommands(bot))