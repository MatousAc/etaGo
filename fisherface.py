# this file defines the structure of a fisher agent
from states import state
from uuid import uuid4
import asyncio as aio, websockets as ws
import random, json, time

class fisher:
  # static
  HOST = "127.0.0.1"
  PORT = 4444
  NUM_DELT = 7
  AVGP = -1 # used to represent the "average probability"

  def __init__(self):
    self.uuid = uuid4() # generate uuid
    self.info = { # keeps track of client info
      "state"     : state.DISCONNECTED,
      "am_ready"  : False
    }
    self.game = {} # game state
    print(self.uuid)
    # make connection
    aio.run(self.connect())
  # logic - meant to be overridden
  def think(self): # obtains and organizes info
    pass
  def play(self): # chooses a player and card
    pass
  async def send(self): # sends info
    await self.sock.send(json.dumps(self.info))
  # connects to sever
  async def connect(self):
    self.sock = await ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    self.info["state"] = state.CONNECTED
    input("press enter to signal that you are ready to play") # blocks until ready
    self.info["am_ready"] = True
    await self.loop()
    # keeps agent playing
  async def loop(self):
    while True:
      await self.sock.send("PING")
      update = json.loads(await self.sock.recv())
      
      if (update != self.game):
        self.game = update
        print(self.game)
        self.info["state"] = self.game["state"]
        # handling states
        if self.game["state"] == 1: # restart
          await self.send()
        elif (self.game["state"] == 2): # revert
          await self.send()
          # self.info["am_ready"] = False
          # self.info["state"] = state.CONNECTED
          # await self.send()
          # input("press enter to signal that you are ready to play") # blocks until ready
          # self.info["am_ready"] = True          
        elif self.game["state"] in [3,4]: # update info
          self.think()
        elif self.game["state"] == 5: # play
          self.think()
          self.play()
          await self.send()
        elif self.game["state"] == 6: # end
          pass
        else:
          print("invalid or disconnected state returned")
      time.sleep(1)

  def possibilities_deck(self):
    deck = {} # returns an object representing a deck of possibilities
    for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]:
        for suit in ["diams", "spades", "clubs", "hearts"]:
          deck[f"{rank} {suit}"] = self.AVGP
    return deck
  def avg_prob(self, cards_in_hand):
    pass
  # destructor
  def __del__(self):
    # self.sock.close()
    pass

# testing
if __name__ == "__main__":
  etaGo = fisher()