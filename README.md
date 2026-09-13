# AI 최신 동향 대시보드

AI 산업의 주요 트렌드를 정리한 데이터셋을 SQLite 데이터베이스로 구축하고,
Streamlit으로 조회·필터링·시각화하는 대시보드입니다.

## 데이터 개요

- 생성형 AI·LLM, AI 에이전트, 멀티모달 AI, AI 반도체·인프라, 온디바이스·엣지 AI,
  AI 규제·정책, 오픈소스 AI, 산업별 AI 도입, 로보틱스·피지컬 AI, AI 안전성·윤리·인재
  **10개 대분류 x 10개 항목 = 총 100개 트렌드**를 정리했습니다.
- 각 항목은 제목/요약/상세설명/시사점/핵심 플레이어/지역/시점/영향도(1~5)/성숙 단계 등을
  포함해, 단순 표가 아니라 보고서 한 섹션 분량의 정보를 담고 있습니다.
- 2026년 상반기 기준으로 공개적으로 널리 보도·연구된 AI 산업 동향을 바탕으로
  작성했으며, 특정 기업의 미공개 정보나 확정되지 않은 수치는 포함하지 않았습니다.
  실제 리서치/과제 제출용으로 쓰실 경우, 최신 사실관계는 원문 기사·보고서로
  교차 확인하시는 것을 권장합니다.

## 폴더 구조

```
ai_trends_dashboard/
├── app.py                          # Streamlit 대시보드 (엔트리 포인트)
├── database.py                     # CSV -> SQLite 변환 모듈
├── data/
│   └── generate_ai_trends_data.py  # 원본 CSV 생성 스크립트 (100개 트렌드 데이터)
├── ai_trends_raw.csv               # 생성된 CSV (데이터베이스화 이전 원본)
├── ai_trends.db                    # SQLite 데이터베이스 (app.py가 조회하는 대상)
├── requirements.txt
└── .streamlit/
```

## 1) VSCode에서 로컬 실행하기

### 사전 준비
- Python 3.9 이상
- (권장) VSCode에서 이 폴더(`ai_trends_dashboard`)를 열고, Python 인터프리터를 선택

### 설치 및 실행

```bash
# 1. (선택) 가상환경 생성
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. (선택) CSV/DB를 직접 재생성하고 싶을 때
python data/generate_ai_trends_data.py   # ai_trends_raw.csv 생성
python database.py                       # ai_trends.db 생성

# 4. 앱 실행
streamlit run app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 출력되는
`http://localhost:8501` 주소로 직접 접속하세요.

> `app.py`는 `ai_trends.db`가 없으면 실행 시 자동으로 `ai_trends_raw.csv`로부터
> 데이터베이스를 다시 생성하므로, DB 파일을 지워도 앱은 정상 동작합니다.

## 2) Streamlit Community Cloud로 배포하기

1. 이 프로젝트 폴더를 GitHub 저장소에 푸시합니다. (레포 전체가 아니라
   `ai_trends_dashboard` 폴더만 별도 저장소로 만들어도 되고, 기존 저장소의
   서브폴더로 두어도 됩니다 — 후자의 경우 배포 시 "Main file path"를
   `ai_trends_dashboard/app.py`처럼 지정합니다.)
2. https://share.streamlit.io 에 GitHub 계정으로 로그인합니다.
3. **New app** 클릭 → 저장소/브랜치 선택 → Main file path에 `app.py`
   (서브폴더에 있다면 `ai_trends_dashboard/app.py`) 입력 → **Deploy**.
4. 별도 설정 없이 `requirements.txt`를 자동으로 읽어 패키지를 설치하고,
   `ai_trends.db`(또는 없다면 CSV로부터 자동 생성한 DB)를 사용해 앱을 띄웁니다.
5. 배포 후 코드를 GitHub에 push하면 앱이 자동으로 재배포됩니다.

## 3) 데이터를 직접 바꾸고 싶다면

`data/generate_ai_trends_data.py`의 `RAW_ITEMS` 리스트에 항목을 추가/수정한 뒤

```bash
python data/generate_ai_trends_data.py
python database.py
```

를 실행하면 `ai_trends_raw.csv`와 `ai_trends.db`가 갱신됩니다. 이후
`streamlit run app.py`를 다시 실행(또는 이미 실행 중이면 새로고침)하면
바뀐 데이터가 반영됩니다.

## 주요 기능

- 카테고리 / 지역 / 성숙 단계 / 영향도 점수 / 기간 / 키워드로 필터링
- KPI 카드(전체 건수, 카테고리 수, 평균 영향도, 주류화 비중)
- 카테고리별 건수, 지역별 분포, 월별 등록 추이, 성숙 단계 분포 차트
- 필터링된 데이터 테이블 및 CSV 다운로드
- 트렌드 선택 시 상세 설명·시사점·핵심 플레이어를 보여주는 상세 보기
