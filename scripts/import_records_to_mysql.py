import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.db_handler import get_mysql_config, mysql_connection
from utils.path_tools import get_abs_path


CSV_PATH = Path(get_abs_path("data/external/records.csv"))


def create_database():
    conf = get_mysql_config()
    with mysql_connection(database=None) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{conf['database']}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()


def create_table():
    conf = get_mysql_config()
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS `{conf['table']}` (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(20) NOT NULL,
                    feature TEXT,
                    efficiency TEXT,
                    consumables TEXT,
                    comparison TEXT,
                    record_month CHAR(7) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_user_month (user_id, record_month)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        conn.commit()


def import_records():
    conf = get_mysql_config()
    sql = f"""
        INSERT INTO `{conf['table']}`
            (user_id, feature, efficiency, consumables, comparison, record_month)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            feature = VALUES(feature),
            efficiency = VALUES(efficiency),
            consumables = VALUES(consumables),
            comparison = VALUES(comparison)
    """
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [
            (
                row["用户ID"],
                row["特征"],
                row["清洁效率"],
                row["耗材"],
                row["对比"],
                row["时间"],
            )
            for row in csv.DictReader(f)
        ]

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, rows)
        conn.commit()
    return len(rows)


def main():
    create_database()
    create_table()
    count = import_records()
    conf = get_mysql_config()
    print(f"已导入 {count} 条记录到 MySQL：{conf['database']}.{conf['table']}")


if __name__ == "__main__":
    main()
