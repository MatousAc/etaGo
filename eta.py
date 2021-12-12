# defines a rule-based agent to play Go Fish
from time import sleep
from random import choice, random
from ai import aiBase
import help as h
class etaGo(aiBase):
  NAME = "etaGo"
## playing ##
  def gather_certain_cards(self):
    self.stats["known_cards"] = []
    for pid in self.other_pids():
      for card, prob in self.ihands[pid].items():
        if h.eq(1, prob):
          self.stats["known_cards"].append(card)

  def random_play(self, choices):
    # ask player w/ most cards
    other_hand_lengths = self.hand_lengths[:self.id] + self.hand_lengths[self.id + 1:]
    pid = self.hand_lengths.index(max(other_hand_lengths))
    res = []
    avg_prob = self.avg_prob(pid)
    for card in choices:
      prob = self.ihands[pid][card]
      if (prob == -1) or (prob > avg_prob):
        res.append([pid, card])
    return res if res else [
      [pid, card] 
        for pid in self.other_pids(self.id)
      for card in choices]

  def prob_filter(self, choices):
    best = []
    best_prob = self.avg_prob(0)
    # choose highest prob
    for pid in self.other_pids(self.id):
      avg_prob = self.avg_prob(pid)
      if avg_prob > best_prob: best_prob = avg_prob
      for card in choices:
        prob = self.ihands[pid][card]
        if prob > best_prob:
          best = [[pid, card]]
          best_prob = prob
        elif h.eq(prob, best_prob):
          best.append([pid, card])
    if not best: # choose randomly of all avg prob
      return self.random_play(choices)
    else: return best

  def interest_ranks(self):
    ranks = {} # what are my interests?
    rank = ""
    for card in self.hand:
      rank = card.split()[0]
      if rank in ranks.keys():
        ranks[rank] += 1
      else:
        ranks[rank] = 1
    tir = [] # top interest ranks
    interest_freq = 0
    for r, freq in ranks.items():
      if freq > interest_freq:
        interest_freq = freq
        tir = [r]
      elif freq == interest_freq:
        tir.append(r)
    return interest_freq, tir

  def interest_filter(self, options):
    # we want to do this 1/2 of the time
    if random() % 2 == 0: return options
    _, best_ranks = self.interest_ranks()
    temp = [] # filter by options
    for pid, card in options:
      if card.split()[0] in best_ranks:
        temp.append([pid, card])
    return temp if temp else options

  def entropy_filter(self, options):
    # we want to do this 2/3 of the time
    if random() % 3 != 0: return options
    remove = [] # ranks to remove
    temp = options[:]
    # get cards we're interested in
    freq, ranks = self.interest_ranks()
    # calc cards we know for certain
    if freq > 2: self.gather_certain_cards()
    # chose what is too uncertain to ask for
    if freq == 2:
      for rank in ranks:
        known_freq = 0
        for card in self.stats["certain_cards"]:
          if card.split()[0] == rank: known_freq += 1
        if known_freq < 3:
          remove.append(rank)
    if freq == 3:
      for rank in ranks:
        known_freq = 0
        for card in self.stats["certain_cards"]:
          if card.split()[0] == rank: known_freq += 1
        if known_freq < 4:
          remove.append(rank)
    # remove them if necessary
    for t in temp:
      card = t[1]
      if card.split()[0] in remove:
        temp.remove(t)
    return temp if temp else options

  def info_filter(self, options):
    # we want to do this 1/2 of the time
    if random() % 2 == 0: return options
    rr = self.stats["rank_reqs"]
    smallest = min(rr.values())
    lowest = [key for key in rr if rr[key] == smallest]
    temp = [] # filter by options
    for pid, card in options:
      if card.split()[0] in lowest:
        temp.append([pid, card])
    return temp if temp else options

  def play(self):
    sleep(self.pause)
    # filters output choices using various strategies
    choices = self.valid_plays()
    strategy = self.prob_filter(choices)
    strategy = self.entropy_filter(strategy)
    strategy = self.interest_filter(strategy)
    strategy = self.info_filter(strategy)
    # ask them for that card
    pid, card = choice(strategy)
    
    self.info["player_asked"] = pid
    self.info["card_played"] = card
    # print(f"I am asking player {self.info['player_asked']}",
      # f" for {self.info['card_played']}")
    print(f"{self.id} is asking player {self.info['player_asked']}",
      f" for {self.info['card_played']}")

if __name__ == "__main__":
  # print(
  #   " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  # )
  player = etaGo()