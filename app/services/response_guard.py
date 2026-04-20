from app.services.query_classifier import classify_query

def check_need_followup(user_query:str):
    query_type=classify_query(user_query)
    if query_type =="size":
        #如果用户的话里 没有 “身高” 两个字,need_height 就变成 True（需要问身高）
        need_height="身高" not in user_query
        #判断用户有没有提体重相关,如果都没有 → need_weight = True（需要问体重）
        need_weight="体重" not in user_query and "斤" not in user_query and "kg" not in user_query.lower()
        if need_weight or need_height:
            return {
                "action":"followup",# 告诉系统：执行“追问”动作
                "message" : "为了给你更准确的尺码建议，请告诉我你的身高、体重，以及你喜欢合身还是宽松一点。"
            }
        #如果身高体重都有了 → 不追问，直接继续回答。
        return {"action":"continue"}

def check_need_refuse(rag_context_text:str):
    if "无相关资料" in rag_context_text:
        return{
            "action":"refuse",
            "message":"抱歉，我目前没有足够依据回答这个问题，建议你换个问法，或者联系客服人工处理。"
        }
    return {"action":"continue"}
#只负责输出指令，不负责执行指令,判断 action 的代码不在这个文件里，在主程序 / 入口文件里

# if __name__ =="__main__":
#     user_query = input()
#     result = check_need_followup(user_query)
#     action = result["action"]
#     if action == "followup":
#         #执行追问
#         print("【机器人回复】", result["message"])
#     elif action == "refuse":
#         # 执行拒绝回答
#         print("【机器人回复】", result["message"])
#     elif action == "continue":
#         # 继续回答（去查知识库）
#         print("【机器人】继续查询资料并回答...")







