import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas import OrderItem, Order, FilteredOrder, StatsSummary


class TestOrderItem:
    """Tests for OrderItem schema."""

    def test_valid_order_item(self):
        """Test creating a valid OrderItem."""
        item = OrderItem(
            sku="JEW-001",
            quantity=2,
            unit_price=99.99,
            category="Rings"
        )
        assert item.sku == "JEW-001"
        assert item.quantity == 2
        assert item.unit_price == 99.99
        assert item.category == "rings"  # Should be lowercased

    def test_quantity_validation_positive(self):
        """Test that quantity must be positive."""
        item = OrderItem(
            sku="JEW-001",
            quantity=1,
            unit_price=99.99,
            category="Rings"
        )
        assert item.quantity == 1

    def test_quantity_validation_negative(self):
        """Test that quantity cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                sku="JEW-001",
                quantity=-1,
                unit_price=99.99,
                category="Rings"
            )
        assert "invalid_quantity" in str(exc_info.value)

    def test_unit_price_validation_positive(self):
        """Test that unit_price must be positive."""
        item = OrderItem(
            sku="JEW-001",
            quantity=1,
            unit_price=50.0,
            category="Rings"
        )
        assert item.unit_price == 50.0

    def test_unit_price_validation_negative(self):
        """Test that unit_price cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                sku="JEW-001",
                quantity=1,
                unit_price=-10.0,
                category="Rings"
            )
        assert "invalid_unit_price" in str(exc_info.value)


class TestOrder:
    """Tests for Order schema."""

    def test_valid_order(self):
        """Test creating a valid Order."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        items = [
            OrderItem(
                sku="JEW-001", quantity=2, unit_price=99.99, category="Rings"
            ),
            OrderItem(
                sku="JEW-002", quantity=1, unit_price=199.99, category="Book"
            ),
        ]
        order = Order(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=items,
            currency="USD"
        )
        assert order.order_id == "ORD-001"
        assert order.customer_id == "CUST-001"
        assert order.order_timestamp == timestamp
        assert len(order.items) == 2
        assert order.currency == "USD"
        # Order total should be calculated automatically
        expected_total = (2 * 99.99) + (1 * 199.99)
        assert order.order_total == expected_total

    def test_items_validation_empty_list(self):
        """Test that items cannot be an empty list."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        with pytest.raises(ValidationError) as exc_info:
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=[],
                currency="USD"
            )
        assert "invalid_items" in str(exc_info.value)

    def test_items_validation_none(self):
        """Test that items cannot be None."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        with pytest.raises(ValidationError) as exc_info:
            Order(
                order_id="ORD-001",
                customer_id="CUST-001",
                order_timestamp=timestamp,
                items=None,
                currency="USD"
            )
        assert "invalid_items" in str(exc_info.value)


class TestFilteredOrder:
    """Tests for FilteredOrder schema."""

    def test_valid_filtered_order(self):
        """Test creating a valid FilteredOrder."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        items = [
            OrderItem(
                sku="JEW-001", quantity=2, unit_price=99.99, category="Rings"
            ),
        ]
        filtered_order = FilteredOrder(
            order_id="ORD-001",
            customer_id="CUST-001",
            order_timestamp=timestamp,
            items=items,
            currency="USD"
        )
        assert filtered_order.order_id == "ORD-001"
        assert filtered_order.customer_id == "CUST-001"
        assert filtered_order.currency == "USD"  # Field exists in model

        # Test that currency is excluded when serializing
        order_dict = filtered_order.model_dump()
        assert "currency" not in order_dict


class TestStatsSummary:
    """Tests for StatsSummary schema."""

    def test_valid_stats_summary(self):
        """Test creating a valid StatsSummary."""
        stats = StatsSummary(
            total_orders=100,
            total_revenue=50000.0,
            average_order_value=500.0,
            orders_per_category={
                "Rings": 40, "Necklaces": 35, "Earrings": 25
            },
            revenue_per_category={
                "Rings": 20000.0, "Necklaces": 20000.0, "Earrings": 10000.0
            }
        )
        assert stats.total_orders == 100
        assert stats.total_revenue == 50000.0
        assert stats.average_order_value == 500.0
        assert stats.orders_per_category["Rings"] == 40
        assert stats.revenue_per_category["Necklaces"] == 20000.0
