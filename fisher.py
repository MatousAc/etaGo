# this file defines the structure of a fisher agent
import socket
import uuid

class fisher:
  HOST = '127.0.0.1'
  PORT = 4444
  def __init__(self):
    print ("The random id using uuid1() is : ",end="")
    print (uuid.uuid1())
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #   s.connect((self.HOST, self.PORT))
    #   s.sendall(b'Hello, world')
    #   data = s.recv(1024)

    # print('Received', repr(data))

if __name__ == "__main__":
  # do my testing stuff
  etaGo = fisher()