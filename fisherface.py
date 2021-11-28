# this file defines the structure of a fisher agent
import asyncio, websockets as ws
import socket, uuid, random, json
import enum, time

class fisher:
  HOST = "127.0.0.1"
  PORT = 4444
  def __init__(self):
    # self.port = random.randint(1024, 65535)
    self.uuid = uuid.uuid4()
    self.sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.game = {}
    asyncio.run(self.play())
    print(self.uuid)
    print("created fisher")

  async def play(self):
    print(f"connecting to: ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    self.sock = await ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    while True:
      await self.sock.send("PING")
      update = json.loads(await self.sock.recv())
      if (update != self.game):
        self.game = update
        print(self.game)
        self.handle_states()
      time.sleep(1)

  def handle_states():
    

  def __del__(self):
    # self.sock.close()
    pass

if __name__ == "__main__":
  etaGo = fisher()