from datetime import datetime

from app.services import add_orders, get_filtered_orders, get_stats_summary
from app.repository import OrderRepository
from app.schemas import Order, OrderItem


class TestAddOrders:
    """Tests for add_orders function."""

    def test_add_valid_orders(self):
        """Test adding valid orders."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 2,
                        "unit_price": 99.99,
                        "category": "rings"
                    }
                ],
                "currency": "USD"
            },
            {
                "order_id": "ORD-002",
                "customer_id": "CUST-002",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-002",
                        "quantity": 1,
                        "unit_price": 199.99,
                        "category": "necklaces"
                    }
                ],
                "currency": "USD"
            }
        ]

        result = add_orders(repo, orders_data)

        assert result["ingested"] == 2
        assert len(result["failed"]) == 0
        assert len(repo.orders) == 2
        assert "ORD-001" in repo.orders
        assert "ORD-002" in repo.orders

    def test_add_mixed_valid_and_invalid_orders(self):
        """Test adding a mix of valid and invalid orders."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 2,
                        "unit_price": 99.99,
                        "category": "rings"
                    }
                ],
                "currency": "USD"
            },
            {
                "order_id": "ORD-002",
                "customer_id": "CUST-002",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-002",
                        "quantity": -1,  # Invalid
                        "unit_price": 199.99,
                        "category": "necklaces"
                    }
                ],
                "currency": "USD"
            },
            {
                "order_id": "ORD-003",
                "customer_id": "CUST-003",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-003",
                        "quantity": 1,
                        "unit_price": 149.99,
                        "category": "earrings"
                    }
                ],
                "currency": "USD"
            }
        ]

        result = add_orders(repo, orders_data)

        assert result["ingested"] == 2
        assert len(repo.orders) == 2
        assert "ORD-001" in repo.orders
        assert "ORD-003" in repo.orders

        assert len(result["failed"]) == 1
        assert result["failed"][0].reason == "invalid_quantity"
        assert "ORD-002" not in repo.orders

    def test_add_orders_with_duplicate_order_id(self):
        """Test adding orders with duplicate order IDs."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 2,
                        "unit_price": 99.99,
                        "category": "rings"
                    }
                ],
                "currency": "USD"
            },
            {
                "order_id": "ORD-001",  # Duplicate
                "customer_id": "CUST-002",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-002",
                        "quantity": 1,
                        "unit_price": 199.99,
                        "category": "necklaces"
                    }
                ],
                "currency": "USD"
            }
        ]

        result = add_orders(repo, orders_data)

        assert result["ingested"] == 1
        assert len(result["failed"]) == 1
        assert len(repo.orders) == 1
        assert result["failed"][0]["reason"] == "duplicate_order_id"

    def test_add_orders_with_missing_order_id(self):
        """
        Test that orders without order_id.
        """
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 1,
                        "unit_price": 99.99,
                        "category": "rings"
                    }
                ],
                "currency": "USD"
            }
        ]

        result = add_orders(repo, orders_data)

        assert result["ingested"] == 0
        assert len(result["failed"]) == 1
        assert result["failed"][0].order_id == "unknown"
        assert result["failed"][0].reason == "missing_order_id"


class TestGetFilteredOrders:
    """Tests for get_filtered_orders function."""

    def test_get_all_orders(self):
        """Test getting all orders without filters."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        order1 = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-001",
                    quantity=2,
                    unit_price=99.99,
                    category="rings"
                ),
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
                    quantity=1,
                    unit_price=199.99,
                    category="necklaces"
                ),
            ],
            currency="USD"
        )

        repo.add_order(order1)
        repo.add_order(order2)

        result = get_filtered_orders(repo)

        assert len(result) == 2
        assert all("currency" not in order.model_dump() for order in result)

    def test_get_orders_with_multiple_filters(self):
        """Test getting orders with multiple filters."""
        repo = OrderRepository()
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        order1 = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-001",
                    quantity=2,
                    unit_price=99.99,
                    category="rings"
                ),
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
                    quantity=1,
                    unit_price=199.99,
                    category="necklaces"
                ),
            ],
            currency="USD"
        )
        order3 = Order(
            order_id="ORD-003",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-003",
                    quantity=1,
                    unit_price=149.99,
                    category="rings"
                ),
            ],
            currency="USD"
        )

        repo.add_order(order1)
        repo.add_order(order2)
        repo.add_order(order3)

        result = get_filtered_orders(
            repo,
            customer_id="CUST-001",
            category="rings",
            min_total=100.0,
            max_total=200.0,
            offset=0,
            limit=1
        )

        assert len(result) == 1
        assert result[0].order_id == "ORD-001"


class TestGetStatsSummary:
    """Tests for get_stats_summary function."""

    def test_stats_summary(self):
        """Test stats summary."""
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
                    unit_price=100.0,
                    category="rings"
                ),
                OrderItem(
                    sku="JEW-002",
                    quantity=2,
                    unit_price=75.0,
                    category="necklaces"
                ),
            ],
            currency="USD"
        )

        order2 = Order(
            order_id="ORD-002",
            customer_id="CUST-002",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-003",
                    quantity=1,
                    unit_price=200.0,
                    category="rings"
                ),
            ],
            currency="USD"
        )

        order3 = Order(
            order_id="ORD-003",
            customer_id="CUST-003",
            order_timestamp=timestamp,
            items=[
                OrderItem(
                    sku="JEW-004",
                    quantity=2,
                    unit_price=50.0,
                    category="earrings"
                ),
            ],
            currency="USD"
        )

        repo.add_order(order1)
        repo.add_order(order2)
        repo.add_order(order3)

        stats = get_stats_summary(repo)

        assert stats.total_orders == 3
        assert stats.total_revenue == 550.0
        assert abs(stats.average_order_value - 183.33) < 0.01

        assert stats.orders_per_category["rings"] == 2
        assert stats.orders_per_category["necklaces"] == 1
        assert stats.orders_per_category["earrings"] == 1

        assert stats.revenue_per_category["rings"] == 300.0
        assert stats.revenue_per_category["necklaces"] == 150.0
        assert stats.revenue_per_category["earrings"] == 100.0
