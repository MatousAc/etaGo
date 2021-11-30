# defines a rule-based agent to play Go Fish
from fisherface import fisher
class etaGo(fisher):
  def __init__(self):
    self.phands = []
    self.stats = {
      "num_players"   : 0,
      "unknown_cards"   : 52,
      "first_pass"    : True
    }
    super().__init__()

  def possibilities_deck(self): # returns an object representing a deck of possibilities
    deck = {}
    for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]:
        for suit in ["diams", "spades", "clubs", "hearts"]:
            deck[f"{rank} {suit}"] = 1/self.stats["unknown_cards"]
    return deck

  def configure_hands(self):
    self.stats["unknown_cards"] -= len(self.game["hand"])
    self.stats["num_players"] = len(self.game["other_hands"]) + 1
    for pid in range(self.stats["num_players"]):
      if pid != self.game["pid"]:
        self.hands[pid] = None
      self.hands[pid] = self.possibilities_deck()


  def think(self):
    print("overridden think")
    if self.stats["first_pass"]:
      self.configure_hands()
      self.stats["first_pass"] = False
    pass

  def play(self):
    print("overridden play")


if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()