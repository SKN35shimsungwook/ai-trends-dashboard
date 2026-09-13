"""
CSV -> SQLite 데이터베이스 변환 모듈
====================================
data/ai_trends_raw.csv 파일을 읽어 ai_trends.db (SQLite)에
trends 테이블로 적재한다. Streamlit 앱은 이 DB 파일을 조회한다.

실행:
    python database.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ai_trends_raw.csv"
DB_PATH = BASE_DIR / "ai_trends.db"

TABLE_NAME = "trends"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    region TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    detailed_description TEXT NOT NULL,
    implication TEXT NOT NULL,
    key_players TEXT NOT NULL,
    trend_stage TEXT NOT NULL,
    impact_score INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    tags TEXT NOT NULL
);
"""


def build_database(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} 파일이 없습니다. 먼저 data/generate_ai_trends_data.py 를 실행하세요."
        )

    df = pd.read_csv(csv_path)

    with sqlite3.connect(db_path) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        conn.execute(CREATE_TABLE_SQL)
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_category ON {TABLE_NAME}(category)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_region ON {TABLE_NAME}(region)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_date ON {TABLE_NAME}(date)")
        conn.commit()

    print(f"DB 생성 완료: {db_path} ({len(df)}행)")


if __name__ == "__main__":
    build_database()
