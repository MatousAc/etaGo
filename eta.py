# defines a rule-based agent to play Go Fish
import json, help as h
from fisherface import fisher
class etaGo(fisher):
  def __init__(self):
    self.ihands = [] # imagined hands
    self.stats = {
      "num_players"   : 0,
      "unknown_cards"   : 52,
      "first_pass"    : True
    }
    super().__init__()

  def possibilities_deck(self, cards_in_hand):
    deck = {} # returns an object representing a deck of possibilities
    for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]:
        for suit in ["diams", "spades", "clubs", "hearts"]:
            deck[f"{rank} {suit}"] = cards_in_hand/self.stats["unknown_cards"]
    return deck

  def avg_prob(self, cards_in_hand):
    return cards_in_hand/self.stats["unknown_cards"]

  def configure_hands(self): # imaginary hands setup
    self.stats["unknown_cards"] -= len(self.game["hand"])
    self.stats["num_players"] = len(self.game["other_hands"]) + 1
    for pid in range(self.stats["num_players"]):
      if pid != self.game["p_id"]: # if not your own id
        self.ihands.append(self.possibilities_deck(self.NUM_DELT))
        for card, prob in self.ihands[pid].items():
          if (card in self.game["hand"]):
            self.ihands[pid][card] = 0
      else:
        self.ihands.append(None)

  def think(self):
    print("overridden think")
    if self.stats["first_pass"]:
      self.configure_hands()
      self.stats["first_pass"] = False
    # here we change up all the probabilities based on events


  def play(self):
    print("overridden play")


if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()