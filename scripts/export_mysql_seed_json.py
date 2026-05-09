import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.db_handler import get_mysql_config, mysql_connection
from utils.path_tools import get_abs_path


SEED_PATH = Path(get_abs_path("data/mysql_seed.json"))
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


def json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ")
    return str(value)


def export_table(cursor, table: str) -> list[dict]:
    cursor.execute(f"SELECT * FROM `{table}` ORDER BY `id`")
    return cursor.fetchall()


def main():
    conf = get_mysql_config()
    payload = {
        "database": conf["database"],
        "exported_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "tables": {},
    }

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            for table in TABLES:
                payload["tables"][table] = export_table(cursor, table)

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=json_default),
        encoding="utf-8",
    )

    print(f"已导出 MySQL 初始化数据：{SEED_PATH}")
    for table in TABLES:
        print(f"{table}: {len(payload['tables'][table])}")


if __name__ == "__main__":
    main()
