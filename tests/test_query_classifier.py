#对应 classify_query()
from app.services.query_classifier import classify_query


def test_classify_size_query():
    assert classify_query("我穿多大合适") == "size"


def test_classify_logistics_query():
    assert classify_query("我的物流到哪了") == "logistics_query"


def test_classify_refund_query():
    assert classify_query("我的退款什么时候到账") == "refund_query"


def test_classify_promotion_query():
    assert classify_query("现在有优惠券吗") == "promotion"


def test_classify_product_query():
    assert classify_query("这件衣服是什么材质") == "product"


def test_classify_order_query():
    assert classify_query("帮我查一下订单状态") == "order_query"


def test_classify_general_query():
    assert classify_query("你好") == "general"