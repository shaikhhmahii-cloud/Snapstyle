"""
SnapStyle Products Management Module
Uses Pandas to load, index, filter, and organize the fashion product catalog.
Handles category grouping, price tiering in INR, Wishlist management, and Saved Looks.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.csv")

# Global DataFrame and user session stores
_products_df: Optional[pd.DataFrame] = None
_wishlist_ids: set[str] = {"prod_001", "prod_007", "prod_010"} # Pre-populate a couple for realistic feel
_saved_looks: List[Dict[str, Any]] = [
    {
        "look_id": "look_saved_01",
        "title": "Minimalist Atelier Chic",
        "created_at": "2026-09-15T14:30:00Z",
        "inspiration_image": "https://lh3.googleusercontent.com/aida-public/AB6AXuAM8jsCn8WeBjhTpgbt6Zl7_CcPUozgszCOee3MdGVqP6aIEk7WGR6o6TpJU8wog0gb_hh85kOrm9lUIVTWwN4nOdgBzzdMy0dA8JlBorZFWgI7EcOFX59hjj0zSfVF3zzMQ9kFTqxctEMtWFLCaX1o3W-PKw2skUY7aMASzVep2RY5HaQ0Jop2nushfEs-rILXO6JHAaMjwsMmFzKCEkCC97-9vNngZzG00bF3unI-4SkN0RDJdKazzQ",
        "items": [
            {"category": "Top", "name": "Crisp White Blouse", "brand": "Zara", "price": 799, "size": "M"},
            {"category": "Bottom", "name": "Classic Straight Jeans", "brand": "Levi's Vintage", "price": 1299, "size": "32W"},
            {"category": "Accessories", "name": "Minimalist Gold Set", "brand": "Aurate", "price": 1996, "size": "One Size"}
        ],
        "total_price": 4094,
        "total_price_formatted": "₹4,094"
    }
]

_last_mtime: float = 0.0

def get_products_df() -> pd.DataFrame:
    """Loads and caches the product catalog as a Pandas DataFrame, refreshing if file changed."""
    global _products_df, _last_mtime
    path = DATA_PATH if os.path.exists(DATA_PATH) else os.path.join("data", "products.csv")
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        if _products_df is None or mtime > _last_mtime:
            _products_df = pd.read_csv(path)
            _last_mtime = mtime
    elif _products_df is None:
        _products_df = pd.DataFrame(columns=[
            "product_id", "product_name", "category", "brand", "price", 
            "image_url", "product_url", "description", "rating"
        ])
    return _products_df

def get_all_products() -> List[Dict[str, Any]]:
    """Returns all products as a list of dictionaries."""
    df = get_products_df()
    return df.to_dict(orient="records")

def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Finds a single product by its unique product_id."""
    df = get_products_df()
    match = df[df["product_id"] == product_id]
    if not match.empty:
        return match.iloc[0].to_dict()
    return None

def filter_products(
    category: Optional[str] = None,
    budget_tier: Optional[str] = None,
    brand: Optional[str] = None,
    sort_by: Optional[str] = "match",
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Applies Pandas multi-criteria filtering:
    - category: "top", "bottom", "shoes", "bag", "accessories", "all"
    - budget_tier: "under_1000", "1000_2500", "2500_5000", "5000_plus"
    - brand: brand name substring
    - sort_by: "price_asc", "price_desc", "rating_desc"
    """
    df = get_products_df().copy()
    
    # Category filter
    if category and category.lower() != "all":
        df = df[df["category"].str.lower() == category.lower()]
        
    # Budget filter in INR
    if budget_tier:
        b = budget_tier.lower()
        if "1000" in b and "under" in b:
            df = df[df["price"] <= 1000]
        elif "1000" in b and "2500" in b:
            df = df[(df["price"] >= 1000) & (df["price"] <= 2500)]
        elif "2500" in b and "5000" in b:
            df = df[(df["price"] >= 2500) & (df["price"] <= 5000)]
        elif "5000" in b or "plus" in b or "+" in b:
            df = df[df["price"] >= 5000]
            
    # Brand filter
    if brand and brand.lower() != "all":
        df = df[df["brand"].str.lower().str.contains(brand.lower(), na=False)]
        
    # Search query
    if search_query:
        q = search_query.lower()
        df = df[
            df["product_name"].str.lower().str.contains(q, na=False) |
            df["description"].str.lower().str.contains(q, na=False) |
            df["brand"].str.lower().str.contains(q, na=False)
        ]
        
    # Sorting
    if sort_by == "price_asc":
        df = df.sort_values(by="price", ascending=True)
    elif sort_by == "price_desc":
        df = df.sort_values(by="price", ascending=False)
    elif sort_by == "rating_desc":
        df = df.sort_values(by="rating", ascending=False)
        
    # Mark wishlist flag
    records = df.to_dict(orient="records")
    for r in records:
        r["is_wishlisted"] = r["product_id"] in _wishlist_ids
        r["formatted_price"] = f"₹{r['price']:,}"
        
    return records

def get_wishlist_products() -> List[Dict[str, Any]]:
    """Returns all products in the wishlist."""
    df = get_products_df()
    wishlisted_df = df[df["product_id"].isin(_wishlist_ids)]
    records = wishlisted_df.to_dict(orient="records")
    for r in records:
        r["is_wishlisted"] = True
        r["formatted_price"] = f"₹{r['price']:,}"
    return records

def add_to_wishlist(product_id: str) -> bool:
    """Adds a product_id to the wishlist."""
    _wishlist_ids.add(product_id)
    return True

def remove_from_wishlist(product_id: str) -> bool:
    """Removes a product_id from the wishlist."""
    _wishlist_ids.discard(product_id)
    return True

def get_saved_looks() -> List[Dict[str, Any]]:
    """Returns list of complete curated saved looks."""
    return _saved_looks

def save_new_look(look_data: Dict[str, Any]) -> Dict[str, Any]:
    """Stores a recreated outfit look."""
    _saved_looks.insert(0, look_data)
    return look_data
