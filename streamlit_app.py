import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import datetime
import csv

# ---- 페이지 설정 ----
st.set_page_config(page_title="부동산 임장 기록 챗봇 🏢", layout="centered")
st.title("🏠 부동산 임장 기록 챗봇")
st.markdown("<p style='opacity:0.7;'>방문한 부동산 기록을 체계적으로 CSV에 저장할 수 있습니다.</p>", unsafe_allow_html=True)

# ---- 사이드바: OpenAI API 키 ----
st.sidebar.title("설정")
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key)
if not st.session_state.api_key:
    st.sidebar.warning("API 키를 입력해야 사용 가능합니다.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# ---- 세션 상태 초기화 ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", 
         "content": (
            "당신은 부동산 투자 전문가이자 기록 관리자입니다. "
            "사용자가 입력한 방문 정보를 CSV 컬럼에 맞춰 정리해 주세요. "
            "CSV 컬럼: 날짜,아파트 이름,주소,관심 평형,부동산 유형,건물 연식,층수,매매가,월세,관리비,"
            "대출 가능 여부,교통 편의성,생활 편의시설,개발 호재,내부 상태,외관 상태,안전/보안,"
            "예상 수익률,공실 가능성,임대 수요,투자 적합성,개인 코멘트"
         )
        }
    ]

# ---- CSV 파일 경로 ----
csv_file = "real_estate_records.csv"
csv_columns = ["날짜","아파트 이름","주소","관심 평형","부동산 유형","건물 연식","층수",
               "매매가","월세","관리비","대출 가능 여부","교통 편의성","생활 편의시설",
               "개발 호재","내부 상태","외관 상태","안전/보안","예상 수익률",
               "공실 가능성","임대 수요","투자 적합성","개인 코멘트"]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = st.session_state.messages[:1]
    st.experimental_rerun()

# ---- 사용자 입력 ----
st.markdown("### 💬 오늘 방문한 곳 기록 입력")
user_input = st.text_input("예: 서울 강남 자이 84m² 아파트 방문, 10층, 매매가 10억, 내부 신축...", key="user_input")

if user_input:
    # AI에 전달할 메시지 생성
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # AI 응답 생성
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_message})

        with st.chat_message("assistant"):
            st.markdown(ai_message)

        # ---- AI 메시지를 CSV로 변환하여 저장 ----
        # AI가 CSV 행 형식으로 반환한다고 가정 (콤마 구분)
        row_values = [v.strip() for v in ai_message.split(",")]
        if len(row_values) == len(csv_columns):
            # CSV 파일이 없으면 새로 생성
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(csv_columns)
                writer.writerow(row_values)
            st.success("✅ 기록이 CSV에 저장되었습니다!")
        else:
            st.warning("⚠️ AI 응답 형식이 CSV 컬럼과 일치하지 않습니다. 확인이 필요합니다.")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# ---- CSV 기록 확인 ----
st.markdown("### 📊 현재 저장된 기록")
if os.path.isfile(csv_file):
    df_records = pd.read_csv(csv_file)
    st.dataframe(df_records)
else:
    st.info("아직 기록이 없습니다.")
