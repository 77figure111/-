#对应 should_escalate()
from app.services.escalation_service import should_escalate


def test_should_escalate_for_complaint():
    assert should_escalate("我要投诉你们", "好的，我来帮您处理") is True


def test_should_escalate_for_compensation():
    assert should_escalate("我要赔偿", "好的，我来帮您处理") is True


def test_should_escalate_for_manual_service_keyword():
    assert should_escalate("我要人工客服", "好的，我来帮您处理") is True


def test_should_escalate_when_order_not_found():
    assert should_escalate("帮我查订单JD99999", "抱歉，没有查询到订单 JD99999 的信息。") is True


def test_should_not_escalate_for_normal_query():
    assert should_escalate("这件衣服是什么材质", "这件衣服是纯棉材质。") is False