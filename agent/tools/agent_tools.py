import csv
import os
import os.path
from datetime import datetime
from utils.logger_handler import logger
from rag.rag_service import RagSummarizeService
from langchain_core.tools import tool
import random
from utils.config_handler import agent_conf
from utils.path_tools import get_abs_path
from utils.db_handler import fetch_usage_record


rag = RagSummarizeService()
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
external_data = {}


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query:str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city:str) -> str:
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时内降雨概率极低"

@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    return random.choice(["深圳", "合肥", "杭州"])

@tool(description="获取用户的id，以纯字符串的形式返回")
def get_user_id():
    return os.environ.get("AGENT_DEMO_USER_ID", user_ids[0])

@tool(description="获取当前月份，以纯字符串的形式返回")
def get_current_month() -> str:
    return os.environ.get("AGENT_DEMO_MONTH", agent_conf.get("demo_month", datetime.now().strftime("%Y-%m")))

def generate_external_data():
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部文件数据{external_data_path}不存在")
        with open(external_data_path, "r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                user_id: str = row["用户ID"]
                feature: str = row["特征"]
                efficiency: str = row["清洁效率"]
                consumables: str = row["耗材"]
                comparison: str = row["对比"]
                time: str = row["时间"]
                if user_id not in external_data:
                    external_data[user_id] = {}
                external_data[user_id][time] = {
                    "特征":feature,
                    "效率":efficiency,
                    "耗材":consumables,
                    "对比":comparison,
                }





@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串的形式返回，如果未检索到返回空字符串")
def fetch_external_data(user_id:str,month:str) -> str:
    try:
        record = fetch_usage_record(user_id, month)
        if record:
            return {
                "特征": record["feature"],
                "效率": record["efficiency"],
                "耗材": record["consumables"],
                "对比": record["comparison"],
            }
    except Exception as e:
        logger.warning(f"[fetch_external_data]MySQL查询失败，回退CSV数据源：{str(e)}")

    generate_external_data()

    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}使用记录数据")
        return ""

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成场景动态注入上下文信息，为后续提示词切换提供上下文支撑")
def fill_context_for_report():
    return "fill_context_for_report已调用"





