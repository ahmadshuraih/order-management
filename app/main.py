from typing import List, Any, Dict, Optional

from fastapi import Depends, FastAPI, status, Query

from app.repository import OrderRepository
from app.schemas import StatsSummary, BatchOrderResponse, FilteredOrder
from app.services import add_orders, get_filtered_orders, get_stats_summary

app = FastAPI(title="Order Management Service", version="1.0.0")


@app.post(
    "/orders/batch",
    response_model=BatchOrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def ingest_orders_batch(
    orders: List[Dict[str, Any]],
    repository: OrderRepository = Depends(OrderRepository)
):
    """
    Add a batch of orders to the repository.
    """
    return add_orders(repository, orders)


@app.get(
    "/orders",
    response_model=List[FilteredOrder],
    status_code=status.HTTP_200_OK
)
async def fetch_orders(
    customer_id: Optional[str] = Query(
        None, description="Filter by customer ID"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_total: Optional[float] = Query(
        None, description="Minimum order total"
    ),
    max_total: Optional[float] = Query(
        None, description="Maximum order total"
    ),
    offset: Optional[int] = Query(0, description="Number of orders to skip"),
    limit: Optional[int] = Query(
        -1, description="Maximum number of orders to return"
    ),
    repository: OrderRepository = Depends(OrderRepository)
):
    """
    Get dynamically filtered orders from the repository.
    """
    return get_filtered_orders(
        repository,
        customer_id=customer_id,
        category=category,
        min_total=min_total,
        max_total=max_total,
        offset=offset,
        limit=limit
    )


@app.get(
    "/stats/summary",
    response_model=StatsSummary,
    status_code=status.HTTP_200_OK
)
async def fetch_stats_summary(
    repository: OrderRepository = Depends(OrderRepository)
):
    """
    Get the summary of statistics from the repository.
    """
    return get_stats_summary(repository)
