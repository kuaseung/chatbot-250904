import streamlit as st
import pandas as pd
import os
import datetime
import csv

# ---- 페이지 설정 ----
st.set_page_config(page_title="부동산 임장 기록 챗봇 🏢", layout="centered")
st.title("🏠 부동산 임장 기록 챗봇")
st.markdown("<p style='opacity:0.7;'>방문한 부동산 기록을 체계적으로 CSV에 저장할 수 있습니다.</p>", unsafe_allow_html=True)

# ---- 대화 흐름(순차 질문) 설정 ----
# OpenAI 사용 대신 단계별 입력 방식을 사용합니다.
# ---- 세션 상태 초기화 ----
if "step" not in st.session_state:
    st.session_state.step = 0  # 현재 질문 단계 인덱스
if "answers" not in st.session_state:
    st.session_state.answers = {}  # 사용자가 입력한 값 저장

# ---- CSV 파일 경로 ----
csv_file = "real_estate_records.csv"
csv_columns = ["날짜","아파트 이름","주소","관심 평형","부동산 유형","건물 연식","층수",
               "매매가","월세","관리비","대출 가능 여부","교통 편의성","생활 편의시설",
               "개발 호재","내부 상태","외관 상태","안전/보안","예상 수익률",
               "공실 가능성","임대 수요","투자 적합성","개인 코멘트"]

# ---- 질문 메타데이터 (csv_columns와 동일 순서 유지를 권장) ----
scale_opts = ["매우 좋음","좋음","보통","나쁨"]
yn_opts = ["가능","불가","미정"]
type_opts = ["아파트","오피스텔","빌라","주택","상가","토지","기타"]

questions = [
    {"key": "날짜", "label": "방문 날짜", "type": "date", "default": datetime.date.today()},
    {"key": "아파트 이름", "label": "아파트/건물 이름", "type": "text"},
    {"key": "주소", "label": "주소", "type": "text"},
    {"key": "관심 평형", "label": "관심 평형(예: 84m²)", "type": "text"},
    {"key": "부동산 유형", "label": "부동산 유형", "type": "select", "options": type_opts},
    {"key": "건물 연식", "label": "건물 연식(년)", "type": "number"},
    {"key": "층수", "label": "층수", "type": "number"},
    {"key": "매매가", "label": "매매가(만원 단위 추천)", "type": "number"},
    {"key": "월세", "label": "월세(만원)", "type": "number"},
    {"key": "관리비", "label": "관리비(만원)", "type": "number"},
    {"key": "대출 가능 여부", "label": "대출 가능 여부", "type": "select", "options": yn_opts},
    {"key": "교통 편의성", "label": "교통 편의성", "type": "select", "options": scale_opts},
    {"key": "생활 편의시설", "label": "생활 편의시설", "type": "select", "options": scale_opts},
    {"key": "개발 호재", "label": "개발 호재(있다면 간단히)", "type": "text"},
    {"key": "내부 상태", "label": "내부 상태", "type": "select", "options": scale_opts},
    {"key": "외관 상태", "label": "외관 상태", "type": "select", "options": scale_opts},
    {"key": "안전/보안", "label": "안전/보안", "type": "select", "options": scale_opts},
    {"key": "예상 수익률", "label": "예상 수익률(예: 4~5%)", "type": "text"},
    {"key": "공실 가능성", "label": "공실 가능성", "type": "select", "options": scale_opts},
    {"key": "임대 수요", "label": "임대 수요", "type": "select", "options": scale_opts},
    {"key": "투자 적합성", "label": "투자 적합성", "type": "select", "options": ["매우 적합","적합","보통","부적합"]},
    {"key": "개인 코멘트", "label": "개인 코멘트", "type": "textarea"},
]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 입력 초기화"):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.rerun()

# ---- 순차 질문 UI ----
st.markdown("### 💬 오늘 방문한 곳 정보를 단계별로 입력하세요")

current = st.session_state.step
total = len(questions)

if current < total:
    q = questions[current]
    st.markdown(f"**단계 {current+1}/{total}** — {q['label']}")

    # 기존 입력값 불러오기
    prev_val = st.session_state.answers.get(q["key"], None)

    # 위젯 렌더링
    widget_key = f"q_{current}"
    value = None
    if q["type"] == "text":
        value = st.text_input(q["label"], value=prev_val if isinstance(prev_val, str) else None, key=widget_key)
    elif q["type"] == "textarea":
        value = st.text_area(q["label"], value=prev_val if isinstance(prev_val, str) else None, key=widget_key)
    elif q["type"] == "number":
        value = st.number_input(q["label"], value=float(prev_val) if isinstance(prev_val, (int,float)) else 0.0, step=1.0, key=widget_key)
    elif q["type"] == "select":
        options = q.get("options", [])
        default_index = options.index(prev_val) if (prev_val in options) else 0
        value = st.selectbox(q["label"], options=options, index=default_index, key=widget_key)
    elif q["type"] == "date":
        default_date = prev_val if isinstance(prev_val, datetime.date) else q.get("default", datetime.date.today())
        value = st.date_input(q["label"], value=default_date, key=widget_key)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ 이전", disabled=(current == 0)):
            st.session_state.step = max(0, current - 1)
            st.rerun()

    with col2:
        if st.button("⏭️ 건너뛰기"):
            st.session_state.step = min(total, current + 1)
            st.rerun()

    with col3:
        if st.button("➡️ 다음"):
            # 값 저장 (date는 문자열로 저장)
            if isinstance(value, datetime.date):
                st.session_state.answers[q["key"]] = value.isoformat()
            else:
                st.session_state.answers[q["key"]] = value
            st.session_state.step = min(total, current + 1)
            st.rerun()
else:
    st.success("모든 항목 입력이 완료되었습니다. 아래 요약을 확인하고 CSV로 저장하세요.")

    # 요약 테이블 생성
    row_values = []
    for col in csv_columns:
        v = st.session_state.answers.get(col, "")
        # 숫자형은 int로 표시 가능
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        row_values.append(v)

    df_preview = pd.DataFrame([row_values], columns=csv_columns)
    st.dataframe(df_preview, use_container_width=True)

    colA, colB = st.columns(2)
    with colA:
        if st.button("✏️ 수정하기"):
            # 마지막 항목으로 이동하여 필요한 항목 수정하도록 유도
            st.session_state.step = max(0, total - 1)
            st.rerun()
    with colB:
        if st.button("💾 CSV 저장"):
            try:
                file_exists = os.path.isfile(csv_file)
                with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(csv_columns)
                    writer.writerow([str(v) if v is not None else "" for v in row_values])
                st.success("✅ 기록이 CSV에 저장되었습니다!")
                # 입력 초기화
                st.session_state.step = 0
                st.session_state.answers = {}
                st.rerun()
            except Exception as e:
                st.error(f"❌ 저장 중 오류가 발생했습니다: {e}")

# ---- CSV 기록 확인 ----
st.markdown("### 📊 현재 저장된 기록")
if os.path.isfile(csv_file):
    df_records = pd.read_csv(csv_file)
    st.dataframe(df_records)
else:
    st.info("아직 기록이 없습니다.")
