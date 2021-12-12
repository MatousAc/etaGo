# defines a watered-down mcts agent to play Go Fish
from ai import aiBase

class sigmaGo(aiBase):
  NAME = "sigmaGo"
## playing ##
  def play(self):
    nodes = self.valid_plays()
    # loop through many possibilities of hands
    for _ in range(100):
      pass


if __name__ == "__main__":
  player = sigmaGo()