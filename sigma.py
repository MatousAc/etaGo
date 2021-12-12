# defines a watered-down mcts agent to play Go Fish
from ai import aiBase
from virtual import virtualPlayer
from random import choices, choice, sample, random, shuffle
import help as h

class sigmaGo(aiBase):
  NAME = "sigmaGo"
  BRANCH_FACT = 1
  SIM_DEPTH = 10
  SIM_BREADTH =  1
  PIG1 = {'hands': [['k hearts', '7 spades', '2 diams', 'q clubs', '3 spades', '9 diams', '2 clubs', 'k spades', '2 spades', '2 hearts', 'j clubs'], ['3 clubs', 'a hearts', 'j diams', '4 clubs', '10 clubs', '8 spades', '5 diams'], ['5 spades', '6 spades', '8 hearts', 'a spades', 'k diams', 'q diams', '5 clubs']], 'drawpile': ['9 hearts', '8 clubs', '7 diams', 'k clubs', '9 spades', '10 spades', '4 diams', '6 diams', '4 spades', '6 clubs', '5 hearts', '10 diams', 'a clubs', 'a diams', '8 diams', '7 clubs', '9 clubs', '6 hearts', '4 hearts', '3 hearts', 'q hearts', '7 hearts', 'j spades', 'j hearts', '3 diams', '10 hearts', 'q spades']}

  def __init__(self):
    self.virts = []
    self.store = {}
    super().__init__()

  def configure(self):
    super().configure()
    self.virts = [virtualPlayer(pid) for pid in range(self.stats["num_players"])]
    print(f"self.virts: {self.virts}")

## virtual thinking ##
  def game_conversion(self, pid, hand = None):
    # we have to convert hand, other_hands && pid
    op = self.other_pids(pid)
    game = self.game.copy()
    if hand == None: hand = self.sample_hand(pid)
    game["hand"] = hand
    game["other_hands"] = [[p, self.hand_lengths[p]] for p in op]
    game["p_id"] = pid
    return game

  def think(self):
    super().think()
    # every vp must think along with sigmaGo
    for pid in range(self.stats["num_players"]):
      self.virts[pid].game = self.game_conversion(pid)
      print(f"\nvirtual player #{pid} knows: {self.virts[pid].game}")
      self.virts[pid].think()

  # thanks to Raymond Hettinger @ SO for most of the following f(x):
  def sample_hand(self, pid):
    ihand = self.ihands[pid]
    k = self.hand_lengths[pid]
    population = list(ihand.keys())
    weights = self.avg_prob_replace(pid, ihand.values())
    weights = [100 if h.eq(1, prob) else prob for prob in weights]

    positions = range(len(population))
    indices = []
    while True:
        needed = k - len(indices)
        if not needed:
            break
        for i in choices(positions, weights, k=needed):
            if weights[i]:
                weights[i] = 0.0
                indices.append(i)
    return [population[i] for i in indices]

  def drawpile(self, hands):
    pile = []
    for rank in self.RANKS:
      for suit in self.SUITS:
        # if f"{rank} {suit}" not in known:
        pile.append(f"{rank} {suit}") 
    pile = list(set(pile) - set(sum(hands, [])))
    shuffle(pile)
    print(f"pile: {pile}")
    return pile

  def sample_pig(self):
    # generates a perfect informaition game
    # based on current ihands probabilities
    self.store["cur_ihands"] = self.ihands.copy()
    hands = [[]] * self.stats["num_players"]
    hands[self.id] = self.hand[:]
    self.ihands_zero(hands[self.id], self.other_pids(self.id))

    for pid in self.other_pids(self.id):
      hands[pid] = self.sample_hand(pid)
      self.ihands_zero(hands[pid], self.other_pids(pid))
    
    self.ihands = self.store["cur_ihands"]
    return {
      "hands" : hands,
      "drawpile" : self.drawpile(hands)
    }

## simulating recursively ##
  def get_other_hands(self, p_id, hands):
    final = []
    for i in range(self.stats['num_players']):
        if (i == p_id):
            continue
        final.append([i, hands[i]])
    return final

  def simulate(self, play, pig, asking = None, depth = SIM_DEPTH):
    print(f"\ncurrent pig:  {pig}")
    print(f"\ncurrent play: {play}")
    if depth == self.SIM_DEPTH:
      self.store["cur_virt_ihands"] = [virt.ihands for virt in self.virts]
    depth -= 1
    if asking == None: asking = self.id
    asked = play[0]
    card = play[1]
    asking_last_play = asking

    ## handling current play
    if card in pig["hands"][asked]:
      success = True
      # swap cards
      pig["hands"][asked].remove(card)
      pig["hands"][asking].append(card)
    else: # try draw, move to next player
      success = False
      if pig["drawpile"]:
        drawn_card = pig["drawpile"].pop(0)
        pig["hands"][asking].append(drawn_card)
        if card != drawn_card:
          asking = (asking + 1) % self.stats["num_players"]
      else:
        asking = (asking + 1) % self.stats["num_players"]
    
    ## setting up next play
    if depth != 0:
      # virt rethinking
      for pid in range(self.stats["num_players"]):
        sim_game = self.virts[pid].game.copy()
        sim_game["hand"] = pig["hands"][pid]
        sim_game["other_hands"] = self.get_other_hands(pid, pig["hands"])
        sim_game["last_play"] = {
          "player_asking" : asking_last_play,
          "player_asked" : asked,
          "card_asked_for" : card,
          "success" : success
        }
        self.virts[pid].game = sim_game
        self.virts[pid].think()
      
      print(f"now it's {asking}'s turn")
      virt = self.virts[asking]
      virt.play()
      play = virt.info["player_asked"], virt.info["card_played"]
      return self.simulate(play, pig, asking, depth)
    
    # finishing the simulation branch
    # restore ihands
    for pid in range(self.stats["num_players"]):
      self.virts[pid].ihands = self.store["cur_virt_ihands"][pid]
    return pig

  def fitness(self, hands):
    pass

  def best_plays(self, pig, sample_space):
    plays = [] # choose some best plays
    sample_plays = sample(sample_space, self.BRANCH_FACT)
    for play in sample_plays:
      print(f"\npig before: {pig}")
      fin_pig = self.simulate(play, pig)
      print(f"\npig after:  {fin_pig}")
      print(fin_pig)
    return plays
    

## playing ##
  def play(self):
    nodes = [[pid, card] 
        for pid in self.other_pids(self.id)
      for card in self.valid_plays()]
    # # loop through many possibilities of hands
    best = []
    for _ in range(self.SIM_BREADTH):
      pig = self.sample_pig()
      best += self.best_plays(pig, nodes)
    
    print(f"hand_lengths: {self.hand_lengths}")

    self.info["player_asked"] = choice(self.other_pids(self.id))
    self.info["card_played"] = choice(self.valid_plays())



if __name__ == "__main__":
  player = sigmaGo()