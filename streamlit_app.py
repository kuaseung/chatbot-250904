import streamlit as st
import pandas as pd
import requests
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="부동산 투자 챗봇 🏠", page_icon="🏢", layout="centered")

st.title("🏠 부동산 투자 챗봇")
st.markdown("<p style='opacity:0.7;'>실제 실거래가 데이터를 기반으로 투자 정보를 제공합니다.</p>", unsafe_allow_html=True)

# ---- 사이드바 - OpenAI API 키 ----
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
        {
            "role": "system",
            "content": (
                "당신은 부동산 투자 전문가입니다. "
                "사용자가 입력한 지역과 조건을 바탕으로, "
                "실제 실거래가 데이터를 활용하여 투자 정보를 제공합니다. "
                "잘 모르는 정보는 모른다고 답합니다."
            )
        }
    ]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = st.session_state.messages[:1]
    st.experimental_rerun()

# ---- 실거래가 데이터 불러오기 ----
def fetch_real_transaction_data(region):
    # 공공데이터 포털 API를 통해 실거래가 데이터를 가져옵니다.
    # 예시 URL: "https://api.odcloud.kr/api/RealEstateTradingPrice/v1/getRealEstateTradingPrice"
    # 실제 API URL과 파라미터는 공공데이터 포털에서 확인하세요.
    url = "https://api.odcloud.kr/api/RealEstateTradingPrice/v1/getRealEstateTradingPrice"
    params = {
        "serviceKey": "YOUR_API_KEY",  # 공공데이터 포털에서 발급받은 서비스 키
        "page": 1,
        "perPage": 10,
        "cond[지역명::eq]": region
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# ---- 지역 선택 ----
st.markdown("### 📍 투자 지역 선택")
region = st.selectbox("지역을 선택하세요", ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])

# 선택한 지역 실거래가 데이터 표시
st.markdown(f"**선택한 지역: {region}**")
real_transaction_data = fetch_real_transaction_data(region)
st.write(real_transaction_data)

# ---- 사용자 질문 입력 ----
st.markdown("### 💬 질문을 입력하세요")
question = st.text_input("질문을 입력하세요...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_message})

        with st.chat_message("assistant"):
            st.markdown(ai_message)

    except Exception:
        st.error("❌ 오류 발생: 올바른 API 키를 입력했는지 확인해주세요.")
