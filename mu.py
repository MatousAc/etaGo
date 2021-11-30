# defines a human agent to play Go Fish
from fisherface import fisher

class muGo(fisher):
  def think(self): # obtains and organizes info
    print(self.game)
  def play(self): # chooses a player and card
    # player_asked = int(input("enter player to ask (0-3): "))
    # rank, suit = input("enter card (2 hearts): ").split()
    self.info["player_asked"] = int(input("enter player to ask (0-3): "))
    self.info["card_played"] = input("enter card (2 hearts): ")



if __name__ == "__main__":
  player = muGo()