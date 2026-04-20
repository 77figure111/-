#加“转人工”策略
"""
这些问题会触发转人工建议：
“我要投诉你们”
“我要赔偿”
“订单 JD99999 怎么查不到”
"""
def should_escalate(user_query:str,answer_text:str):
    escalate_keywords=["投诉", "赔偿", "人工", "举报", "欺骗", "生气", "差评"]
    if any(k in user_query for k in escalate_keywords):
        return True
    if "抱歉，没有查询到" in answer_text:
        return True
    return False