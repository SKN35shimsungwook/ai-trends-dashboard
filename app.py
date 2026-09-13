"""AI 최신 동향(Latest AI Trends) 탐색 대시보드.

data/generate_ai_trends_data.py 로 만든 CSV를 SQLite DB(ai_trends.db)로
적재한 뒤, 이 앱에서 SQLite DB를 조회하여 필터링·시각화·상세 조회를 제공한다.
"""

import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd

import streamlit as st
from database import DB_PATH, build_database

st.set_page_config(
    page_title="AI 최신 동향 대시보드",
    page_icon=":material/smart_toy:",
    layout="wide",
)


@st.cache_resource(show_spinner="데이터베이스를 준비하는 중...")
def ensure_database() -> Path:
    if not DB_PATH.exists():
        build_database()
    return DB_PATH


@st.cache_data(show_spinner="AI 동향 데이터를 불러오는 중...")
def load_data() -> pd.DataFrame:
    db_path = ensure_database()
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM trends", conn)
    df["date"] = pd.to_datetime(df["date"])
    return df


df_full = load_data()

"# :material/smart_toy: AI 최신 동향 대시보드"
"AI 산업 트렌드 100건을 정리해 SQLite 데이터베이스로 구축하고, 조건별로 탐색할 수 있는 대시보드입니다."

st.space("medium")

with st.sidebar:
    st.header("필터")

    categories = sorted(df_full["category"].unique())
    selected_categories = st.multiselect("카테고리", categories, default=categories)

    regions = sorted(df_full["region"].unique())
    selected_regions = st.multiselect("지역", regions, default=regions)

    stages = sorted(df_full["trend_stage"].unique())
    selected_stages = st.multiselect("성숙 단계", stages, default=stages)

    min_impact, max_impact = int(df_full["impact_score"].min()), int(df_full["impact_score"].max())
    impact_range = st.slider("영향도 점수", min_impact, max_impact, (min_impact, max_impact))

    min_date, max_date = df_full["date"].min().date(), df_full["date"].max().date()
    date_range = st.date_input(
        "기간", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )

    keyword = st.text_input("키워드 검색", placeholder="예: 에이전트, 반도체, 규제...")

mask = (
    df_full["category"].isin(selected_categories)
    & df_full["region"].isin(selected_regions)
    & df_full["trend_stage"].isin(selected_stages)
    & df_full["impact_score"].between(*impact_range)
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    mask &= df_full["date"].between(pd.Timestamp(start_d), pd.Timestamp(end_d))
elif isinstance(date_range, tuple) and len(date_range) == 1:
    mask &= df_full["date"] >= pd.Timestamp(date_range[0])

if keyword.strip():
    text_cols = ["title", "summary", "detailed_description", "key_players", "tags"]
    kw_mask = pd.Series(False, index=df_full.index)
    for col in text_cols:
        kw_mask |= df_full[col].str.contains(keyword.strip(), case=False, na=False, regex=False)
    mask &= kw_mask

df = df_full[mask]

if df.empty:
    st.warning("조건에 맞는 데이터가 없습니다. 필터를 조정해보세요.", icon=":material/warning:")
    st.stop()

with st.container(horizontal=True):
    st.metric("전체 트렌드 수", f"{len(df)}건", border=True)
    st.metric("카테고리 수", f"{df['category'].nunique()}개", border=True)
    st.metric("평균 영향도", f"{df['impact_score'].mean():.2f} / 5", border=True)
    mainstream_share = (df["trend_stage"] == "주류화").mean() * 100
    st.metric("주류화 단계 비중", f"{mainstream_share:.0f}%", border=True)

st.space("medium")

col1, col2 = st.columns(2)

with col1.container(border=True, height="stretch"):
    "### :material/bar_chart: 카테고리별 트렌드 수"
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    st.altair_chart(
        alt.Chart(cat_counts)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="건수"),
            y=alt.Y("category:N", sort="-x", title=None),
            tooltip=["category", "count"],
        )
    )

with col2.container(border=True, height="stretch"):
    "### :material/public: 지역별 분포"
    region_counts = df["region"].value_counts().reset_index()
    region_counts.columns = ["region", "count"]
    st.altair_chart(
        alt.Chart(region_counts)
        .mark_arc()
        .encode(theta="count:Q", color="region:N", tooltip=["region", "count"])
        .configure_legend(orient="bottom")
    )

col3, col4 = st.columns(2)

with col3.container(border=True, height="stretch"):
    "### :material/timeline: 월별 트렌드 등록 추이"
    monthly = df.set_index("date").resample("MS").size().reset_index(name="count")
    st.line_chart(monthly, x="date", y="count", height=300)

with col4.container(border=True, height="stretch"):
    "### :material/trending_up: 성숙 단계 분포"
    stage_counts = df["trend_stage"].value_counts().reset_index()
    stage_counts.columns = ["trend_stage", "count"]
    st.altair_chart(
        alt.Chart(stage_counts)
        .mark_bar()
        .encode(
            x=alt.X("trend_stage:N", title=None, sort="-y"),
            y=alt.Y("count:Q", title="건수"),
            tooltip=["trend_stage", "count"],
        )
    )

st.space("medium")

with st.container(border=True):
    "### :material/table: 트렌드 목록"
    table_df = df[
        ["date", "category", "subcategory", "region", "title", "impact_score", "trend_stage", "source_type"]
    ].sort_values("date", ascending=False)

    st.dataframe(
        table_df,
        hide_index=True,
        width="stretch",
        column_config={
            "date": st.column_config.DateColumn("날짜"),
            "category": "카테고리",
            "subcategory": "세부분야",
            "region": "지역",
            "title": "제목",
            "impact_score": st.column_config.ProgressColumn("영향도", min_value=0, max_value=5),
            "trend_stage": "단계",
            "source_type": "출처유형",
        },
    )

    st.download_button(
        "필터링된 데이터 CSV로 내려받기",
        data=df.sort_values("date", ascending=False).to_csv(index=False).encode("utf-8-sig"),
        file_name="ai_trends_filtered.csv",
        mime="text/csv",
        icon=":material/download:",
    )

st.space("medium")

with st.container(border=True):
    "### :material/article: 상세 보기"
    ordered = df.sort_values("date", ascending=False)
    selected_title = st.selectbox("트렌드를 선택하세요", ordered["title"].tolist())
    row = ordered[ordered["title"] == selected_title].iloc[0]

    st.markdown(f"**{row['title']}**")
    st.caption(
        f"{row['category']} · {row['subcategory']} · {row['region']} · "
        f"{row['date'].date()} · 영향도 {row['impact_score']}/5 · {row['source_type']}"
    )
    st.write(row["summary"])
    with st.expander("상세 설명 보기", expanded=True):
        st.write(row["detailed_description"])
        st.markdown(f"**시사점:** {row['implication']}")
        st.markdown(f"**주요 플레이어:** {row['key_players']}")
