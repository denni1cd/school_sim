from dataclasses import dataclass, field
from enum import Enum

class NPCState(Enum):
    IDLE='idle'; MOVING='moving'; PERFORMING_TASK='performing_task'

@dataclass
class Actor:
    name:str; x:int; y:int
    state:NPCState=NPCState.IDLE
    target:tuple|None=None
    path:list=field(default_factory=list)
    def set_target(self,tx,ty): self.target=(tx,ty); self.path.clear()
