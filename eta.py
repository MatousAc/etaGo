# defines a rule-based agent to play Go Fish
from fisherface import fisher
class etaGo(fisher):
  def __init__(self):
    self.phands = []
    self.stats = {
      "num_unknown"   : 52,
      "first_pass"    : True
    }
    super().__init__()

  def configure_hands(self):
    pass

  def think(self):
    print("overridden think")
    if self.stats["first_pass"]:
      self.configure_hands()
    pass

  def play(self):
    print("overridden play")


if __name__ == "__main__":
  print(
    " _______ _________ _______  _______  _______ \n(  ____ \\__   __/(  ___  )(  ____ \(  ___  )\n| (    \/   ) (   | (   ) || (    \/| (   ) |\n| (__       | |   | (___) || |      | |   | |\n|  __)      | |   |  ___  || | ____ | |   | |\n| (         | |   | (   ) || | \_  )| |   | |\n| (____/\   | |   | )   ( || (___) || (___) |\n(_______/   )_(   |/     \|(_______)(_______)"
  )
  player = etaGo()