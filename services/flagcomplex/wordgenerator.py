# Developed by Sven Gruetzmacher.

import numpy as np

class wordgenerator:
  def __init__(self,gens,rules):
    self.generators = gens
    self.rules = rules
    self.maxlength = 0
    self.words = []
    self.maps = {}
    
  def generate(self,l):
    words = list(self.generators)
    for i in range(l-1):
        tmp = list(words)
        for g in self.generators:
            for w in tmp:
                words.append(g+w)
        words = self.filter(words, self.rules)
    words.sort(key=len)
    self.words = words
    self.maxlength = l
    #print("generated {} words of maximal length {}".format(len(words),l))
    
  def filter(self, words, rules):
    if rules is not None:
      cf = [x*y for x,y in rules.items()]
      for r in cf:
          words = [x.replace(r,'') for x in words]
      words = [x for x in words if not x=='']
      words = list(set(words))
    return words
  
  def wordtomap(self,word):
    m = np.eye(np.shape(self.maps['a'])[0])
    for x in reversed(word):
      m = np.matmul(self.maps[x],m)
    return m

  def tomaps(self,maps):
    self.maps = maps
    return [self.wordtomap(x) for x in self.words]
