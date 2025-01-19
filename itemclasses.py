import asyncio
import asqlite

class Item():
  def __init__(self, name: str, price: int, description: str, image: str, category: str):
    self.name = name
    self.price = price
    self.description = description
    self.category = category
    self.image = image

class Fumo(Item):
  def __init__(
      self,
      name: str,
      title: str,
      description: str,
      image: str,
      category: str = "Fumo",
    ):
    self.name = name
    self.title = title
    self.description = description
    self.image = image
  
class GachaBox(Item):
  def __init__(
      self, 
      name: str, 
      price: int, 
      description: str,
      lootDrop: dict[str, Item], 
      category: str = "Pack", 
    ):
    super().__init__(name, price, description, category)
    self.lootDrop = lootDrop
  
  

# ALL THE ITEM OBJECTS

EoSDFumos = {
  "Rumia": Fumo(
    "Rumia", 
    "Youkai of The Dusk", 
    "A silly youkai that can manipulate darkness. Not very good in expeditions... although makes for a very cute pet!",
    "./assets/FumoImages/EoSD/Rumia.png"
  ),
  "Cirno": Fumo(
    "Cirno", 
    "Fairy of The Ice", 
    "An idiotic fairy that has the ability to manipulate ice. Also claims to be the strongest.",
    "./assets/FumoImages/EoSD/Cirno.png"
  ),
  "Koakuma": Fumo(
    "Koakuma", 
    "Library Assistant", 
    "A mischievous little devil, who works as a library assistant. Knowledgable! ...Maybe.",
    "./assets/FumoImages/EoSD/Koakuma.png"
  ),
  "Meiling": Fumo(
    "Hong Meiling", 
    "Chinese Girl", 
    "A skilled combatant and a gatekeeper. Though lazy and narcoleptic..",
    "./assets/FumoImages/EoSD/Meiling.png"
  ),
  "Patchouli": Fumo(
    "Patchouli Knowledge", 
    "The Unmoving Great Library", 
    "A highly knowledgable magician (it's even in the name!). Not very good at moving, although very strong in her spells! ",
    "./assets/FumoImages/EoSD/Patchouli.png"
  ),
  "Remilia": Fumo(
    "Remilia Scarlet", 
    "The Scarlet Devil", 
    "A fate-manipulating vampire. Charming and mysterious... although also silly at times.",
    "./assets/FumoImages/EoSD/Remilia.png"
  ),
  "Flandre": Fumo(
    "Flandre Scarlet", 
    "Sister of the Devil", 
    "A highly dangerous and destructive vampire. Thread carefully when interacting with this one!",
    "./assets/FumoImages/EoSD/Flandre.png"
  )
}

EoSDBox = GachaBox("Embodiment of Scarlet Devil", 200, "A pack that contain all EoSD Fumos!", EoSDFumos)