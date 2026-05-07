import os
from contextlib import contextmanager

from utils.config_handler import db_conf


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
