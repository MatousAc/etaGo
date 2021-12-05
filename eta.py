# defines a rule-based agent to play Go Fish
import json, help as h
from fisherface import fisher
class etaGo(fisher):
  def __init__(self):
    self.ihands = [] # imagined hands
    self.hand_lengths = []
    self.stats = {
      "num_players"   : 0,
      "unknown_cards"   : 52,
      "first_pass"    : True,
      "match_counts" :[],
      "rank_reqs" : {f"{r}" : 0 # tracks interest in certain sets
      for r in [n for n in range(2, 11)] + ["j", "q", "k", "a"]}
    }
    self.hand = []
    self.last_play = {
      "player_asking" : None,
      "player_asked" : None,
      "card_asked_for" : None,
      "success" : None
    }
    self.matches = {}
    super().__init__()

  def avg_prob(self, pid):
    known_in_hand = 0
    hand = self.ihands[pid]
    for card, prob in hand.items():
      if h.eq(1, prob): known_in_hand += 1
    unknown_in_hand =  self.hand_lengths[pid] - known_in_hand
    return unknown_in_hand/self.stats["unknown_cards"]
  def drew_requested_card(self):
    if self.last_play == {}: return False
    return (self.last_play["player_asking"] == self.game["last_play"]["player_asking"]) and not self.last_play["success"]

  def configure_hands(self): # ihands && stats setup
    self.stats["unknown_cards"] -= len(self.game["hand"])
    self.stats["num_players"] = len(self.game["other_hands"]) + 1
    self.hand_lengths = [self.NUM_DELT] * self.stats["num_players"]
    self.hand = self.game["hand"]
    for pid in range(self.stats["num_players"]):
      if pid != self.id:
        self.ihands.append(self.possibilities_deck())
        for card in self.ihands[pid].keys():
          if (card in self.hand):
            self.ihands[pid][card] = 0
      else: # if it's you:
        self.ihands.append(self.possibilities_deck())
        for card in self.ihands[pid]: # our id - set all our probs
          self.ihands[pid][card] = 1 if (card in self.hand) else 0

  def ihands_zero(self, known_cards, pids): # zeroes prob. of cards in hands
    self.stats["unknown_cards"] -= len(known_cards)
    for pid in pids:
      for card in known_cards:
        self.ihands[pid][card] = 0

  def hand_change(self):
    if len(self.hand) < len(self.game["hand"]): # gained a card
      new_cards = list(set(self.game["hand"]) - set(self.hand))
      self.ihands_zero(new_cards, self.other_pids(self.id))
    else: # if we lost a card
      old_cards = list(set(self.hand) - set(self.game["hand"]))
      self.ihands_zero(old_cards, [self.id])

  def handle_draw(self, pid): # decreases unlikeliness
    self.hand_lengths[pid] += 1
    avg_prob = self.avg_prob(pid)
    for card in self.ihands[pid].keys():
      # we don't affect cards set to 0 on purpose
      if 0 < self.ihands[pid][card] < (avg_prob * 0.9):
        self.ihands[pid][card] += avg_prob / 5
        if (avg_prob * 0.9) < self.ihands[pid][card] < (avg_prob * 1.2):
          self.ihands[pid][card] = self.AVGP # return to avg (?)

  def rank_known(self, rank, pids): # FIXME test if good behaviour
    count = 0
    cards = []
    set = self.set(rank)
    for pid in pids:
      avg_prob = self.avg_prob(pid)
      for card in set:
        culm_prob = 0
        prob = self.ihands[pid][card]
        if h.eq(1, prob):
          count += 1
          cards.append(card)
        elif prob > avg_prob:
          culm_prob += prob
      count += culm_prob // 1
    return count, cards

  def asker_rr(self, rank, num_known, cards_known, pid): # rank recalc - worth reviewing logic!
    # cards_in_hand = []
    set = self.set(rank)
    # for card in set:
    #   if h.eq(1, self.ihands[pid][card]):
    #     cards_in_hand.append(card)
    #     num_known += 1
    for card in set:
      prob = self.ihands[pid][card]
      if (prob == 0): continue
      elif (prob == 1): return # can't say anthing else about them(?)
      elif card in cards_known: # if someone else has card (useless?)
        self.ihands[pid][card] = 0
      elif prob == self.AVGP: # if we have no info on it yet
        self.ihands[pid][card] = 1 / (4 - num_known)

  def ihand_doesnt_have(self, absent_card, pid):
    culm_prob = 0
    cards_above_avg = []
    for card in self.set(absent_card.split()[0]):
      culm_prob += self.ihands[pid][card]
      cards_above_avg.append(card)
    if h.eq(1, culm_prob): # if pid has at least one of the rank
      for card in cards_above_avg: # make other cards more certain
        self.ihands[pid][card] = 1 / len(cards_above_avg)
    self.ihands[pid][card] = 0 # they don't have *this* card though
  
  def request_made(self): # someone asked someone for a card
    if self.game["last_play"] == {}: return
    asking_pid = self.game["last_play"]["player_asking"]
    asked_pid = self.game["last_play"]["player_asked"]
    if self.drew_requested_card():
      card = self.last_play["card_asked_for"] # card drawn last play
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.ihands[asking_pid][card] = 1 # set to known
      self.hand_lengths[asking_pid] += 1
    old_asker = self.last_play["player_asking"]
    if (old_asker != asking_pid) and (old_asker != self.id):
      self.handle_draw(old_asker)
    
    self.last_play = self.game["last_play"] # otherwise
    card = self.last_play["card_asked_for"]
    [rank, suit] = card.split()
    self.stats["rank_reqs"][rank] += 1 # set is more popular
    
    if asking_pid == self.id:
      # you've given away that you're interested in this rank:
      self.stats["rank_reqs"][rank] -= 6
      if not self.last_play["success"]: 
        self.ihand_doesnt_have(card, asked_pid)
      return

    num_known, cards_known = self.rank_known(rank, self.other_pids(asking_pid))
    self.asker_rr(rank, num_known, cards_known, asking_pid)
    self.ihands[asking_pid][card] /= 10 # probably not asking for own card
    if self.last_play["success"]:
      self.ihands[asking_pid][card] = 1
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.hand_lengths[asked_pid] -= 1
    else: # remove that card from consideration
      self.ihand_doesnt_have(card, asked_pid)
  
  def match_made(self):
    for match in self.game["matches"]:
      if match not in self.matches:
        [pid, rank] = match # found new match
        break
    self.matches == self.game["matches"]
    self.stats["match_counts"][pid] += 1
    self.hand_lengths[pid] -= 4
    self.ihands_zero(self.set(rank), range(self.stats["num_players"]))

  def think(self):
    if self.stats["first_pass"]:
      self.stats["first_pass"] = False
      self.configure_hands()
      self.stats["match_counts"] = [0] * self.stats["num_players"]
      return # we assume no more thinking
    # here we change up all the probabilities based on events
    if self.hand != self.game["hand"]: self.hand_change() # useless??
    if self.last_play != self.game["last_play"]: self.request_made()
    if self.matches != self.game["matches"]: self.match_made()

  def play(self):
    print("etaGo playing . . .")

if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()