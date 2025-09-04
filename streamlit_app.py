import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(
    page_title="여행 챗봇 🌍",
    page_icon="✈️",
    layout="centered"
)

# ---- 앱 제목 ----
st.title("🌍 ChatGPT 여행 챗봇")
st.markdown(
    "<p style='opacity:0.7;'>한국어 & 영어로 여행 관련 질문만 답변합니다.</p>",
    unsafe_allow_html=True
)

# ---- 사이드바 - API 키 입력 ----
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

# OpenAI 클라이언트 생성
client = OpenAI(api_key=st.session_state.api_key)

# ---- 세션 상태 초기화 ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "기본적으로 한국어와 영어로 제공해 주세요. "
                "여행 관련 질문에만 답변하고, 없는 장소/음식점/관광지는 추천하지 마세요. "
                "잘 모르는 내용은 '모르겠다'라고 답변하세요."
            )
        }
    ]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = st.session_state.messages[:1]
    st.experimental_rerun()

# ---- 검증 함수 ----
def validate_response(text: str) -> str:
    risky_phrases = ["없는", "허구", "가짜", "잘못된"]
    if any(phrase in text for phrase in risky_phrases):
        return "⚠️ 답변이 신뢰할 수 없을 수 있습니다. 다른 여행 정보를 물어봐주세요."
    return text

# ---- 대화 기록 출력 ----
st.markdown("### 📜 대화 기록")

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div style='
                background-color: rgba(25,118,210,0.15);
                color: inherit;
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                text-align: right;
                max-width: 80%;
                float: right;
                clear: both;
            '>
                👤 {message['content']}
            </div>
            """,
            unsafe_allow_html=True
        )
    elif message["role"] == "assistant":
        st.markdown(
            f"""
            <div style='
                background-color: rgba(158,158,158,0.15);
                color: inherit;
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                text-align: left;
                max-width: 80%;
                float: left;
                clear: both;
            '>
                🤖 {message['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---- 채팅 입력창 (엔터로 전송) ----
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

    except Exception:
        st.error("❌ 오류 발생: 올바른 API 키를 입력했는지 확인해주세요.")
