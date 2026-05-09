import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.db_handler import get_mysql_config, mysql_connection
from utils.path_tools import get_abs_path


SEED_PATH = Path(get_abs_path("data/mysql_seed.json"))
SCHEMA_PATH = Path(get_abs_path("scripts/create_usage_records_mysql.sql"))
TABLES = [
    "users",
    "devices",
    "usage_records",
    "knowledge_files",
    "chat_sessions",
    "chat_messages",
    "tool_call_logs",
    "report_records",
]
TRUNCATE_ORDER = [
    "chat_messages",
    "tool_call_logs",
    "report_records",
    "chat_sessions",
    "usage_records",
    "knowledge_files",
    "devices",
    "users",
]


def create_database():
    conf = get_mysql_config()
    with mysql_connection(database=None) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{conf['database']}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()


def execute_sql_file(path: Path):
    sql_text = path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    with mysql_connection(database=None) as conn:
        with conn.cursor() as cursor:
            for stmt in statements:
                cursor.execute(stmt)
        conn.commit()


def truncate_tables(cursor):
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    for table in TRUNCATE_ORDER:
        cursor.execute(f"TRUNCATE TABLE `{table}`")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")


def insert_rows(cursor, table: str, rows: list[dict]):
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(f"`{column}`" for column in columns)
    sql = f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders})"
    values = [tuple(row.get(column) for column in columns) for row in rows]
    cursor.executemany(sql, values)


def main():
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"未找到初始化数据文件：{SEED_PATH}")

    create_database()
    execute_sql_file(SCHEMA_PATH)
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            truncate_tables(cursor)
            for table in TABLES:
                insert_rows(cursor, table, payload["tables"].get(table, []))
        conn.commit()

    print(f"已从 JSON 导入 MySQL 初始化数据：{SEED_PATH}")
    for table in TABLES:
        print(f"{table}: {len(payload['tables'].get(table, []))}")


if __name__ == "__main__":
    main()
