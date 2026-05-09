import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.db_handler import mysql_connection


SESSIONS = [
    ("DEMO-SESSION-1001-001", "1001", "小户型选购咨询"),
    ("DEMO-SESSION-1002-001", "1002", "瓷砖地面拖地模式咨询"),
    ("DEMO-SESSION-1003-001", "1003", "宠物毛发清理咨询"),
    ("DEMO-SESSION-1004-001", "1004", "猫砂清理与主刷维护"),
    ("DEMO-SESSION-1005-001", "1005", "老人家庭定时清扫设置"),
    ("DEMO-SESSION-1006-001", "1006", "多层住宅使用建议"),
    ("DEMO-SESSION-1007-001", "1007", "边刷维护咨询"),
    ("DEMO-SESSION-1008-001", "1008", "滤网更换咨询"),
    ("DEMO-SESSION-1009-001", "1009", "扫拖一体报告查询"),
    ("DEMO-SESSION-1010-001", "1010", "机器人迷路故障排查"),
    ("DEMO-SESSION-1001-002", "1001", "本月使用报告生成"),
    ("DEMO-SESSION-1004-002", "1004", "养宠家庭保养建议"),
]

MESSAGES = {
    "DEMO-SESSION-1001-001": [
        ("user", "我家是65平小户型，适合买什么样的扫地机器人？"),
        ("assistant", "建议选择基础激光导航、机身轻薄、吸力不低于3000Pa的扫拖一体机型，尘盒和水箱容量适中即可。"),
    ],
    "DEMO-SESSION-1002-001": [
        ("user", "瓷砖地面适合每天开拖地模式吗？"),
        ("assistant", "瓷砖地面适合使用拖地模式，建议根据灰尘量选择中档水量，并定期清洗拖布，避免水渍残留。"),
    ],
    "DEMO-SESSION-1003-001": [
        ("user", "家里有狗，毛发比较多，怎么设置清扫效果更好？"),
        ("assistant", "建议开启强力吸尘模式并提高每周清扫频率，每次清扫后检查主刷和尘盒，宠物家庭耗材更换周期建议适当缩短。"),
    ],
    "DEMO-SESSION-1004-001": [
        ("user", "猫砂经常被带到客厅，机器人能处理吗？"),
        ("assistant", "可以处理少量猫砂，但建议开启重点清扫区域，并定期清理主刷缠绕物，猫砂颗粒较多时需要及时清空尘盒。"),
    ],
    "DEMO-SESSION-1005-001": [
        ("user", "老人不会用App，怎么让机器人自动清扫？"),
        ("assistant", "可以提前设置固定时间的定时清扫计划，并开启自动回充；如果设备支持语音控制，也可以绑定语音助手降低操作难度。"),
    ],
    "DEMO-SESSION-1006-001": [
        ("user", "复式房子能不能让扫地机器人跨楼层工作？"),
        ("assistant", "普通扫地机器人不能自主上下楼层，建议分别保存多楼层地图，人工移动设备后选择对应楼层地图再启动清扫。"),
    ],
    "DEMO-SESSION-1007-001": [
        ("user", "边刷多久清理一次比较合适？"),
        ("assistant", "建议每天观察边刷是否缠绕毛发或线头，每周拆下边刷做一次集中清理，磨损明显时及时更换。"),
    ],
    "DEMO-SESSION-1008-001": [
        ("user", "HEPA滤网还剩30%，需要马上换吗？"),
        ("assistant", "剩余30%时建议提前准备新滤网，如果出现吸力下降、异味或二次扬尘，应尽快更换。"),
    ],
    "DEMO-SESSION-1009-001": [
        ("user", "帮我查一下这个月的扫拖一体机器人使用情况。"),
        ("assistant", "已根据您的使用记录生成报告，重点关注清洁覆盖率、耗材状态和使用频率，并给出维护建议。"),
    ],
    "DEMO-SESSION-1010-001": [
        ("user", "机器人清扫时经常迷路怎么办？"),
        ("assistant", "建议检查传感器是否被灰尘遮挡，清理充电座周围障碍物，并重新建图；如果仍频繁迷路，可检查导航模块状态。"),
    ],
    "DEMO-SESSION-1001-002": [
        ("user", "生成我的本月扫地机器人使用报告。"),
        ("assistant", "已生成扫地机器人使用情况报告与保养建议，您的清洁覆盖率为84%，建议重点优化沙发底部和床底漏扫区域。"),
    ],
    "DEMO-SESSION-1004-002": [
        ("user", "养猫家庭主刷缠绕严重怎么办？"),
        ("assistant", "养猫家庭建议每次清扫后清理主刷毛发，每周拆洗滚刷仓，并适当缩短主刷和滤网更换周期。"),
    ],
}

TOOL_LOGS = [
    ("DEMO-SESSION-1001-001", "rag_summarize", '{"query":"小户型 扫地机器人 选购"}', "小户型建议选择激光导航、轻薄机身、吸力可调节机型。", 1),
    ("DEMO-SESSION-1002-001", "get_weather", '{"city":"合肥"}', "城市合肥天气为晴天，气温26摄氏度，空气湿度50%。", 1),
    ("DEMO-SESSION-1003-001", "rag_summarize", '{"query":"宠物毛发 扫地机器人 清理"}', "宠物家庭需及时清理主刷和尘盒，缩短耗材更换周期。", 1),
    ("DEMO-SESSION-1004-001", "rag_summarize", '{"query":"猫砂 主刷 缠绕 维护"}', "猫砂较多时建议重点清扫并及时清空尘盒。", 1),
    ("DEMO-SESSION-1005-001", "rag_summarize", '{"query":"老人 定时清扫 语音控制"}', "老人家庭建议配置定时清扫和语音控制。", 1),
    ("DEMO-SESSION-1006-001", "rag_summarize", '{"query":"多楼层 地图 扫地机器人"}', "多楼层场景需分别保存地图，人工移动设备。", 1),
    ("DEMO-SESSION-1008-001", "rag_summarize", '{"query":"HEPA滤网 更换 周期"}', "滤网寿命不足时应提前准备替换耗材。", 1),
    ("DEMO-SESSION-1009-001", "get_user_id", "{}", "1009", 1),
    ("DEMO-SESSION-1009-001", "get_current_month", "{}", "2025-07", 1),
    ("DEMO-SESSION-1009-001", "fetch_external_data", '{"user_id":"1009","month":"2025-07"}', "已返回用户1009在2025-07的使用记录。", 1),
    ("DEMO-SESSION-1010-001", "rag_summarize", '{"query":"扫地机器人 迷路 故障排查"}', "建议清理传感器、检查充电座位置并重新建图。", 1),
    ("DEMO-SESSION-1001-002", "get_user_id", "{}", "1001", 1),
    ("DEMO-SESSION-1001-002", "get_current_month", "{}", "2025-07", 1),
    ("DEMO-SESSION-1001-002", "fill_context_for_report", "{}", "fill_context_for_report已调用", 1),
    ("DEMO-SESSION-1001-002", "fetch_external_data", '{"user_id":"1001","month":"2025-07"}', "已返回用户1001在2025-07的使用记录。", 1),
    ("DEMO-SESSION-1004-002", "rag_summarize", '{"query":"养宠家庭 主刷缠绕 保养"}', "养宠家庭每次清扫后应检查主刷和尘盒。", 1),
]

REPORTS = [
    ("DEMO-REPORT-1001-2025-07", "1001", "DEV-1001-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1001本月覆盖率84%，日均清扫44㎡，建议重点处理沙发底部和床底漏扫区域，并提前准备HEPA滤网。"),
    ("DEMO-REPORT-1003-2025-07", "1003", "DEV-1003-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1003为养狗家庭，毛发清理表现良好，建议继续保持高频清扫并缩短主刷维护周期。"),
    ("DEMO-REPORT-1004-2025-07", "1004", "DEV-1004-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1004猫砂处理频率较高，主刷缠绕严重，建议更换防缠绕主刷并增加尘盒清理频率。"),
    ("DEMO-REPORT-1005-2025-07", "1005", "DEV-1005-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1005手动操作占比较高，建议启用定时清扫和语音控制功能。"),
    ("DEMO-REPORT-1008-2025-07", "1008", "DEV-1008-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1008滤网寿命偏低，建议提前准备耗材并检查吸力变化。"),
    ("DEMO-REPORT-1010-2025-07", "1010", "DEV-1010-001", "2025-07", "扫地机器人使用情况报告与保养建议：用户1010存在迷路和回充效率问题，建议清理传感器、优化充电座位置并重新建图。"),
]


def clear_old_seed_data(cursor):
    cursor.execute("DELETE FROM chat_messages WHERE session_id LIKE 'DEMO-SESSION-%'")
    cursor.execute("DELETE FROM tool_call_logs WHERE session_id LIKE 'DEMO-SESSION-%'")
    cursor.execute("DELETE FROM report_records WHERE report_id LIKE 'DEMO-REPORT-%'")
    cursor.execute("DELETE FROM chat_sessions WHERE session_id LIKE 'DEMO-SESSION-%'")


def seed_sessions(cursor):
    sql = """
        INSERT INTO chat_sessions (session_id, user_id, title)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            user_id = VALUES(user_id),
            title = VALUES(title)
    """
    cursor.executemany(sql, SESSIONS)


def seed_messages(cursor):
    rows = []
    for session_id, messages in MESSAGES.items():
        rows.extend((session_id, role, content) for role, content in messages)
    cursor.executemany(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
        rows,
    )
    return len(rows)


def seed_tool_logs(cursor):
    sql = """
        INSERT INTO tool_call_logs
            (session_id, tool_name, tool_args, tool_result, success)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, TOOL_LOGS)


def seed_reports(cursor):
    sql = """
        INSERT INTO report_records
            (report_id, user_id, device_id, record_month, report_content)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_content = VALUES(report_content)
    """
    cursor.executemany(sql, REPORTS)


def main():
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            clear_old_seed_data(cursor)
            seed_sessions(cursor)
            message_count = seed_messages(cursor)
            seed_tool_logs(cursor)
            seed_reports(cursor)
        conn.commit()

    print("演示运行数据填充完成")
    print(f"会话：{len(SESSIONS)} 条，消息：{message_count} 条，工具调用：{len(TOOL_LOGS)} 条，报告：{len(REPORTS)} 条")


if __name__ == "__main__":
    main()
