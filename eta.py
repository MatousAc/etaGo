# defines a rule-based agent to play Go Fish
import json, help as h
from random import choice
from states import state
from fisherface import fisher
class etaGo(fisher):
  NAME = "etaGo"
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
    self.last_play = {
      "player_asking" : None,
      "player_asked" : None,
      "card_asked_for" : None,
      "success" : None
    }
    self.matches = []
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
  def hand_exchange(self, asking, asked):
    self.hand_lengths[asking] += 1
    self.hand_lengths[asked] -= 1
  def success_prob_shift(self, asking, asked, card):
      self.ihands[asking][card] = 1 # asker has it
      if self.ihands[asked][card] != 1:
        self.stats["unknown_cards"] -= 1 # becomes known
      self.ihands[asked][card] = 0 # asked def. doesn't have it
  def print_stats(self):
    print(f"_____________________I'm {self.NAME} and I know_____________________")
    for pid in self.other_pids(self.id):
      has, has_not, might_have = [], [], {}
      for card, prob in self.ihands[pid].items():
        if h.eq(1, prob): has.append(card)
        elif h.eq(0, prob): has_not.append(card)
        elif not h.eq(-1, prob): might_have[card] = prob
      print(f"----Player {pid}----")
      print(f"-has: ")
      print(*has)
      print(f"-maybe has:")
      for card, prob in might_have.items():
        print(f"{card}:{h.truncate(prob, 4)}")
      print("")
      print(f"-and doesn't have: ")
      print(*has_not)

    print(f"# unknown cards: {self.stats['unknown_cards']}")
    print(f"# rank reqs: {self.stats['rank_reqs']}")
    print(f"# match counts: {self.stats['match_counts']}")

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

## thinking ##
  def ihands_zero(self, known_cards, pids): # zeroes prob. of cards in hands
    for pid in pids:
      for card in known_cards:
        self.ihands[pid][card] = 0

  def hand_change(self):
    if len(self.hand) < len(self.game["hand"]): # gained a card
      new_cards = list(set(self.game["hand"]) - set(self.hand))
      self.ihands_zero(new_cards, self.other_pids(self.id))
      for card in new_cards:
        self.ihands[self.id][card] = 1
    else: # if we lost a card
      old_cards = list(set(self.hand) - set(self.game["hand"]))
      self.ihands_zero(old_cards, [self.id])

  def handle_draw(self, pid): # increases likeliness
    if sum(self.hand_lengths) >= 52: return # no drawpile
    self.hand_lengths[pid] += 1
    avg_prob = self.avg_prob(pid)
    for card in self.ihands[pid].keys():
      # we don't affect cards set to 0 on purpose
      if 0 < self.ihands[pid][card] < (avg_prob * 0.9):
        self.ihands[pid][card] += avg_prob / 15
        if (avg_prob * 0.9) < self.ihands[pid][card] < (avg_prob * 1.2):
          self.ihands[pid][card] = self.AVGP # return to avg (?)

  def rank_known(self, rank, pids):
    count = 0
    cards_known = []
    set = self.set(rank)
    for pid in pids:
      avg_prob = self.avg_prob(pid)
      for card in set:
        culm_prob = 0
        prob = self.ihands[pid][card]
        if h.eq(1, prob):
          count += 1
          cards_known.append(card)
        elif prob > avg_prob:
          culm_prob += prob
      count += culm_prob // 1
    last = self.last_play["card_asked_for"]
    if (self.last_play["success"]) and (last not in cards_known):
      count += 1 # one card is already missing
      cards_known.append(self.last_play["card_asked_for"])
    return count, cards_known

  def asker_rr(self, rank, num_known, cards_known, pid): # rank recalc FIXME?
    set = self.set(rank)
    for card in set:
      prob = self.ihands[pid][card]
      if (prob == 0): continue
      elif (prob == 1): return # can't say anthing else about them
      elif card in cards_known: # if someone else has card (useless?)
        self.ihands[pid][card] = 0
      elif prob == self.AVGP: # if we have no info on it yet
        self.ihands[pid][card] = 1 / (4 - num_known)

  def ihand_has_not(self, absent_card, pid, new_prob = 0):
    culm_prob = 0
    cards_above_avg = []
    avg_prob = self.avg_prob(pid)
    for card in self.set(absent_card.split()[0]):
      prob = self.ihands[pid][card]
      if avg_prob < prob < .95:
        culm_prob += prob
        if card != absent_card: cards_above_avg.append(card)
    if .95 < culm_prob: # if pid has at least one of the rank
      for card in cards_above_avg: # make other cards more certain
        self.ihands[pid][card] = 1 / len(cards_above_avg)
    self.ihands[pid][absent_card] = new_prob # don't have abs_card tho
  
  def request_made(self): # someone asked someone for a card
    if self.game["last_play"] == {}: return
    asking_pid = self.game["last_play"]["player_asking"]
    asked_pid = self.game["last_play"]["player_asked"]
    if self.drew_requested_card():
      card = self.last_play["card_asked_for"] # card drawn last play
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.ihands[asking_pid][card] = 1 # set to known
      self.hand_lengths[asking_pid] += 1
    
    self.last_play = self.game["last_play"] # otherwise
    card = self.last_play["card_asked_for"]
    rank, suit = card.split()
    self.stats["rank_reqs"][rank] += 1 # set is more popular
    
    if asking_pid == self.id:
      # you've given away that you're interested in this rank:
      self.stats["rank_reqs"][rank] -= 6
      if self.last_play["success"]:
        self.ihands[self.id][card] = 1
        if self.ihands[asked_pid][card] != 1:
          self.stats["unknown_cards"] -= 1
        self.ihands[asked_pid][card] = 0
        self.hand_exchange(self.id, asked_pid)
        self.hand.append(card)
      else:
        self.ihand_has_not(card, asked_pid)
        self.hand_lengths[self.id] += 1
      return

    num_known, cards_known = self.rank_known(rank, self.other_pids(asking_pid))
    self.asker_rr(rank, num_known, cards_known, asking_pid)
    self.ihand_has_not(card, asking_pid, self.UNLIKELYP) # prob. not asking for own card
    if self.last_play["success"]:
      self.success_prob_shift(asking_pid, asked_pid, card)
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.hand_exchange(asking_pid, asked_pid)
      if card in self.hand: self.hand.remove(card)
    else: # remove card from consideration
      self.ihand_has_not(card, asked_pid)
      self.handle_draw(asking_pid)

  def czech_for_win(self):
    for match_count in self.stats["match_counts"]:
      if match_count >= 2:
        pid = self.stats['match_counts'].index(match_count)
        if pid == self.id:
          self.won()
        else:
          self.lost(pid)

  def match_made(self):
    new_matches = []
    for match in self.game["matches"]:
      if match not in self.matches:
        new_matches.append(match) # found new match
    # pull all of the card out of the game
    for pid, rank in new_matches:
      self.stats["match_counts"][pid] += 1
      self.hand_lengths[pid] -= 4
      self.ihands_zero(self.set(rank), range(self.stats["num_players"]))
      # take out of your hand (nesc)
      if self.id == pid:
        for card in self.set(rank):
          if card in self.hand: self.hand.remove(card)
    self.matches += new_matches
    self.czech_for_win()

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
    # if self.game["state"] == state.WAITING_FOR_OTHERS: self.print_stats()

  ## playing ##
  
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
    if not best: # choose randomly if all avg prob
      print("random choice")
      return [[pid, card] 
        for card in choices 
        for pid in self.other_pids(self.id)]
    else: return best

  def interest_filter(self, options):
    ranks = {} # what are my interests?
    rank = ""
    for card in self.hand:
      rank = card.split()[0]
      if rank in ranks.keys():
        ranks[rank] += 1
      else:
        ranks[rank] = 1
    interest_ranks = []
    interest_freq = 0
    for r, freq in ranks.items():
      if freq > interest_freq:
        interest_freq = freq
        interest_ranks = [r]
      elif freq == interest_freq:
        interest_ranks.append(r)
    # out of my options, which am i most interested in?
    temp = []
    for pid, card in options:
      if card.split()[0] in interest_ranks:
        temp.append([pid, card])
    return temp if temp else options

  def play(self): # playing w/ strategy
    # log
    # self.print_stats()
    choices = self.valid_plays()
    # print(f"hand: {self.hand}\nchoices: {choices}")
    # choose highest probabilities of cards and players
    strategy = self.prob_filter(choices)
    # certainty first strategy FIXME

    # print(f"highest probs: {strategy}")
    # choose the rank you need most FIXME we don't want this
    strategy = self.interest_filter(strategy)
    # print(f"highest interest: {strategy}")
    # get secrecy strategy FIXME

    # ask them for that card
    pid, card = choice(strategy)
    # set
    self.info["player_asked"] = pid
    self.info["card_played"] = card

    print(f"I am asking player {self.info['player_asked']}",
      f" for {self.info['card_played']}")

if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()