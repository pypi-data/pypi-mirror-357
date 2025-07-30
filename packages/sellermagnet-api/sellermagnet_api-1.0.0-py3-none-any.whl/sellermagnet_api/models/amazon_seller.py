from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AmazonSellerReview:
    date_rated: str
    review_text: str
    star_rating: str

@dataclass
class AmazonSellerFeedback:
    rating: str
    reviews_count: str

@dataclass
class AmazonSellerData:
    seller_id: str
    marketplace: Dict[str, Dict[str, Any]]