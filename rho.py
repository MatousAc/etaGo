# defines a human agent to play Go Fish
from fisherface import fisher

class rhoGo(fisher):
  def play(self): # chooses a player and card
    choices = self.valid_plays()



if __name__ == "__main__":
  player = rhoGo()