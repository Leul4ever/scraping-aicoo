"""Data models for AI COO E-commerce Product Acquisition Engine.
Defines schemas for product candidates and scraping results using Pydantic.
"""

from datetime import datetime, timezone
from typing import List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProductCandidate(BaseModel):
    """Normalized schema representing a single e-commerce product candidate."""
    item_id: Union[str, int] = Field(
        ...,
        description="Unique identifier for the item on the source platform."
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Cleaned product title."
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Current listing price in target currency."
    )
    currency: str = Field(
        default="USD",
        description="Currency code (e.g., USD, EUR)."
    )
    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Average customer review rating (0.0 to 5.0)."
    )
    review_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total number of customer reviews/ratings."
    )
    product_url: str = Field(
        ...,
        description="Direct URL to product detail page."
    )
    image_url: str = Field(
        ...,
        description="URL of the main product thumbnail image."
    )
    
    # Metadata fields beneficial for downstream AI operations & analysis
    platform: str = Field(
        default="AliExpress",
        description="Source marketplace or platform."
    )
    orders_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Reported order volume or sold count, if available."
    )
    shipping_fee: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Estimated shipping cost to target destination, if available."
    )

    @field_validator("item_id", mode="before")
    @classmethod
    def clean_item_id(cls, v: Union[str, int]) -> str:
        """Coerce item_id to string representation."""
        return str(v).strip()

    @field_validator("title", mode="before")
    @classmethod
    def clean_title(cls, v: str) -> str:
        """Trim and clean title text."""
        if not isinstance(v, str):
            return str(v)
        return " ".join(v.split())

    @field_validator("price", mode="before")
    @classmethod
    def clean_price(cls, v: Union[float, int, str]) -> float:
        """Parse float price from strings like '$19.99' or raw numeric values."""
        if isinstance(v, (int, float)):
            return round(float(v), 2)
        if isinstance(v, str):
            # Strip currency symbols and whitespace
            cleaned = "".join(c for c in v if c.isdigit() or c in ".-")
            try:
                return round(float(cleaned), 2)
            except ValueError:
                return 0.0
        return 0.0

    @field_validator("rating", mode="before")
    @classmethod
    def clean_rating(cls, v: Union[float, int, str, None]) -> float:
        """Safely parse rating with bounds checking."""
        if v is None:
            return 0.0
        try:
            val = float(v)
            return max(0.0, min(5.0, round(val, 2)))
        except (ValueError, TypeError):
            return 0.0


class ScrapingBatchResult(BaseModel):
    """Container schema for a batch scraping execution run."""
    query: str
    target_market: str = "US"
    scraped_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_found: int = 0
    products: List[ProductCandidate] = Field(default_factory=list)
