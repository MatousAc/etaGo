# defines a rule-based agent to play Go Fish
import json, help as h
from random import choice, random
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
        for r in [n for n in range(2, 11)] + ["j", "q", "k", "a"]},
      "certain_cards" : []
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
      if not h.eq(1, self.ihands[asked][card]):
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
    self.hand = self.game["hand"] # brute force update

  def handle_draw(self, pid): # increases likeliness
    if sum(self.hand_lengths) >= 52: return # no drawpile
    self.hand_lengths[pid] += 1
    avg_prob = self.avg_prob(pid)
    for card in self.ihands[pid].keys():
      # we don't affect cards set to 0 on purpose
      if 0 < self.ihands[pid][card] < (avg_prob * 0.9):
        self.ihands[pid][card] += avg_prob / 15
        if (avg_prob * 0.8) < self.ihands[pid][card] < (avg_prob * 1.3):
          self.ihands[pid][card] = self.AVGP # return to avg (?)
    if pid == self.id: # add the card to your hand
      self.hand == self.game["hand"]

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

  def ihand_unlikely(self, absent_card, pid, new_prob = 1e-7):
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
  
  def request_made(self): 
    if self.game["last_play"] == {}: return
    # if requested card was drawn:
    asking_pid = self.game["last_play"]["player_asking"]
    asked_pid = self.game["last_play"]["player_asked"]
    if self.drew_requested_card():
      card = self.last_play["card_asked_for"] # card drawn last play
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.ihands[asking_pid][card] = 1 # set to known
      self.stats["unknown_cards"] -= 1
      self.hand_lengths[asking_pid] += 1
    
    self.last_play = self.game["last_play"] # otherwise
    card = self.game["last_play"]["card_asked_for"]
    rank = card.split()[0]
    self.stats["rank_reqs"][rank] += 1 # set is more popular
    
    if asking_pid == self.id:
      # you've given away that you're interested in this rank:
      self.stats["rank_reqs"][rank] -= 7
      if self.last_play["success"]:
        self.success_prob_shift(self.id, asked_pid, card)
        self.hand_exchange(self.id, asked_pid)
      else:
        self.ihand_unlikely(card, asked_pid)
        self.hand_lengths[self.id] += 1
      return

    num_known, cards_known = self.rank_known(rank, self.other_pids(asking_pid))
    self.asker_rr(rank, num_known, cards_known, asking_pid)
    self.ihand_unlikely(card, asking_pid, self.UNLIKELYP) # prob. not asking for own card
    if self.last_play["success"]:
      self.success_prob_shift(asking_pid, asked_pid, card)
      self.ihands_zero([card], self.other_pids(asking_pid))
      self.hand_exchange(asking_pid, asked_pid)
    else: # remove card from consideration
      self.ihand_unlikely(card, asked_pid)
      self.handle_draw(asking_pid)

  def czech_for_win(self):
    for match_count in self.stats["match_counts"]:
      if match_count >= self.MATCHES_TO_WIN:
        pid = self.stats['match_counts'].index(match_count)
        if pid == self.id:
          self.won()
        else:
          self.lost(pid)
        self.end_game()

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
    if self.hand != self.game["hand"]:
      self.hand = self.game["hand"]
      if not self.hand:
        self.out()
        return
    # thinking
    if self.last_play != self.game["last_play"]: self.request_made()
    if self.matches != self.game["matches"]: self.match_made()
    if self.game["state"] == state.WAITING_FOR_OTHERS: self.print_stats()

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

  def play(self): # playing w/ strategy
    # filters output choices using various strategies
    # self.print_stats()
    choices = self.valid_plays()
    # print(f"hand: {self.hand}\nchoices: {choices}")
    strategy = self.prob_filter(choices)
    strategy = self.entropy_filter(strategy)
    # print(f"highest probs: {strategy}")
    # get secrecy strategy FIXME
    strategy = self.interest_filter(strategy)
    strategy = self.info_filter(strategy)
    # print(f"highest interest: {strategy}")
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