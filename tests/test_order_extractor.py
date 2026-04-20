#对应项目里的 extract_order_id()
from app.services.order_extractor import extract_order_id


def test_extract_order_id_from_plain_text():
    assert extract_order_id("JD10001") == "JD10001"


def test_extract_order_id_from_sentence():
    assert extract_order_id("帮我查一下订单JD10001到哪了") == "JD10001"


def test_extract_order_id_not_found():
    assert extract_order_id("帮我查一下我的订单") is None


def test_extract_order_id_multiple_words():
    assert extract_order_id("你好，订单号是JD88888，帮我看一下") == "JD88888"