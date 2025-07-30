from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class AmazonProductStatistics:
    asin: str
    product_title: str
    buy_box_price: int
    buy_box_fulfillment: str
    buy_box_seller_id_history: List[List[str]]
    category_tree: List[Dict[str, Any]]
    graphs: Optional[Dict[str, str]]
    listed_since: str
    lowest_fba_price: int
    lowest_fbm_price: int
    marketplace_id: str
    marketplace_new_price_history: List[List[Any]]
    offers: Dict[str, Any]
    product_review_average: float
    product_total_reviews: int
    root_category: Dict[str, Any]
    stats: Dict[str, Any]

@dataclass
class AmazonProductInfo:
    asin: str
    additional_details: Dict[str, str]
    bestseller_ranks: Dict[str, Any]
    bullet_points: List[str]
    buy_box_info: Dict[str, Any]
    categories: Dict[str, Any]
    description: List[str]
    details: Dict[str, str]
    has_a_plus_content: bool
    images: List[str]
    link: str
    listed_since_date: Optional[str]
    main_image: str
    marketplace_id: str
    reviews: Dict[str, Any]
    title: str
    variations: List[Dict[str, Any]]
    videos: List[str]

@dataclass
class AmazonProductOffer:
    condition: str
    delivery_date: str
    fulfillment_type: str
    inventory: int
    positive_percentage: int
    price_without_shipping: float
    seller_id: str
    seller_name: str
    shipping_price: float
    total_price: float
    total_reviews: int

@dataclass
class AmazonProductEstimatedSales:
    asin: str
    estimated_monthly_sales: int
    sales_rank: int
    category: str
    CX
    marketplace_domain: str