import os
import json
import uuid
from contextlib import contextmanager

from utils.config_handler import db_conf
from utils.logger_handler import logger


def _load_pymysql():
    try:
        import pymysql
        return pymysql
    except ImportError as e:
        raise RuntimeError("缺少 PyMySQL 依赖，请先执行：pip install pymysql") from e


def get_mysql_config() -> dict:
    mysql_conf = db_conf["mysql"]
    return {
        "host": mysql_conf.get("host", "localhost"),
        "port": int(mysql_conf.get("port", 3306)),
        "database": mysql_conf["database"],
        "user": mysql_conf.get("user", "root"),
        "password": os.environ.get(mysql_conf.get("password_env", "MYSQL_PASSWORD"), ""),
        "charset": mysql_conf.get("charset", "utf8mb4"),
        "table": mysql_conf.get("usage_records_table", "usage_records"),
    }


@contextmanager
def mysql_connection(database: str | None = None):
    pymysql = _load_pymysql()
    conf = get_mysql_config()
    conn = pymysql.connect(
        host=conf["host"],
        port=conf["port"],
        user=conf["user"],
        password=conf["password"],
        database=database if database is not None else conf["database"],
        charset=conf["charset"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        yield conn
    finally:
        conn.close()


def fetch_usage_record(user_id: str, month: str) -> dict | None:
    conf = get_mysql_config()
    sql = f"""
        SELECT feature, efficiency, consumables, comparison
        FROM `{conf["table"]}`
        WHERE user_id = %s AND record_month = %s
        LIMIT 1
    """
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, month))
            return cursor.fetchone()


def create_chat_session(user_id: str, title: str = "智能客服会话") -> str:
    session_id = uuid.uuid4().hex
    sql = """
        INSERT INTO chat_sessions (session_id, user_id, title)
        VALUES (%s, %s, %s)
    """
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (session_id, user_id, title))
        conn.commit()
    return session_id


def save_chat_message(session_id: str, role: str, content: str) -> None:
    sql = """
        INSERT INTO chat_messages (session_id, role, content)
        VALUES (%s, %s, %s)
    """
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (session_id, role, content))
        conn.commit()


def save_tool_call_log(
        session_id: str | None,
        tool_name: str,
        tool_args,
        tool_result=None,
        success: bool = True,
        error_message: str | None = None,
) -> None:
    sql = """
        INSERT INTO tool_call_logs
            (session_id, tool_name, tool_args, tool_result, success, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    args_text = json.dumps(tool_args, ensure_ascii=False, default=str)
    result_text = "" if tool_result is None else json.dumps(tool_result, ensure_ascii=False, default=str)
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (session_id, tool_name, args_text, result_text, int(success), error_message))
        conn.commit()


def save_report_record(user_id: str, record_month: str, report_content: str, device_id: str | None = None) -> None:
    sql = """
        INSERT INTO report_records (report_id, user_id, device_id, record_month, report_content)
        VALUES (%s, %s, %s, %s, %s)
    """
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (uuid.uuid4().hex, user_id, device_id, record_month, report_content))
        conn.commit()


def safe_create_chat_session(user_id: str, title: str = "智能客服会话") -> str | None:
    try:
        return create_chat_session(user_id, title)
    except Exception as e:
        logger.warning(f"[db]创建会话失败，跳过数据库记录：{str(e)}")
        return None


def safe_save_chat_message(session_id: str | None, role: str, content: str) -> None:
    if not session_id:
        return
    try:
        save_chat_message(session_id, role, content)
    except Exception as e:
        logger.warning(f"[db]保存聊天消息失败，跳过数据库记录：{str(e)}")


def safe_save_tool_call_log(
        session_id: str | None,
        tool_name: str,
        tool_args,
        tool_result=None,
        success: bool = True,
        error_message: str | None = None,
) -> None:
    try:
        save_tool_call_log(session_id, tool_name, tool_args, tool_result, success, error_message)
    except Exception as e:
        logger.warning(f"[db]保存工具调用日志失败，跳过数据库记录：{str(e)}")


def safe_save_report_record(
        user_id: str,
        record_month: str,
        report_content: str,
        device_id: str | None = None,
) -> None:
    try:
        save_report_record(user_id, record_month, report_content, device_id)
    except Exception as e:
        logger.warning(f"[db]保存报告记录失败，跳过数据库记录：{str(e)}")
