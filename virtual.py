# defines a player that never connects to a server
from eta import etaGo
from random import choices, choice, sample, random, shuffle
import help as h

class virtualPlayer(etaGo):
  NAME = "virtualPlayer"
  def __init__(self, id):
    self.ihands = [] # imagined hands
    self.hand_lengths = []
    self.stats = {
      "num_players"   : 0,
      "unknown_cards"   : 52,
      "first_pass"    : True,
      "match_counts" :[],
      "rank_reqs" : {f"{r}" : 0 # tracks interest in certain sets
        for r in [n for n in range(2, 11)] + ["j", "q", "k", "a"]},
      "certain_cards" : []
    }
    self.last_play = {
      "player_asking" : None,
      "player_asked" : None,
      "card_asked_for" : None,
      "success" : None
    }
    self.info, self.game, self.hand, self.matches = {}, {}, [], []
    self.pause, self.id = 0, id

  def out(self):
    pass
# consider recalculating with very different hand? FIXME
  def think(self):
    print(f"\n{self.id} is thinking\n")
    super().think()


if __name__ == "__main__":
  virtualPlayer()