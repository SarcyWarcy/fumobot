import asyncio
import asqlite

class Items():
  def __init__(self, name: str, price: int, description: str):
    self.name = name
    self.price = price
    self.description = description
  
  async def buy(self, ctx):
    async with asqlite.connect("fumo.db") as db:
      async with db.cursor() as cursor:
        return