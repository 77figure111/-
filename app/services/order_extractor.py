#“订单号提取”函数
"""
文本信息抽取
正则表达式基础
输入规范化
extract_order_id(text: str)功能：从用户输入里提取订单号
"""
import re
def extract_order_id(text: str):
    text = text.strip().upper()
    pattern=r"(JD\d{5,})"
    match=re.search(pattern,text)
    if match:
        return match.group(1)
    return None

# if __name__ =="__main__":
#     print(extract_order_id("帮我查一下订单JD10001到哪了"))