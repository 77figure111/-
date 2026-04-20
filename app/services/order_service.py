#写订单查询工具
"""
get_order_status(order_id)功能：根据订单号查订单状态
get_logistics_status(order_id)功能：根据订单号查物流状态
get_refund_status(order_id)功能：根据订单号查退款状态
"""

from app.services.order_data_loader import load_orders, load_logistics, load_refunds
def get_order_status(order_id: str):
    orders=load_orders()
    for order in orders:
        if order["order_id"]==order_id:
            return order
    return None
def get_logistics_status(order_id: str):
    logistics_list=load_logistics()
    for item in logistics_list:
        if item["order_id"] == order_id:
            return item
    return None
def get_refund_status(order_id: str):
    refunds=load_refunds()
    for item in refunds:
        if item["order_id"] == order_id:
            return item
    return None

# if __name__ =="__main__":
#     print(get_order_status("JD10001"))
#     print(get_logistics_status("JD10002"))
#     print(get_refund_status("JD10003"))