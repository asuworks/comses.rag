from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class VectorPoint:
  id: str
  payload: Dict[str,str]
  vector: List[float]
