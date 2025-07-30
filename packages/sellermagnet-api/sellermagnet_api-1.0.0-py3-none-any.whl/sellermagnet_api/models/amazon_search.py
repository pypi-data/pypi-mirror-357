from typing import Dict
from dataclasses import dataclass

@dataclass
class AmazonSearchResult:
    asin: str
    link: str
    listing_price: Dict[str, Any]
    main_image: str
    on_sale: bool
    position: int
    product_title: str
    review_amount: int
    review_rating: float
    sponsored: bool