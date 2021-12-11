# defines a human agent to play Go Fish
from ai import aiBase

class sigmaGo(aiBase):
  NAME = "sigmaGo"
  def play(self): # chooses a player and card
    self.info["player_asked"] = int(input("enter player to ask (0-3): "))
    self.info["card_played"] = input("enter card (2 hearts): ")

if __name__ == "__main__":
  player = sigmaGo()