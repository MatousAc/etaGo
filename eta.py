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
    self.hand = []
    self.last_play = {}
    super().__init__()

  def avg_prob(self, cards_in_hand):
    return cards_in_hand/self.stats["unknown_cards"]

  def configure_hands(self): # imaginary hands setup
    self.stats["unknown_cards"] -= len(self.game["hand"])
    self.stats["num_players"] = len(self.game["other_hands"]) + 1
    for pid in range(self.stats["num_players"]):
      if pid != self.game["p_id"]: # if not your own id
        self.ihands.append(self.possibilities_deck(self.NUM_DELT))
        for card in self.ihands[pid].keys():
          if (card in self.game["hand"]):
            self.ihands[pid][card] = 0
      else:
        self.ihands.append(None)
    h.print_dict_list(self.ihands)

  def ihands_zero(self, known_cards):
    self.stats["unknown_card"] -= len(known_cards)
    for hand in self.ihands:
      for card in hand.keys():
        if (card in known_cards): hand[card] = 0

  # def prob_recalc(self):
  #   for hand in self.ihands:
  #     avgp = self.avg_prob(len(hand))
  #     for card in hand.keys():
  #       if h.eq(hand[card], 1):


  def hand_change(self): # if we gained a card
    if len(self.hand) >= len(self.game["hand"]): return
    new_cards = []
    for card in self.game["hand"]:
      if card not in self.hand:
        new_cards.append(card)
    self.ihand_zero(new_cards)
    # self.prob_recalc()

  def think(self):
    print("overridden think")
    if self.stats["first_pass"]:
      self.configure_hands()
      self.stats["first_pass"] = False
    # here we change up all the probabilities based on events
    if (self.hand != self.game["hand"]): self.hand_change()
    if (self.last_play !=)

  def play(self):
    print("overridden play")


if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()