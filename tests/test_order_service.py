


import app.services.order_service as order_service


def test_get_order_status_found(monkeypatch):
    fake_orders = [
        {
            "order_id": "JD10001",
            "status": "已发货",
            "product_name": "运动卫衣",
            "created_at": "2026-04-01 10:00:00",
        }
    ]

    monkeypatch.setattr(order_service, "load_orders", lambda: fake_orders)

    result = order_service.get_order_status("JD10001")
    assert result is not None
    assert result["order_id"] == "JD10001"
    assert result["status"] == "已发货"


def test_get_order_status_not_found(monkeypatch):
    monkeypatch.setattr(order_service, "load_orders", lambda: [])

    result = order_service.get_order_status("JD99999")
    assert result is None


def test_get_logistics_status_found(monkeypatch):
    fake_logistics = [
        {
            "order_id": "JD10002",
            "logistics_status": "运输中",
            "current_location": "西安转运中心",
            "estimated_delivery": "2026-04-22 18:00:00",
        }
    ]

    monkeypatch.setattr(order_service, "load_logistics", lambda: fake_logistics)

    result = order_service.get_logistics_status("JD10002")
    assert result is not None
    assert result["order_id"] == "JD10002"
    assert result["logistics_status"] == "运输中"


def test_get_logistics_status_not_found(monkeypatch):
    monkeypatch.setattr(order_service, "load_logistics", lambda: [])

    result = order_service.get_logistics_status("JD99999")
    assert result is None


def test_get_refund_status_found(monkeypatch):
    fake_refunds = [
        {
            "order_id": "JD10003",
            "refund_status": "退款处理中",
            "refund_amount": 99.0,
            "updated_at": "2026-04-20 09:30:00",
        }
    ]

    monkeypatch.setattr(order_service, "load_refunds", lambda: fake_refunds)

    result = order_service.get_refund_status("JD10003")
    assert result is not None
    assert result["order_id"] == "JD10003"
    assert result["refund_status"] == "退款处理中"


def test_get_refund_status_not_found(monkeypatch):
    monkeypatch.setattr(order_service, "load_refunds", lambda: [])

    result = order_service.get_refund_status("JD99999")
    assert result is None