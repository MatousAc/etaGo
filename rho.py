# defines a human agent to play Go Fish
from fisherface import fisher
from random import choice

class rhoGo(fisher):
  def play(self): # chooses a player and card
    self.hand = self.game["hand"]
    self.stats = {"num_players" : len(self.game["other_hands"]) + 1}
    self.info["player_asked"] = choice(self.other_pids(self.id))
    self.info["card_played"] = choice(self.valid_plays())

if __name__ == "__main__":
  player = rhoGo()