def classify_query(user_query:str) ->str:
    text=user_query.lower()
    size_keywords=["尺码", "多大", "合适吗", "身高", "体重", "穿什么码"]
    logistics_keywords=["物流", "发货", "送到", "快递", "多久到", "订单到哪"]
    refund_keywords=["退款", "退货", "换货", "售后", "保修", "发票"]
    promotion_keywords=["优惠", "满减", "活动", "折扣", "优惠券"]
    product_keywords=["材质", "颜色", "款式", "适合", "面料", "参数"]
    order_keywords = ["订单", "订单号", "下单", "购买记录"]
    if any(k in text for k in size_keywords):
        return "size"
    if any(k in text for k in logistics_keywords):
        return "logistics_query"
    if any(k in text for k in refund_keywords):
        return "refund_query"
    if any(k in text for k in promotion_keywords):
        return "promotion"
    if any(k in text for k in product_keywords):
        return "product"
    if any(k in text for k in order_keywords):
        return "order_query"

    return "general"