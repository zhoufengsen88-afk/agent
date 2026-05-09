import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.db_handler import get_mysql_config, mysql_connection
from utils.file_handler import get_file_md5_hex
from utils.path_tools import get_abs_path


CSV_PATH = Path(get_abs_path("data/external/records.csv"))
DATA_DIR = Path(get_abs_path("data"))
SCHEMA_PATH = Path(get_abs_path("scripts/create_usage_records_mysql.sql"))
MODEL_NAMES = ["ZST-S1", "ZST-MopPro", "ZST-Lite", "ZST-NaviMax", "ZST-CleanX"]
CITIES = ["深圳", "合肥", "杭州", "南宁", "广州"]


def create_database():
    conf = get_mysql_config()
    with mysql_connection(database=None) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{conf['database']}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()


def split_feature(feature: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in feature.split("|")]
    house_area = parts[0] if len(parts) > 0 else ""
    family_profile = parts[1] if len(parts) > 1 else ""
    floor_type = parts[2] if len(parts) > 2 else ""
    return house_area, family_profile, floor_type


def has_pet(feature: str) -> int:
    return int(any(word in feature for word in ["猫", "狗", "宠"]))


def execute_sql_file(path: Path):
    sql_text = path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    with mysql_connection(database=None) as conn:
        with conn.cursor() as cursor:
            for stmt in statements:
                cursor.execute(stmt)
        conn.commit()


def ensure_usage_records_columns():
    conf = get_mysql_config()
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{conf['table']}` LIKE 'device_id'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE `{conf['table']}` ADD COLUMN `device_id` VARCHAR(50) NULL AFTER `user_id`")
                cursor.execute(f"ALTER TABLE `{conf['table']}` ADD KEY `idx_usage_device_month` (`device_id`, `record_month`)")
        conn.commit()


def load_csv_rows() -> list[dict]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def import_users(rows: list[dict]) -> int:
    sql = """
        INSERT INTO users (user_id, nickname, city)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nickname = VALUES(nickname),
            city = VALUES(city)
    """
    user_ids = sorted({row["用户ID"] for row in rows})
    values = [
        (user_id, f"用户{user_id}", CITIES[index % len(CITIES)])
        for index, user_id in enumerate(user_ids)
    ]
    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, values)
        conn.commit()
    return len(values)


def import_devices(rows: list[dict]) -> int:
    sql = """
        INSERT INTO devices
            (device_id, user_id, model_name, house_area, family_profile, floor_type, has_pet, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
        ON DUPLICATE KEY UPDATE
            model_name = VALUES(model_name),
            house_area = VALUES(house_area),
            family_profile = VALUES(family_profile),
            floor_type = VALUES(floor_type),
            has_pet = VALUES(has_pet),
            status = VALUES(status)
    """
    first_record_by_user = {}
    for row in rows:
        first_record_by_user.setdefault(row["用户ID"], row)

    values = []
    for index, (user_id, row) in enumerate(sorted(first_record_by_user.items())):
        feature = row["特征"]
        house_area, family_profile, floor_type = split_feature(feature)
        values.append((
            f"DEV-{user_id}-001",
            user_id,
            MODEL_NAMES[index % len(MODEL_NAMES)],
            house_area,
            family_profile,
            floor_type,
            has_pet(feature),
        ))

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, values)
        conn.commit()
    return len(values)


def import_usage_records(rows: list[dict]) -> int:
    conf = get_mysql_config()
    sql = f"""
        INSERT INTO `{conf['table']}`
            (user_id, device_id, feature, efficiency, consumables, comparison, record_month)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            device_id = VALUES(device_id),
            feature = VALUES(feature),
            efficiency = VALUES(efficiency),
            consumables = VALUES(consumables),
            comparison = VALUES(comparison)
    """
    values = [
        (
            row["用户ID"],
            f"DEV-{row['用户ID']}-001",
            row["特征"],
            row["清洁效率"],
            row["耗材"],
            row["对比"],
            row["时间"],
        )
        for row in rows
    ]

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, values)
        conn.commit()
    return len(values)


def import_knowledge_files() -> int:
    sql = """
        INSERT INTO knowledge_files
            (file_name, file_path, file_type, md5_hash, file_size, import_status)
        VALUES (%s, %s, %s, %s, %s, 'imported')
        ON DUPLICATE KEY UPDATE
            md5_hash = VALUES(md5_hash),
            file_size = VALUES(file_size),
            import_status = VALUES(import_status)
    """
    values = []
    for path in sorted(DATA_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in [".txt", ".pdf"]:
            continue
        values.append((
            path.name,
            str(path.relative_to(ROOT)).replace("\\", "/"),
            path.suffix.lower().lstrip("."),
            get_file_md5_hex(str(path)),
            path.stat().st_size,
        ))

    if not values:
        return 0

    with mysql_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, values)
        conn.commit()
    return len(values)


def main():
    create_database()
    execute_sql_file(SCHEMA_PATH)
    ensure_usage_records_columns()
    rows = load_csv_rows()
    user_count = import_users(rows)
    device_count = import_devices(rows)
    usage_count = import_usage_records(rows)
    knowledge_count = import_knowledge_files()
    conf = get_mysql_config()
    print(f"数据库初始化完成：{conf['database']}")
    print(f"用户：{user_count} 条，设备：{device_count} 条，使用记录：{usage_count} 条，知识文件：{knowledge_count} 条")


if __name__ == "__main__":
    main()
