"""
Tests for restocking API endpoints.
"""
from datetime import datetime

import pytest

import main


@pytest.fixture(autouse=True)
def clear_restock_orders():
    """Restock orders are module-level state; reset them for each test."""
    main.restock_orders.clear()
    yield
    main.restock_orders.clear()


class TestRestockRecommendations:
    """Test suite for the restock recommendation endpoint."""

    def test_get_recommendations_structure(self, client):
        """Test the response structure of the recommendations."""
        response = client.get("/api/restocking/recommendations?budget=3500")
        assert response.status_code == 200

        data = response.json()
        for key in ["budget", "max_budget", "recommended_total", "remaining_budget", "candidates"]:
            assert key in data
        assert len(data["candidates"]) > 0

        candidate = data["candidates"][0]
        for key in ["sku", "name", "category", "trend", "quantity", "unit_cost",
                    "line_total", "lead_time_days", "recommended"]:
            assert key in candidate

    @pytest.mark.parametrize("budget", [0, 1000, 3500, 7000])
    def test_recommended_total_within_budget(self, client, budget):
        """Test that the recommended items never cost more than the budget."""
        data = client.get(f"/api/restocking/recommendations?budget={budget}").json()

        recommended = [c for c in data["candidates"] if c["recommended"]]
        total = sum(c["line_total"] for c in recommended)
        assert total <= budget
        assert data["recommended_total"] == pytest.approx(total)
        assert data["remaining_budget"] == pytest.approx(budget - total)

    def test_zero_budget_recommends_nothing(self, client):
        """Test that a budget of zero gives no recommended items."""
        data = client.get("/api/restocking/recommendations?budget=0").json()
        assert not any(c["recommended"] for c in data["candidates"])

    def test_max_budget_recommends_everything(self, client):
        """Test that the max budget covers all candidates."""
        data = client.get("/api/restocking/recommendations").json()
        full = client.get(f"/api/restocking/recommendations?budget={data['max_budget']}").json()
        assert all(c["recommended"] for c in full["candidates"])
        assert full["max_budget"] % 500 == 0

    def test_default_budget_is_half_of_max(self, client):
        """Test that the budget defaults to half of the max budget."""
        data = client.get("/api/restocking/recommendations").json()
        assert data["budget"] == pytest.approx(round(data["max_budget"] / 2 / 100) * 100)

    def test_candidates_ranked_by_trend_then_gap(self, client):
        """Test that increasing items come first, then larger gaps."""
        candidates = client.get("/api/restocking/recommendations?budget=0").json()["candidates"]
        ranks = [(0 if c["trend"] == "increasing" else 1, -c["quantity"]) for c in candidates]
        assert ranks == sorted(ranks)

    def test_candidates_exclude_non_positive_gaps(self, client):
        """Test that items with falling demand are not candidates."""
        candidates = client.get("/api/restocking/recommendations?budget=0").json()["candidates"]
        skus = {c["sku"] for c in candidates}
        assert "SRV-301" not in skus
        assert all(c["quantity"] > 0 for c in candidates)

    def test_negative_budget_rejected(self, client):
        """Test that a negative budget returns 400."""
        response = client.get("/api/restocking/recommendations?budget=-1")
        assert response.status_code == 400


class TestRestockOrders:
    """Test suite for submitting and listing restock orders."""

    def test_list_empty(self, client):
        """Test that no restock orders exist at start."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restock_order(self, client):
        """Test submitting a valid restock order."""
        payload = {"budget": 2000, "items": [
            {"sku": "PRS-203", "quantity": 100},   # Sensors, 12.75, 7 days
            {"sku": "MCU-401", "quantity": 10}     # Controllers, 8.25, 12 days
        ]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-")
        assert order["total_cost"] == pytest.approx(1275 + 82.5)
        assert order["lead_time_days"] == 12
        assert len(order["items"]) == 2

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert (expected - submitted).days == 12

    def test_server_uses_inventory_price(self, client):
        """Test that the server ignores any price sent by the client."""
        payload = {"budget": 100, "items": [{"sku": "PSU-501", "quantity": 2, "unit_cost": 0.01}]}
        order = client.post("/api/restock-orders", json=payload).json()
        assert order["items"][0]["unit_cost"] == 18.99
        assert order["total_cost"] == pytest.approx(37.98)

    def test_created_order_is_listed_newest_first(self, client):
        """Test that the list shows the newest order first."""
        client.post("/api/restock-orders", json={"budget": 100, "items": [{"sku": "PSU-501", "quantity": 1}]})
        client.post("/api/restock-orders", json={"budget": 100, "items": [{"sku": "DRV-405", "quantity": 1}]})

        orders = client.get("/api/restock-orders").json()
        assert len(orders) == 2
        assert orders[0]["items"][0]["sku"] == "DRV-405"
        assert orders[0]["order_number"] != orders[1]["order_number"]

    def test_over_budget_rejected(self, client):
        """Test that an order above the budget returns 400."""
        payload = {"budget": 10, "items": [{"sku": "PCB-001", "quantity": 150}]}
        response = client.post("/api/restock-orders", json=payload)
        assert response.status_code == 400
        assert client.get("/api/restock-orders").json() == []

    def test_unknown_sku_rejected(self, client):
        """Test that an unknown SKU returns 400."""
        payload = {"budget": 1000, "items": [{"sku": "NOPE-999", "quantity": 1}]}
        assert client.post("/api/restock-orders", json=payload).status_code == 400

    def test_duplicate_sku_rejected(self, client):
        """Test that the same SKU twice returns 400."""
        payload = {"budget": 1000, "items": [{"sku": "PSU-501", "quantity": 1},
                                             {"sku": "PSU-501", "quantity": 2}]}
        assert client.post("/api/restock-orders", json=payload).status_code == 400

    @pytest.mark.parametrize("payload", [
        {"budget": 1000, "items": []},
        {"budget": 1000, "items": [{"sku": "PSU-501", "quantity": 0}]},
        {"budget": -5, "items": [{"sku": "PSU-501", "quantity": 1}]},
    ])
    def test_invalid_payload_rejected(self, client, payload):
        """Test that empty items, zero quantity or a negative budget return 422."""
        assert client.post("/api/restock-orders", json=payload).status_code == 422
