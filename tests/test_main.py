from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app


class TestIngestOrdersBatch:
    """Tests for POST /orders/batch endpoint."""

    def test_ingest_mixed_valid_and_invalid_orders(self):
        """Test ingesting a mix of valid and invalid orders."""
        client = TestClient(app)
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
            }
        ]

        response = client.post("/orders/batch", json=orders_data)

        assert response.status_code == 201
        data = response.json()
        assert data["ingested"] == 1
        assert len(data["failed"]) == 2
        assert data["failed"][0]['order_id'] == "ORD-002"
        assert data["failed"][0]['reason'] == "invalid_quantity"
        assert data["failed"][1]['order_id'] == "ORD-001"
        assert data["failed"][1]['reason'] == "duplicate_order_id"


class TestFetchOrders:
    """Tests for GET /orders endpoint."""

    def test_fetch_all_orders(self):
        """Test fetching all orders without filters."""
        client = TestClient(app)
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        # First, add some orders
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
        client.post("/orders/batch", json=orders_data)

        response = client.get("/orders")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Verify currency field is excluded
        assert "currency" not in data[0]

    def test_fetch_orders_with_multiple_filters(self):
        """Test fetching orders with multiple filters."""
        client = TestClient(app)
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
                "customer_id": "CUST-001",
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
            },
            {
                "order_id": "ORD-003",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-003",
                        "quantity": 1,
                        "unit_price": 149.99,
                        "category": "rings"
                    }
                ],
                "currency": "USD"
            }
        ]
        client.post("/orders/batch", json=orders_data)

        response = client.get(
            "/orders?customer_id=CUST-001&category=rings"
            "&min_total=100.0&max_total=200.0&offset=0&limit=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_id"] in ["ORD-001", "ORD-003"]

    def test_fetch_orders_with_pagination(self):
        """Test fetching orders with pagination."""
        client = TestClient(app)
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 1,
                        "unit_price": 100.0,
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
                        "unit_price": 200.0,
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
                        "unit_price": 150.0,
                        "category": "earrings"
                    }
                ],
                "currency": "USD"
            }
        ]
        client.post("/orders/batch", json=orders_data)

        response = client.get("/orders?offset=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_fetch_orders_with_min_total_filter(self):
        """Test fetching orders with minimum total filter."""
        client = TestClient(app)
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 1,
                        "unit_price": 50.0,
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
                        "unit_price": 200.0,
                        "category": "necklaces"
                    }
                ],
                "currency": "USD"
            }
        ]
        client.post("/orders/batch", json=orders_data)

        response = client.get("/orders?min_total=100.0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_id"] == "ORD-002"

    def test_fetch_orders_with_max_total_filter(self):
        """Test fetching orders with maximum total filter."""
        client = TestClient(app)
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 1,
                        "unit_price": 50.0,
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
                        "unit_price": 200.0,
                        "category": "necklaces"
                    }
                ],
                "currency": "USD"
            }
        ]
        client.post("/orders/batch", json=orders_data)

        response = client.get("/orders?max_total=100.0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_id"] == "ORD-001"


class TestFetchStatsSummary:
    """Tests for GET /stats/summary endpoint."""

    def test_fetch_stats_summary(self):
        """Test fetching stats."""
        client = TestClient(app)
        timestamp = datetime(2024, 1, 15, 10, 30, 0)

        orders_data = [
            {
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "order_timestamp": timestamp.isoformat(),
                "items": [
                    {
                        "sku": "JEW-001",
                        "quantity": 1,
                        "unit_price": 100.0,
                        "category": "rings"
                    },
                    {
                        "sku": "JEW-002",
                        "quantity": 2,
                        "unit_price": 75.0,
                        "category": "necklaces"
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
                        "sku": "JEW-003",
                        "quantity": 1,
                        "unit_price": 190.0,
                        "category": "rings"
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
                        "sku": "JEW-004",
                        "quantity": 2,
                        "unit_price": 50.0,
                        "category": "earrings"
                    }
                ],
                "currency": "USD"
            }
        ]
        client.post("/orders/batch", json=orders_data)

        response = client.get("/stats/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_orders"] == 3
        assert data["total_revenue"] == 540.0
        assert data["average_order_value"] == 180.0
        assert data["orders_per_category"]["rings"] == 2
        assert data["orders_per_category"]["necklaces"] == 1
        assert data["orders_per_category"]["earrings"] == 1
        assert data["revenue_per_category"]["rings"] == 290.0
        assert data["revenue_per_category"]["necklaces"] == 150.0
        assert data["revenue_per_category"]["earrings"] == 100.0
