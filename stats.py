from eta import etaGo
from sigma import sigmaGo
from theta import thetaGo

def get_stats():
  for offset in range(50):
    e = etaGo(offset)
    t = thetaGo(offset)




if __name__ == "__main__":
  get_stats()