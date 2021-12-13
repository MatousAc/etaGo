# defines an adapted mcts agent to play Go Fish
from ai import aiBase
from virtual import virtualPlayer
from random import choices, choice, sample, random, shuffle
from statistics import median
import help as h

class sigmaGo(aiBase):
  NAME = "sigmaGo"
  BRANCH_FACT = 12
  SIM_DEPTH = 10
  SIM_BREADTH = 150
  JOIN_STR = "$"

  def __init__(self):
    self.virts = []
    self.store = {}
    super().__init__()

  def configure(self):
    super().configure()
    self.virts = [virtualPlayer(pid) for pid in range(self.stats["num_players"])]

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
      self.virts[pid].think()

  # thanks to Raymond Hettinger @ SO for most of the following f(x):
  def sample_hand(self, pid):
    ihand = self.ihands[pid]
    population = list(ihand.keys())
    weights = self.avg_prob_replace(pid, ihand.values())
    weights = [10 if h.eq(1, prob) else prob for prob in weights]
    nonzero = len([w for w in weights if not h.eq(0, w)])
    # print(f"\npop = {population}\nweights = {weights}")

    positions = [x for x in range(len(population))]
    indices = []
    while (len(indices) < self.hand_lengths[pid]) and (nonzero):
        [c] = choices(positions, weights, k=1)
        # print(f"\nc {c}")
        if c not in indices:
          weights[c] = 0.000001
          nonzero -= 1
          # print(f"chose {population[c]}")
          # print(f"\nweights {weights}")
          indices.append(c)
    return [population[i] for i in indices]

  def drawpile(self, hands):
    pile = []
    for rank in self.RANKS:
      for suit in self.SUITS:
        # if f"{rank} {suit}" not in known:
        pile.append(f"{rank} {suit}") 
    pile = list(set(pile) - set(sum(hands, [])))
    shuffle(pile)
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
    if depth == self.SIM_DEPTH:
      self.store["cur_virt_ihands"] = [virt.ihands for virt in self.virts]
      # print("\n\n\n\n\nfirst round")
    # print(f"\ncurrent pig:  {pig}")
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
    if (depth != 0):
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
        if not self.virts[pid].valid_plays(): return pig
      
      # print(f"now it's {asking}'s turn")
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
    fitness = 0
    # reward/punishment based on card number
    prev_other = sum(self.hand_lengths) - self.hand_lengths[self.id]
    curr_other = sum([len(hand) for hand in hands])
    fitness -= (curr_other - prev_other)
    fitness += 3 * (self.hand_lengths[self.id] - len(hands[self.id]))
    for pid in range(self.stats["num_players"]):
      # reward/punishment based on new sets
      new_sets = 0
      suit_hand = [card.split()[0] for card in hands[pid]]
      rank_count = {f"{r}" : 0 for r in [n for n in range(2, 11)] + ["j", "q", "k", "a"]}
      for card in hands[pid]:
        rank = card.split()[0]
        rank_count[rank] += 1
        if rank_count[rank] == 4: new_sets += 1
      if pid == self.id:
        fitness += 11 * new_sets
      else:
        fitness -= 8 * new_sets
    return fitness

  def best_plays(self, pig, sample_space):
    play_fits = {} # see where different actions take you
    sample_plays = sample(sample_space, self.BRANCH_FACT)
    for play in sample_plays:
      # print(f"\npig before: {pig}")
      fin_pig = self.simulate(play, pig)
      # print(f"\npig after:  {fin_pig}")
      play = sample_plays.index(play) #self.JOIN_STR.join(map(str, play))
      play_fits[play] = self.fitness(fin_pig["hands"])
    
    # return the upper quartile
    med = median(play_fits.values())
    mx = max(play_fits.values())
    q3 = (med + mx) / 2 # FIXME - return max and anything reasonably close?
    plays = [sample_plays[play]
      for play in play_fits.keys() if play_fits[play] >= q3]
    return plays
    

## playing ##
  def play(self):
    nodes = [[pid, card] 
        for pid in self.other_pids(self.id)
      for card in self.valid_plays()]
    # loop through many possibilities of hands
    best = []
    for _ in range(self.SIM_BREADTH):
      pig = self.sample_pig()
      best += self.best_plays(pig, nodes)
    
    pid, card = choice(best)
    self.info["player_asked"] = pid # int(pid)
    self.info["card_played"] = card

if __name__ == "__main__":
  player = sigmaGo()