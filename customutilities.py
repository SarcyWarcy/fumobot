from discord.ext import commands
from datetime import timedelta
import asqlite

# THIS IS ALL FOR CONVERTERS

class Duration(commands.Converter):
  async def convert(self, ctx, argument):
    units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    seconds = 0
    currentTime = ""

    for char in argument:
      if char.isdigit():
        currentTime += char
      elif char in units and currentTime:
        seconds += int(currentTime) * units[char]
        currentTime = ""
      
    return timedelta(seconds=seconds)

# USEFUL FUNCTIONS

async def updateBalance(id: int, power: int):
  async with asqlite.connect("fumo.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute(
        """
        UPDATE players SET balance = balance + ? WHERE id = ?
        """, (power, id)
      )
      await db.commit()

async def checkBalance(id: int):
  async with asqlite.connect("fumo.db") as db:
    async with db.cursor() as cursor:
      result = await cursor.execute(
        """
        SELECT balance FROM players WHERE id = ?
        """, (id)
      )
      row = await result.fetchone()
      return row

# THIS IS FOR CHECKS

class Hierarchy(commands.CheckFailure):
  pass

class NotEnoughMoney(commands.CheckFailure):
  pass

class YoureTheOwner(commands.CheckFailure):
  pass

def roleIsHigher(ctx, member, target):
  if isinstance(target, list):
    for t in target:
      if member.top_role <= t.top_role:
        raise Hierarchy()
      else:
        return
  if member.top_role <= target.top_role:
    raise Hierarchy()
  elif target == target.guild.owner:
    raise YoureTheOwner()
  return

async def lowBalance(ctx, power: int):
  result = await checkBalance(ctx.author.id)
  if result[0] < power:
    raise NotEnoughMoney()
      

  