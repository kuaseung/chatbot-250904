import streamlit as st
import openai
from openai import OpenAI

st.sidebar.title("설정")

# 세션 상태에 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.sidebar.text_input(
    "🔑 OpenAI API Key", 
    type="password", 
    value=st.session_state.api_key
)

# API 키 확인
if not st.session_state.api_key:
    st.sidebar.warning("API 키를 입력해야 사용 가능합니다.")
    st.stop()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=st.session_state.api_key)

# 테스트 출력
st.write("✅ API 키가 정상적으로 입력되었습니다.")
