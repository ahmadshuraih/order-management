from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# Database Schemas
class OrderItem(BaseModel):
    """
    Represents an item in an order.
    """
    sku: str = Field(description="The SKU of the item")
    quantity: int = Field(description="The quantity of the item")
    unit_price: float = Field(description="The unit price of the item")
    category: str = Field(description="The category of the item")

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """
        Validates the quantity.
        """
        if v <= 0:
            raise ValueError("invalid_quantity")
        return v

    @field_validator("unit_price", mode="before")
    @classmethod
    def validate_unit_price(cls, v: float) -> float:
        """
        Validates the unit price.
        """
        if v <= 0:
            raise ValueError("invalid_unit_price")
        return v

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """
        Lowercase the category.
        """
        return v.lower()


class Order(BaseModel):
    """
    Represents an order.
    """
    order_id: str = Field(description="The ID of the order")
    customer_id: str = Field(description="The ID of the customer")
    order_timestamp: datetime = Field(description="The timestamp of the order")
    order_total: Optional[float] = Field(
        default=0.0, description="The total of the order"
    )
    items: List[OrderItem] = Field(description="The items in the order")
    currency: str = Field(description="The currency of the order prices")

    @field_validator("items", mode="before")
    @classmethod
    def validate_items(cls, v: List[OrderItem]) -> List[OrderItem]:
        """
        Validates the items.
        """
        if not v or len(v) == 0:
            raise ValueError("invalid_items")
        return v

    @model_validator(mode='after')
    def calculate_order_total(self):
        """
        Calculates order_total from items if not provided or is 0.0.
        """
        if self.order_total is None or self.order_total == 0.0:
            self.order_total = sum(
                item.quantity * item.unit_price for item in self.items
            )
        return self


# API Response Schemas
class FilteredOrder(Order):
    """
    Represents a filtered order response (excludes currency field).
    """
    currency: str = Field(exclude=True)


class StatsSummary(BaseModel):
    """
    Represents the summary of statistics.
    """
    total_orders: int = Field(description="The total number of orders")
    total_revenue: float = Field(description="The total revenue of all orders")
    average_order_value: float = Field(description="The average order value")
    orders_per_category: dict[str, int] = Field(
        description="The number of orders per category"
    )
    revenue_per_category: dict[str, float] = Field(
        description="The revenue per category"
    )


class FailedOrder(BaseModel):
    """
    Represents a failed order entry.
    """
    order_id: str = Field(description="The ID of the failed order")
    reason: str = Field(description="The reason for failure")


class BatchOrderResponse(BaseModel):
    """
    Represents the response from a batch order ingestion.
    """
    ingested: int = Field(
        description="The number of successfully ingested orders"
    )
    failed: List[FailedOrder] = Field(
        description="List of failed orders with reasons"
    )
