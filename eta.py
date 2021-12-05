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
        self.ihands.append(self.possibilities_deck())
        for card in self.ihands[pid].keys():
          if (card in self.game["hand"]):
            self.ihands[pid][card] = 0
      else:
        self.ihands.append(self.possibilities_deck())
        for card in self.ihands[pid]: # our id - set all our probs
          self.ihands[pid][card] = 1 if (card in self.hand) else 0

    h.print_dict_list(self.ihands)
  def ihands_zero(self, known_cards, pids): # zeroes prob. of cards in hands
    self.stats["unknown_card"] -= len(known_cards)
    for pid in pids:
      for card in self.ihands[pid].keys():
        if (card in known_cards): self.ihands[pid][card] = 0
  def num_of_rank_known(self, rank, pids):
    count = 0
    for pid in pids:
      avg_prob = self.avg_prob(self.ihands[pid])
      for card, prob in self.ihands[pid].items():
        culm_prob = 0
        if (card.split()[0] == rank):
          if h.eq(1, prob):
            count += 1
          elif prob > avg_prob:
            culm_prob += prob
      count += culm_prob // 1 # FIXME - this probably doesn't work
    return count
  def hand_change(self): # if our hand changed
    if len(self.hand) < len(self.game["hand"]):
      new_cards = [] # gained a card
      for card in self.game["hand"]:
        if card not in self.hand:
          new_cards.append(card)
      self.ihands_zero(new_cards, self.other_pids(self.ID))
    else: # if we lost a card
      old_cards = [] # gained a card
      for card in self.hand:
        if card not in self.game["hand"]:
          old_cards.append(card)
      self.ihands_zero(old_cards, [self.ID])

  def request_made(self): # someone asked someone for a card
    self.last_play = self.game["last_play"]
    rank, suit = self.last_play["card_asked_for"].split()
    num_in_hands = self.num_of_rank_known(rank, 
      self.other_pids(self.last_play["player_asking"]))
    
    

  def think(self):
    print("overridden think")
    if self.stats["first_pass"]:
      self.configure_hands()
      self.stats["first_pass"] = False
    # here we change up all the probabilities based on events
    if (self.hand != self.game["hand"]): self.hand_change()
    if (self.last_play != self.game["last_play"]): self.request_made()


  def play(self):
    print("overridden play")

if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()