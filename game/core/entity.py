from dataclasses import dataclass

@dataclass
class BaseEntity:
    x:int; y:int
    def pos(self): return self.x,self.y
