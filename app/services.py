from app.schemas import Order, StatsSummary, FilteredOrder, FailedOrder
from app.repository import OrderRepository
from typing import List, Dict, Any
from pydantic import ValidationError


def add_orders(
    repository: OrderRepository, orders: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Validates a list of orders according to business rules.
    """
    failed = []
    orders_to_add = []

    # Validate each order individually and add to list of orders to add
    # If validation fails, add to list of failed orders
    for data in orders:
        try:
            # Create and validate Order instance from raw dict
            order = Order(**data)
            orders_to_add.append(order)
        except ValidationError as e:
            # Extract the error message and order_id
            order_id = data.get('order_id', 'unknown')
            error = (
                'missing_order_id'
                if order_id == 'unknown'
                else e.errors()[0]['msg']
            ).replace('Value error, ', '')
            failed.append(FailedOrder(order_id=order_id, reason=error))

    # Add orders to repository and merge failed orders
    result = repository.add_orders(orders_to_add)
    result["failed"] = failed + result["failed"]
    return result


def get_filtered_orders(
    repository: OrderRepository, **kwargs: Any
) -> List[FilteredOrder]:
    """
    Returns filtered orders from the repository.
    """
    return repository.get_filtered_orders(**kwargs)


def get_stats_summary(repository: OrderRepository) -> StatsSummary:
    """
    Returns the summary of statistics.
    """
    all_orders = repository.get_filtered_orders()

    if not all_orders:
        return StatsSummary(
            total_orders=0,
            total_revenue=0.0,
            average_order_value=0.0,
            orders_per_category={},
            revenue_per_category={}
        )

    # Calculate total orders, total revenue and average order value
    total_orders = len(all_orders)
    total_revenue = sum(order.order_total for order in all_orders)
    average_order_value = total_revenue / total_orders

    # Calculate orders_per_category and revenue_per_category
    orders_per_cat: dict[str, int] = {}
    revenue_per_cat: dict[str, float] = {}

    for order in all_orders:
        order_categories = set()
        for item in order.items:
            cat = item.category
            order_categories.add(cat)

            # Add revenue for this category
            item_revenue = item.quantity * item.unit_price
            revenue_per_cat[cat] = revenue_per_cat.get(cat, 0.0) + item_revenue

        # Count order for each category it contains
        for cat in order_categories:
            orders_per_cat[cat] = orders_per_cat.get(cat, 0) + 1

    return StatsSummary(
        total_orders=total_orders,
        total_revenue=total_revenue,
        average_order_value=average_order_value,
        orders_per_category=orders_per_cat,
        revenue_per_category=revenue_per_cat
    )
