from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AmazonBestseller:
    asin: str
    rank: int
    title: str

@dataclass
class AmazonDealCategory:
    id: str
    name: str