# this file defines the structure of a fisher agent
from states import state
from uuid import uuid4
import asyncio as aio, websockets as ws
import random, json, time

class fisher:
  # static
  HOST = "10.14.2.1" #127.0.0.1"
  PORT = 10000 #4444
  # use this to ssh:
  # ssh -p 2224 ac@10.14.2.1
  NUM_DELT = 7
  AVGP = -1 # represents "average probability"
  UNLIKELYP = 5e-5
  MATCHES_TO_WIN = 7
  SUITS = ["diams", "spades", "clubs", "hearts"]

  def __init__(self):
    self.uuid = uuid4() # generate uuid
    self.id = -1
    self.connections = 0
    self.info = { # keeps track of client info
      "state"     : state.DISCONNECTED,
      "am_ready"  : False
    }
    self.hand = []
    self.game = {} # game state
    # make connection
    aio.run(self.connect())
  # logic - meant to be overridden
  def think(self): # obtains and organizes info
    pass
  def play(self): # chooses a player and card
    pass
  def end_game(self):
    self.info["state"] = state.END_OF_GAME
  def out(self):
    print("          _______             _        _______  _______  _______  _ \n|\     /|(  ___  )|\     /|  ( \      (  ___  )(  ____ \(  ____ \( )\n( \   / )| (   ) || )   ( |  | (      | (   ) || (    \/| (    \/| |\n \ (_) / | |   | || |   | |  | |      | |   | || (_____ | (__    | |\n  \   /  | |   | || |   | |  | |      | |   | |(_____  )|  __)   | |\n   ) (   | |   | || |   | |  | |      | |   | |      ) || (      (_)\n   | |   | (___) || (___) |  | (____/\| (___) |/\____) || (____/\ _ \n   \_/   (_______)(_______)  (_______/(_______)\_______)(_______/(_)\n")
    print("no more cards")
    self.info["state"] = state.END_OF_GAME
  
  async def send(self): # sends info
    await self.sock.send(json.dumps(self.info))
  async def set_sock(self):
    self.sock = await ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")

  async def connect(self):
    await self.set_sock()
    self.info["state"] = state.CONNECTED
    input("press enter to play")
    self.info["am_ready"] = True
    await self.loop()
    # try:
    #   await self.loop()
    # except Exception as e:
    #   if self.connections > 40: return # give up
    #   print(f"exception caught:\n{e}")
    #   self.connections += 1
    #   await self.set_sock()
    #   self.info["state"] = state.CONNECTED
    #   self.info["am_ready"] = True
    #   await self.send() # in case we got stuck on send
    #   await self.loop()

  async def loop(self):
    while True:
      await self.sock.send("PING")
      update = json.loads(await self.sock.recv())
      
      if (update != self.game):
        self.game = update
        if self.id == -1: self.id = self.game["p_id"] # set id
        print(f"\n\n\nself.game['hand']: {self.game['hand']}")
        self.info["state"] = self.game["state"]
        # handling states
        state = self.game["state"]
        if state == 1: # restart
          await self.send()
        elif (state == 2): # revert
          await self.send()
          # self.info["am_ready"] = False
          # self.info["state"] = state.CONNECTED
          # await self.send()
          # input("press enter to signal that you are ready to play") # blocks until ready
          # self.info["am_ready"] = True          
        elif state in [3,4]: # update info
          self.think()
        elif state == 5: # play
          time.sleep(0.1)
          self.think()
          if self.info["state"] == 6: break
          self.play()
          await self.send()
        elif state == 6: # end
          break
        else:
          print("invalid or disconnected state returned")
      time.sleep(1)

  def possibilities_deck(self):
    deck = {} # returns an object representing a deck of possibilities
    for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]:
        for suit in ["diams", "spades", "clubs", "hearts"]:
          deck[f"{rank} {suit}"] = self.AVGP # repr by -1 val
    return deck
  def avg_prob(self, cards_in_hand):
    pass
  def other_pids(self, pid = -1):
    ids = [id for id in range(0, self.stats["num_players"])]
    if pid != -1: ids.remove(pid)
    return ids
  def set(self, rank):
    return [f"{rank} {suit}" for suit in self.SUITS]
  def valid_plays(self):
    plays = []
    for card in self.hand:
      if card not in plays: 
        plays += self.set(card.split()[0])
        plays.remove(card)
      else: plays.remove(card)
    return plays
  def won(self):
    print("          _______                      _______  _        _ \n|\     /|(  ___  )|\     /|  |\     /|(  ___  )( (    /|( )\n( \   / )| (   ) || )   ( |  | )   ( || (   ) ||  \  ( || |\n \ (_) / | |   | || |   | |  | | _ | || |   | ||   \ | || |\n  \   /  | |   | || |   | |  | |( )| || |   | || (\ \) || |\n   ) (   | |   | || |   | |  | || || || |   | || | \   |(_)\n   | |   | (___) || (___) |  | () () || (___) || )  \  | _ \n   \_/   (_______)(_______)  (_______)(_______)|/    )_)(_)\n")
  def lost(self, winner):
    pass
    print("          _______             _        _______  _______  _______  _ \n|\     /|(  ___  )|\     /|  ( \      (  ___  )(  ____ \(  ____ \( )\n( \   / )| (   ) || )   ( |  | (      | (   ) || (    \/| (    \/| |\n \ (_) / | |   | || |   | |  | |      | |   | || (_____ | (__    | |\n  \   /  | |   | || |   | |  | |      | |   | |(_____  )|  __)   | |\n   ) (   | |   | || |   | |  | |      | |   | |      ) || (      (_)\n   | |   | (___) || (___) |  | (____/\| (___) |/\____) || (____/\ _ \n   \_/   (_______)(_______)  (_______/(_______)\_______)(_______/(_)\n")
    print(f"Player {winner} won!")

  # destructor
  def __del__(self):
    # self.sock.close()
    pass

# testing
if __name__ == "__main__":
  player = fisher()