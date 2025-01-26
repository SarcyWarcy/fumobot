import discord
from discord.ui import View, Button
from io import BytesIO
from discord.ext import commands
import aiohttp
import customutilities
import typing
import asyncio
import asqlite
from datetime import timedelta, datetime
import random
import pydealer as pd
from discord.ext.commands.cooldowns import BucketType

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

class BlackjackView(View):
  def __init__(self, ctx, hand, dealerHand, embed, deck, bet, pscore, timeout = 20):
    super().__init__(timeout=timeout)
    self.ctx = ctx
    self.hand = hand
    self.dealerHand = dealerHand
    self.embed = embed
    self.deck = deck
    self.bet = bet
    self.pscore = pscore

    self.winnings = bet
    self.gameRover = False

  async def interaction_check(self, interaction):
    if interaction.user.id != self.ctx.author.id:
      await interaction.response.send_message("This button is not for you!!", ephemeral=True)
      return False
    else:
      return True

  async def on_timeout(self):
    if not self.gameRover:
      for item in self.children:
        item.disabled= True

      await self.message.edit(view=self)
      await self.ctx.reply("You didn't respond in time! The whole game is cancelled, and, the dealer took your power...")
      await customutilities.updateBalance(self.ctx.author.id, self.bet * -1)
  
  @discord.ui.button(label="Hit!", style=discord.ButtonStyle.green)
  async def hitButton(self, interaction: discord.Interaction, button: Button):
    self.hand.add(self.deck.deal(1))
    self.pscore = customutilities.handValue(self.hand)

    self.embed = discord.Embed(
      description=f"{f"**Oh no! You busted! You lost <:Power:1331214328774529025> {self.bet}**...\n\n" if self.pscore > 21 else ""}**Your Hand**:\n# {" ".join(customutilities.cardEmoji(card) for card in self.hand)}\nScore: {self.pscore}\n\n**Dealer's Hand**:\n# {"<:UnknownOfSuit:1331378270611964068>" if self.pscore <= 21 else customutilities.cardEmoji(self.dealerHand[0])} {" ".join(customutilities.cardEmoji(card) for card in self.dealerHand[1:])}\nScore: {customutilities.handValue(self.dealerHand) if self.pscore > 21 else customutilities.handValue(self.dealerHand[1:])}",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    self.embed.set_footer(
      text=self.ctx.author.name,
      icon_url=self.ctx.author.avatar.url
    )

    if self.pscore > 21:
      await customutilities.updateBalance(self.ctx.author.id, self.bet * -1)
      self.gameOver()
      self.gameRover = True
      self.stop()

    await interaction.response.edit_message(embed=self.embed, view=self)
  
  @discord.ui.button(label="Stand!", style=discord.ButtonStyle.red)
  async def standButton(self, interaction: discord.Interaction, button: Button):
    dealerScore = customutilities.handValue(self.dealerHand)

    while customutilities.handValue(self.dealerHand) < 17:
      self.dealerHand.add(self.deck.deal(1))
      dealerScore = customutilities.handValue(self.dealerHand)
    
    if dealerScore > self.pscore and (dealerScore < 22):
      await customutilities.updateBalance(self.ctx.author.id, self.bet * -1)
      self.gameOver()
      self.gameRover = True
    elif dealerScore == self.pscore:
      self.gameOver()
      self.gameRover = True
    else:
      await customutilities.updateBalance(self.ctx.author.id, self.winnings)
      self.gameOver()
      self.gameRover = True
    
    self.embed = discord.Embed(
      description=f"{f"**Ahh! You lost! You reluctantly gave away <:Power:1331214328774529025> {self.bet} to the dealer!**" if dealerScore > self.pscore and (dealerScore < 22) else "**You drew with the dealer! You didn't win anything...**" if dealerScore == self.pscore else f"**Yay! The dealer {"busted" if dealerScore > 21 else "lost"}! You won <:Power:1331214328774529025> {self.winnings}**"}\n\n**Your Hand**:\n# {" ".join(customutilities.cardEmoji(card) for card in self.hand)}\nScore: {self.pscore}\n\n**Dealer's Hand**:\n# {" ".join(customutilities.cardEmoji(card) for card in self.dealerHand)}\nScore: {customutilities.handValue(self.dealerHand)}",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    self.embed.set_footer(
      text=self.ctx.author.name,
      icon_url=self.ctx.author.avatar.url
    )

    await interaction.response.edit_message(embed=self.embed, view=self)
    self.stop()
  
  def gameOver(self):
    self.standButton.disabled = True
    self.hitButton.disabled = True


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
        description=f"**Balance**:\n<:Power:1331214328774529025> 0",
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
      description=f"**Balance**:\n<:Power:1331214328774529025> {row[0]}",
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
  @commands.max_concurrency(1,per=commands.BucketType.user,wait=False)
  async def dice(self, ctx, power: int = commands.parameter(description="The amount of power to be put on bet.")):
    """Gambles your power away. You win everytime you don't roll a 6. Pays out 0.2x of your original bet."""
    await customutilities.lowBalance(ctx, power=power)
    if power <= 2:
      raise commands.BadArgument("You cannot bet less than <:Power:1331214328774529025> 2!")

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
      description=f"{diceEmojis[roll - 1]} | {"Good job!" if roll != 6 else "Oh no..."} You rolled a {roll}! You {"won" if roll != 6 else "lost"} <:Power:1331214328774529025> {winnings if roll != 6 else winnings * -1}{"!" if roll != 6 else "..."}",
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
  @commands.max_concurrency(1,per=commands.BucketType.user,wait=False)
  async def blackjack(self, ctx, power: int = commands.parameter(description="The amount of power to be put on bet.")):
    """Gambles your power away in a game of Blackjack. Pays out 2x, and Blackjacks pays out 2.5x"""
    await customutilities.lowBalance(ctx, power=power)
    if power <= 0:
      raise commands.BadArgument("You cannot bet less than <:Power:1331214328774529025> 0!")

    bjDeck = pd.Deck()
    bjDeck.shuffle()
    
    playerHand = bjDeck.deal(2)
    dealerHand = bjDeck.deal(2)
    
    initialScore = customutilities.handValue(playerHand)
    
    bjEmbed = discord.Embed(
      description=f"{"**BLACKJACK!**\n" if initialScore == 21 else ""}**Your Hand**:\n# {" ".join(customutilities.cardEmoji(card) for card in playerHand)}\nScore: {initialScore}\n\n**Dealer's Hand**: \n# <:UnknownOfSuit:1331378270611964068> {" ".join(customutilities.cardEmoji(card) for card in dealerHand[1:])}\nScore: {customutilities.handValue(dealerHand[1:])}",
      timestamp=datetime.now(),
      color=discord.Color.purple()
    )
    bjEmbed.set_footer(
      text=ctx.author.name,
      icon_url=ctx.author.avatar.url
    )

    bjMessage = await ctx.reply(embed=bjEmbed)

    view = BlackjackView(ctx, playerHand, dealerHand, bjEmbed, bjDeck, power, initialScore)

    if initialScore == 21:
      view.winnings = power + int((power * 0.5))

    view.message = await bjMessage.edit(embed=bjEmbed, view=view)
    await view.wait()


async def setup(bot):
  await bot.add_cog(FumoCommands(bot))