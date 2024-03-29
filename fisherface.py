# this file defines the basics of how an agent will connect
# to the server and handles the game states
from states import state
from uuid import uuid4
from time import sleep
import asyncio as aio, websockets as ws
import json

# use this to ssh:
# ssh -p 2224 ac@10.14.2.1
class fisher:
  # static
  # HOST = "10.14.2.1"
  # PORT = 10000
  HOST = "127.0.0.1"
  PORT = 4444
  NUM_DELT = 7
  MATCHES_TO_WIN = 4
  SUITS = ["diams", "spades", "clubs", "hearts"]
  RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
  
  def __init__(self):
    self.uuid = uuid4() # generate uuid
    self.gamePlayed = False
    self.is_winner = False
    self.id = -1
    self.connections = 0
    self.info = { # keeps track of client info
      "state"     : state.DISCONNECTED,
      "am_ready"  : False
    }
    self.hand = []
    self.game = {} # game state
    self.pause = 0 # 5 - int(input("enter speed (0-5): "))
    # make connection
    aio.run(self.connect())

  # logic - meant to be overridden
  def think(self): # obtains and organizes info
    pass
  def play(self): # chooses a player and card
    pass
  def end_game(self):
    self.info["state"] = state.CONNECTED
    self.gamePlayed = True

  def out(self):
    print("          _______             _        _______  _______  _______  _ \n|\     /|(  ___  )|\     /|  ( \      (  ___  )(  ____ \(  ____ \( )\n( \   / )| (   ) || )   ( |  | (      | (   ) || (    \/| (    \/| |\n \ (_) / | |   | || |   | |  | |      | |   | || (_____ | (__    | |\n  \   /  | |   | || |   | |  | |      | |   | |(_____  )|  __)   | |\n   ) (   | |   | || |   | |  | |      | |   | |      ) || (      (_)\n   | |   | (___) || (___) |  | (____/\| (___) |/\____) || (____/\ _ \n   \_/   (_______)(_______)  (_______/(_______)\_______)(_______/(_)\n")
    print("no more cards")
    self.info["state"] = state.CONNECTED
  
  async def send(self): # sends info
    print("sending...")
    await self.sock.send(json.dumps(self.info))
  async def set_sock(self):
    self.sock = await ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")

  async def connect(self):
    await self.set_sock()
    self.info["state"] = state.CONNECTED
    input("press enter to play")
    self.info["am_ready"] = True
    # await self.loop()
    try:
      await self.loop()
    except Exception as e:
      if self.connections > 40: return # give up
      print(f"exception caught:\n{e}")
      self.connections += 1
      await self.set_sock()
      self.info["state"] = state.CONNECTED
      self.info["am_ready"] = True
      await self.send() # in case we got stuck on send
      await self.loop()

  async def loop(self):
    while True:
      await self.sock.send("PING")
      update = json.loads(await self.sock.recv())
      
      if (update != self.game):
        self.game = update
        self.info["state"] = self.game["state"]
        # handling states
        state = self.game["state"]
        if state == 1: # restart
          await self.send()
        elif (state == 2):
          await self.send()
          if self.gamePlayed: break
        elif state in [3,4]: # update info
          self.think()
        elif state == 5: # play
          self.think()
          self.play()
          await self.send()
        elif state == 6: # end
          break
        else:
          print("invalid or disconnected state returned")
      sleep(1)

# basic universal gameplay
  def valid_plays(self, hand = None):
    if hand == None: hand = self.hand
    plays = []
    for card in hand:
      if card not in plays: 
        plays += self.set(card.split()[0])
        plays.remove(card)
      else: plays.remove(card)
    return plays
  def other_pids(self, pid = -1):
    ids = [id for id in range(0, self.stats["num_players"])]
    if pid != -1: ids.remove(pid)
    return ids
  def set(self, rank):
    return [f"{rank} {suit}" for suit in self.SUITS]
  def deck(self):
    deck = []
    for rank in self.RANKS:
      for suit in self.SUITS:
        deck.append(f"{rank} {suit}") 
    return deck


  def won(self):
    print("          _______                      _______  _        _ \n|\     /|(  ___  )|\     /|  |\     /|(  ___  )( (    /|( )\n( \   / )| (   ) || )   ( |  | )   ( || (   ) ||  \  ( || |\n \ (_) / | |   | || |   | |  | | _ | || |   | ||   \ | || |\n  \   /  | |   | || |   | |  | |( )| || |   | || (\ \) || |\n   ) (   | |   | || |   | |  | || || || |   | || | \   |(_)\n   | |   | (___) || (___) |  | () () || (___) || )  \  | _ \n   \_/   (_______)(_______)  (_______)(_______)|/    )_)(_)\n")
    self.is_winner = True
  def lost(self, winner):
    print("          _______             _        _______  _______  _______  _ \n|\     /|(  ___  )|\     /|  ( \      (  ___  )(  ____ \(  ____ \( )\n( \   / )| (   ) || )   ( |  | (      | (   ) || (    \/| (    \/| |\n \ (_) / | |   | || |   | |  | |      | |   | || (_____ | (__    | |\n  \   /  | |   | || |   | |  | |      | |   | |(_____  )|  __)   | |\n   ) (   | |   | || |   | |  | |      | |   | |      ) || (      (_)\n   | |   | (___) || (___) |  | (____/\| (___) |/\____) || (____/\ _ \n   \_/   (_______)(_______)  (_______/(_______)\_______)(_______/(_)\n")
    print(f"Player {winner} won!")
    self.is_winner = False

  # destructor
  def __del__(self):
    return self.is_winner

# testing
if __name__ == "__main__":
  player = fisher()