import discord
import pyautogui
from discord.ext import commands
from datetime import datetime

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# PVZ MAIN / NON CODE SECTION
columns = "abcdefghi"
rows = range(1, 6)
startX = 80
startY = 528
spaceX = 82 #This is the space of the x coordinate for each tile
spaceY = 108 #This is the space of the y coordinate for each tile

columnsSelect = "abcdefgh"
startXSelect = 46
startYSelect = 163
spaceXSelect = 53 #This is the space of the x coordinate for each select plant tile
spaceYSelect = 77 #This is the space of the y coordinate for each select plant tile

sunImg = './assets/backshotter.png'
plantSlotCoords = {
  '1': 118,
  '2': 177,
  '3': 239,
  '4': 297,
  '5': 355,
  '6': 414
}
pvzHelpCommand = discord.Embed(colour=0x9b59b6, title="How to control the PvZ Stream", description="""
The commands to control the bot should be started with a prefix. 
\n To start the game, use `*startgame`. Sun collection is simple, type in `*sun`, and it will collect them automatically.\n\n""")
pvzHelpCommand.set_image(url='https://media.discordapp.net/attachments/623132444786425858/1317347876602642592/image.png?ex=675e5b50&is=675d09d0&hm=d99139d68c76e40107f2c173601faf8da33427cec5dd76c724bdf4845ea671ce&=&width=832&height=467')

def getLevelTile(notation: str):
  try:
    colLetter = notation[0].lower()
    rowLetter = int(notation[1])
  except:
    raise commands.BadArgument(message=f"Bad argument for `notation`. Try to use `*help place` for the proper usage.")
  
  if (colLetter in columns) and (rowLetter in rows):
    colIndex = columns.index(colLetter) #Gets the index / corresponding number of the letter

    tileX = startX + (colIndex * spaceX)
    tileY = startY - ((rowLetter - 1) * spaceY)
    return tileX, tileY
  else:
    return None
  
def getSeedTile(notation: str):
  try:
    colLetter = notation[0].lower()
    rowLetter = int(notation[1])
  except:
    raise commands.BadArgument(message=f"Bad argument for `notation`. Try to use `*help select` for the proper usage.")
  
  if (colLetter in columnsSelect) and (rowLetter in rows):
    colIndex = columnsSelect.index(colLetter) #Gets the index / corresponding number of the letter

    tileX = startXSelect + (colIndex * spaceXSelect)
    tileY = startYSelect + ((rowLetter - 1) * spaceYSelect)
    return tileX, tileY
  else:
    return None
    

class PvZControls(commands.Cog, name="PvZ Controls"):
  """These commands are for controlling PvZ in my PC from purely Discord text / commands. Have fun!"""
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="pvzhelp")
  async def pvzhelp(self, ctx):
    """Sends a DM guide on how to use the PvZ Stream Control Commands."""
    await ctx.author.send(embed=pvzHelpCommand)

  @commands.command(name="startgame")
  async def startgame(self, ctx):
    """Starts the PvZ Game while in the main menu."""
    pyautogui.click(x=538, y=138)
    await ctx.reply(f":white_check_mark:")
    
  @commands.command(name="plant")
  async def plant(self, ctx, slot: str = commands.parameter(description="The slot to be selected.")):
    """Selects the selected seed slot to plant. The seed slot ranges from 1 - 6, from left to right order."""
    if slot in plantSlotCoords:
      x = plantSlotCoords[slot]
      pyautogui.click(x, 45)
      await ctx.reply(f":white_check_mark:")
    else:
      raise commands.BadArgument(message=f"Bad argument for `slot`. Try to use `*help plant` for the proper usage.")

  @commands.command(name="shovel")
  async def shovel(self, ctx):
    """Selects the shovel in a level."""
    pyautogui.click(490, 39)
    await ctx.reply(f":white_check_mark:")

  @commands.command(name="sun")
  async def sun(self, ctx):
    """Autocollects sun that appears on the screen. You may only collect one sun per message / command."""
    sunPos = pyautogui.locateCenterOnScreen(sunImg, confidence=0.8)
    pyautogui.click(sunPos)
    await ctx.reply(f":white_check_mark:")

  @commands.command(name="place")
  async def place(self, ctx, notation: str = commands.parameter(description="The Chess-like notation to be inputted.")):
    """Selects a tile in the level. Uses a Chessboard-like notation, e.g: A5 or E3"""
    coordPlacement = getLevelTile(notation)

    tileX, tileY = coordPlacement
    pyautogui.click(tileX, tileY)
    await ctx.reply(f":white_check_mark:")

  @commands.command(name="select")
  async def select(self, ctx, notation: str = commands.parameter(description="The Chess-like notation to be inputted.")):
    """Selects a seed packet / plant before the start of the game. Uses a Chessboard-like notation, e.g: A5 or E3"""
    coordPlacement = getSeedTile(notation)

    tileX, tileY = coordPlacement
    pyautogui.click(tileX, tileY)
    await ctx.reply(f":white_check_mark:")

async def setup(bot):
  await bot.add_cog(PvZControls(bot))