# this file defines the structure of a fisher agent
import asyncio, websockets as ws
import socket, uuid, random, json, enum

class fisher:
  HOST = "localhost" #'127.0.0.1'
  PORT = 4444
  def __init__(self):
    # self.port = random.randint(1024, 65535)
    self.uuid = uuid.uuid4()
    self.sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(self.uuid)
    print("created fisher")

  async def play(self):
    print(f"connecting to: ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}")
    async with ws.connect(f"ws://{self.HOST}:{self.PORT}/websocket/{self.uuid}") as sock:
      print(sock)
      await sock.send("PING")
      await sock.recv()

  def __del__(self):
    # self.sock.close()
    pass

if __name__ == "__main__":
  # do my testing stuff
  etaGo = fisher()
  asyncio.run(etaGo.play())