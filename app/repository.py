from app.schemas import Order, FilteredOrder
from typing import List, Dict, Set, Optional


class OrderRepository:
    """
    Represents the repository for orders.
    """

    _instance = None

    # Use the singleton pattern to get the order repository instance.
    # To keep the state of the repository between requests.
    # In this case, we save the data in the memory.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self):
        self.orders: Dict[str, Order] = {}
        self._indexes: Dict[str, Dict[str, Set[str]]] = {
            'customer_id': {}, 'category': {}
        }

    def add_orders(self, orders: List[Order]) -> Dict[str, int]:
        """
        Adds a list of orders to the repository.
        Returns a dictionary with the number of ingested orders
        list of failed orders_id.
        """
        ingested = 0
        failed = []
        for order in orders:
            if self.order_id_exists(order.order_id):
                failed.append({
                    "order_id": order.order_id,
                    "reason": "duplicate_order_id"
                })
                continue
            self.add_order(order)
            ingested += 1
        return {"ingested": ingested, "failed": failed}

    def add_order(self, order: Order) -> None:
        """
        Adds an order to the repository.
        """
        # Add order to orders dictionary
        self.orders[order.order_id] = order

        # Add order to indexes
        self.add_order_to_indexes(order)

    def get_orders_by_customer_id(self, customer_id: str) -> List[Order]:
        """
        Returns all orders for a given customer ID.
        """
        order_ids = self._indexes['customer_id'].get(customer_id, set())
        return [self.orders[order_id] for order_id in sorted(order_ids)]

    def get_orders_by_category(self, category: str) -> List[Order]:
        """
        Returns all orders for a given category.
        """
        order_ids = self._indexes['category'].get(category, set())
        return [self.orders[order_id] for order_id in sorted(order_ids)]

    def get_filtered_orders_by_indexes(
            self,
            customer_id: Optional[str] = None,
            category: Optional[str] = None
    ) -> List[Order]:
        """
        Returns filtered orders by indexes.
        """
        if customer_id and category:
            # Use both indexes - get intersection
            cust_ids = self._indexes['customer_id'].get(customer_id, set())
            cat_ids = self._indexes['category'].get(category.lower(), set())
            all_order_ids = cust_ids.intersection(cat_ids)
            sorted_ids = sorted(all_order_ids)
            return [self.orders[order_id] for order_id in sorted_ids]
        elif customer_id:
            # Return all orders filtered by customer_id
            return self.get_orders_by_customer_id(customer_id)
        elif category:
            # Return all orders filtered by category
            return self.get_orders_by_category(category.lower())

        return sorted(list(self.orders.values()), key=lambda o: o.order_id)

    def paginate_orders(
            self, orders: List[Order], offset: int = 0, limit: int = -1
    ) -> List[Order]:
        """
        Paginates a list of orders.
        """
        if limit == -1:
            return orders[offset:]
        return orders[offset:offset+limit]

    def filter_orders_by_total(
            self,
            orders: List[Order],
            min: Optional[float] = None,
            max: Optional[float] = None
    ) -> List[Order]:
        """
        Filters orders by total.
        """
        if min is not None:
            orders = [order for order in orders if order.order_total >= min]
        if max is not None:
            orders = [order for order in orders if order.order_total <= max]
        return orders

    def get_filtered_orders(
        self,
        customer_id: Optional[str] = None,
        category: Optional[str] = None,
        min_total: Optional[float] = None,
        max_total: Optional[float] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = -1
    ) -> List[FilteredOrder]:
        """
        Returns filtered orders based on the provided criteria.

        Args:
            customer_id: Filter by customer ID
            category: Filter by category (case-insensitive)
            min_total: Minimum order total (inclusive)
            max_total: Maximum order total (inclusive)
            offset: Number of orders to skip (for pagination)
            limit: Maximum number of orders to return (-1 for no limit)

        Returns:
            List of filtered orders matching the filter criteria
        """
        # Get filtered orders by indexes
        orders = self.get_filtered_orders_by_indexes(customer_id, category)

        # Apply additional filters
        if min_total is not None or max_total is not None:
            orders = self.filter_orders_by_total(orders, min_total, max_total)

        # Paginate orders
        paginated_orders = self.paginate_orders(orders, offset, limit)

        # Convert to FilteredOrder to exclude currency field
        filtered_orders = [
            FilteredOrder.model_validate(order.model_dump())
            for order in paginated_orders
        ]

        return filtered_orders

    def add_order_to_indexes(self, order: Order) -> None:
        """
        Adds an order to the indexes.
        """
        for index_key in self._indexes:
            eval(f"self.add_order_to_{index_key}_index(order)")

    def add_order_to_customer_id_index(self, order: Order) -> None:
        """
        Adds an order to the customer id index.
        """
        order_id = order.order_id
        customer_id = order.customer_id

        if customer_id not in self._indexes['customer_id']:
            self._indexes['customer_id'][customer_id] = set()
        self._indexes['customer_id'][customer_id].add(order_id)

    def add_order_to_category_index(self, order: Order) -> None:
        """
        Adds an order to the category index.
        """
        order_id = order.order_id

        for item in order.items:
            category = item.category
            if category not in self._indexes['category']:
                self._indexes['category'][category] = set()
            self._indexes['category'][category].add(order_id)

    def order_id_exists(self, order_id: str) -> bool:
        """
        Checks if an order ID exists in the repository.
        """
        return self.orders.get(order_id) is not None

    def clear_storage(self) -> None:
        """
        Clears all orders and indexes from the repository.
        Useful for testing to reset the singleton state.
        """
        self._init_storage()
