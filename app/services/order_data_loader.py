#读出 3 个 json 文件
import json
from pathlib import Path
from app import config_data as config

PROJECT_ROOT = config.PROJECT_ROOT
def load_json(file_path:Path):
    with open(file_path,"r",encoding="utf-8") as f:
        return json.load(f)

def load_orders():
    return load_json(PROJECT_ROOT / "data" / "orders_mock" / "orders.json")
def load_logistics():
    return load_json(PROJECT_ROOT / "data" / "orders_mock" / "logistics.json")

def load_refunds():
    return load_json(PROJECT_ROOT / "data" / "orders_mock" / "refunds.json")

# if __name__=="__main__":
#     print(load_orders()[:5])
#     print(load_logistics()[:5])
#     print(load_refunds()[:5])