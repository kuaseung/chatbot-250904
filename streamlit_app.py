import streamlit as st
from openai import OpenAI
import re
import urllib.parse

# ---- 페이지 설정 ----
st.set_page_config(page_title="여행 챗봇 🌍", page_icon="✈️", layout="centered")

# ---- 앱 제목 ----
st.title("🌍 ChatGPT 여행 챗봇")
st.markdown("<p style='opacity:0.7;'>한국어 & 영어로 여행 관련 질문만 답변합니다.</p>", unsafe_allow_html=True)

# ---- 사이드바 - OpenAI API 키 ----
st.sidebar.title("설정")
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
st.session_state.api_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    type="password",
    value=st.session_state.api_key
)
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
                "한국어 & 영어로 제공하며, 여행 관련 질문에만 답합니다. "
                "없는 장소/음식점/관광지는 추천하지 않고, 잘 모르면 모른다고 답합니다."
            )
        }
    ]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = st.session_state.messages[:1]
    st.experimental_rerun()

# ---- 지도 링크 + iframe 생성 함수 ----
def generate_map_iframe(text: str):
    # 장소/음식점 이름 추출
    words = re.findall(r"[가-힣a-zA-Z0-9\s]+", text)
    iframes = []
    for word in words:
        word = word.strip()
        if len(word) > 1:
            encoded = urllib.parse.quote(word)
            kakao_url = f"https://map.kakao.com/?q={encoded}"
            naver_url = f"https://map.naver.com/v5/search/{encoded}"
            iframe_html = f"""
            <div style='margin-bottom:10px;'>
                <b>{word}</b><br>
                <iframe src="{kakao_url}" width="100%" height="300px" style="border:1px solid #ccc;"></iframe><br>
                <a href="{kakao_url}" target="_blank">카카오맵에서 보기</a> |
                <a href="{naver_url}" target="_blank">네이버지도에서 보기</a>
            </div>
            """
            iframes.append(iframe_html)
    return iframes

# ---- 검증 함수 ----
def validate_response(text: str):
    risky_phrases = ["없는", "허구", "가짜", "잘못된"]
    if any(phrase in text for phrase in risky_phrases):
        return "⚠️ 답변이 신뢰할 수 없을 수 있습니다. 다른 여행 정보를 물어봐주세요."
    return text

# ---- 대화 기록 출력 ----
st.markdown("### 📜 대화 기록")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"<div style='background-color: rgba(25,118,210,0.15); padding:10px; border-radius:10px; margin:5px 0; text-align:right; max-width:80%; float:right; clear:both;'>👤 {message['content']}</div>",
            unsafe_allow_html=True
        )
    elif message["role"] == "assistant":
        st.markdown(
            f"<div style='background-color: rgba(158,158,158,0.15); padding:10px; border-radius:10px; margin:5px 0; text-align:left; max-width:80%; float:left; clear:both;'>🤖 {message['content']}</div>",
            unsafe_allow_html=True
        )
        # 지도 iframe 표시
        iframes = generate_map_iframe(message['content'])
        for iframe in iframes:
            st.markdown(iframe, unsafe_allow_html=True)

# ---- 채팅 입력창 (엔터 전송) ----
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        response_message = validate_response(response.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": response_message})

        with st.chat_message("assistant"):
            st.markdown(response_message)

        # 지도 iframe 표시
        iframes = generate_map_iframe(response_message)
        for iframe in iframes:
            st.markdown(iframe, unsafe_allow_html=True)

    except Exception:
        st.error("❌ 오류 발생: 올바른 API 키를 입력했는지 확인해주세요.")
