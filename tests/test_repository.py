from datetime import datetime

from app.schemas import Order, OrderItem, FilteredOrder
from app.repository import OrderRepository


class TestOrderRepository:
    """Tests for OrderRepository class."""

    def test_initialization(self):
        """Test that repository initializes with empty state."""
        repo = OrderRepository()
        assert len(repo.orders) == 0
        assert repo._indexes['customer_id'] == {}
        assert repo._indexes['category'] == {}

    def test_add_order_indexes(self):
        """
        Test that adding an order updates customer_id and category indexes.
        """
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        items = [
            OrderItem(
                sku="JEW-001", quantity=2, unit_price=99.99, category="rings"
            ),
            OrderItem(
                sku="JEW-002", quantity=1, unit_price=199.99, category="books"
            )
        ]
        order = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=items,
            currency="USD"
        )

        repo.add_order(order)

        assert "rings" in repo._indexes['category']
        assert "books" in repo._indexes['category']
        assert "ORD-001" in repo._indexes['category']['rings']
        assert "ORD-001" in repo._indexes['category']['books']

    def test_add_orders_batch(self):
        """Test adding multiple orders at once."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    ),
                ],
                currency="USD"
            ),
        ]

        result = repo.add_orders(orders)

        assert result["ingested"] == 2
        assert len(result["failed"]) == 0
        assert len(repo.orders) == 2

    def test_add_orders_with_duplicate_id(self):
        """Test that duplicate order IDs are rejected."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-001",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    )
                ],
                currency="USD"
            ),
        ]

        result = repo.add_orders(orders)

        assert result["ingested"] == 1
        assert len(result["failed"]) == 1
        assert result["failed"][0]["order_id"] == "ORD-001"
        assert result["failed"][0]["reason"] == "duplicate_order_id"
        assert len(repo.orders) == 1

    def test_order_id_exists(self):
        """Test checking if order ID exists."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        assert repo.order_id_exists("ORD-001") is False

        order = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-001",
                    quantity=1,
                    unit_price=99.99,
                    category="rings"
                )
            ],
            currency="USD"
        )
        repo.add_order(order)

        assert repo.order_id_exists("ORD-001") is True
        assert repo.order_id_exists("ORD-999") is False

    def test_get_orders_by_customer_id(self):
        """Test retrieving orders by customer ID."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        order1 = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-001",
                    quantity=1,
                    unit_price=99.99,
                    category="rings"
                )
            ],
            currency="USD"
        )
        order2 = Order(
            order_id="ORD-002",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-002",
                    quantity=2,
                    unit_price=199.99,
                    category="books"
                )
            ],
            currency="USD"
        )
        order3 = Order(
            order_id="ORD-003",
            customer_id="CUST-002",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-003",
                    quantity=1,
                    unit_price=50.0,
                    category="earrings"
                )
            ],
            currency="USD"
        )

        repo.add_order(order1)
        repo.add_order(order2)
        repo.add_order(order3)

        customer_orders = repo.get_orders_by_customer_id("CUST-001")
        assert len(customer_orders) == 2
        assert {o.order_id for o in customer_orders} == {"ORD-001", "ORD-002"}

    def test_get_orders_by_category(self):
        """Test retrieving orders by category."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        order1 = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-001",
                    quantity=1,
                    unit_price=99.99,
                    category="rings"
                )
            ],
            currency="USD"
        )
        order2 = Order(
            order_id="ORD-002",
            customer_id="CUST-002",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-002",
                    quantity=2,
                    unit_price=199.99,
                    category="rings"
                )
            ],
            currency="USD"
        )
        order3 = Order(
            order_id="ORD-003",
            customer_id="CUST-003",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-003",
                    quantity=1,
                    unit_price=50.0,
                    category="books"
                )
            ],
            currency="USD"
        )

        repo.add_order(order1)
        repo.add_order(order2)
        repo.add_order(order3)

        rings_orders = repo.get_orders_by_category("rings")
        assert len(rings_orders) == 2
        assert {o.order_id for o in rings_orders} == {"ORD-001", "ORD-002"}

    def test_get_filtered_orders_by_indexes_no_filters(self):
        """Test getting all orders when no filters are applied."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    )
                ],
                currency="USD"
            ),
        ]

        repo.add_orders(orders)

        all_orders = repo.get_filtered_orders_by_indexes()
        assert len(all_orders) == 2

    def test_get_filtered_orders_by_indexes_customer_id(self):
        """Test filtering by customer ID."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    )
                ],
                currency="USD"
            ),
        ]

        repo.add_orders(orders)

        filtered = repo.get_filtered_orders_by_indexes(customer_id="CUST-001")
        assert len(filtered) == 1
        assert filtered[0].order_id == "ORD-001"

    def test_get_filtered_orders_by_indexes_category(self):
        """Test filtering by category."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="Rings"
                    )
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    )
                ],
                currency="USD"
            ),
        ]

        repo.add_orders(orders)

        # Category is stored as lowercase, so "Rings" should match "rings"
        filtered = repo.get_filtered_orders_by_indexes(category="Rings")
        assert len(filtered) == 1
        assert filtered[0].order_id == "ORD-001"

    def test_paginate_orders_with_limit(self):
        """Test pagination with a limit."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id=f"ORD-00{i}",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku=f"JEW-{i}",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            )
            for i in range(1, 6)
        ]

        paginated = repo.paginate_orders(orders, offset=1, limit=2)
        assert len(paginated) == 2
        assert paginated[0].order_id == "ORD-002"
        assert paginated[1].order_id == "ORD-003"

    def test_paginate_orders_offset_beyond_length(self):
        """Test pagination when offset is beyond list length."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    )
                ],
                currency="USD"
            )
        ]

        paginated = repo.paginate_orders(orders, offset=10, limit=5)
        assert len(paginated) == 0

    def test_filter_orders_by_total_min(self):
        """Test filtering orders by minimum total."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=50.0,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=100.0,
                        category="books"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-003",
                customer_id="CUST-003",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-003",
                        quantity=1,
                        unit_price=150.0,
                        category="earrings"
                    ),
                ],
                currency="USD"
            ),
        ]

        filtered = repo.filter_orders_by_total(orders, min=100.0)
        assert len(filtered) == 2
        assert {o.order_id for o in filtered} == {"ORD-002", "ORD-003"}

    def test_filter_orders_by_total_max(self):
        """Test filtering orders by maximum total."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=50.0,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=100.0,
                        category="books"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-003",
                customer_id="CUST-003",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-003",
                        quantity=1,
                        unit_price=150.0,
                        category="earrings"
                    ),
                ],
                currency="USD"
            ),
        ]

        filtered = repo.filter_orders_by_total(orders, max=100.0)
        assert len(filtered) == 1
        assert filtered[0].order_id == "ORD-001"

    def test_get_filtered_orders_basic(self):
        """Test get_filtered_orders with no filters."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=99.99,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=199.99,
                        category="books"
                    ),
                ],
                currency="USD"
            ),
        ]

        repo.add_orders(orders)

        filtered = repo.get_filtered_orders()
        assert len(filtered) == 2
        assert all(isinstance(o, FilteredOrder) for o in filtered)
        # Verify currency is excluded
        for order in filtered:
            order_dict = order.model_dump()
            assert "currency" not in order_dict

    def test_get_filtered_orders_combined_filters(self):
        """Test get_filtered_orders with multiple filters combined."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-001",
                        quantity=1,
                        unit_price=50.0,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-002",
                        quantity=2,
                        unit_price=100.0,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
            Order(
                order_id="ORD-003",
                customer_id="CUST-002",
                order_timestamp=timestamp,
                items=[
                    OrderItem(
                        sku="JEW-003",
                        quantity=1,
                        unit_price=150.0,
                        category="rings"
                    ),
                ],
                currency="USD"
            ),
        ]

        repo.add_orders(orders)

        filtered = repo.get_filtered_orders(
            customer_id="CUST-001",
            category="rings",
            min_total=100,
            max_total=200,
            offset=0,
            limit=10
        )

        assert len(filtered) == 1
        assert filtered[0].order_id == "ORD-002"
