# this file defines the structure of a fisher agent
from states import state
import asyncio as aio, websockets as ws
import socket, uuid, random, json, time
class fisher:
  HOST = "127.0.0.1"
  PORT = 4444
  def __init__(self):
    # self.port = random.randint(1024, 65535)
    self.uuid = uuid.uuid4()
    self.sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.info = {
      "state"     : state.DISCONNECTED,
      "am_ready"  : False
    }
    self.game = {}
    aio.run(self.play())
    print(self.uuid)
    print("created fisher")

  async def send(self):
    await self.sock.send(json.dumps(self.info))

  async def play(self):
    print(f"connecting to: ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    self.sock = await ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    self.info["state"] = state.CONNECTED
    input("press enter to signal that you are ready to play")
    self.info["am_ready"] = True

    while True:
      await self.sock.send("PING")
      update = json.loads(await self.sock.recv())
      if (update != self.game):
        self.game = update
        print(self.game)
        self.handle_states()
        await self.send()
      time.sleep(1)

  def handle_states(self):
    pass

  def __del__(self):
    # self.sock.close()
    pass

if __name__ == "__main__":
  etaGo = fisher()