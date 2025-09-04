import openai
import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(
    page_title="여행 챗봇 🌍",
    page_icon="✈️",
    layout="centered"
)

# ---- 타이틀 ----
st.markdown(
    """
    <h1 style='text-align: center;'>🌍 여행 전문 챗봇</h1>
    <p style='text-align: center; opacity:0.7;'>
        한국어 & 영어로 여행 관련 질문만 답변해드립니다.
    </p>
    """,
    unsafe_allow_html=True
)

# ---- 사이드바 설정 ----
st.sidebar.header("⚙️ 설정")
openai_api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.info("✈️ 여행지 추천, 준비물, 문화, 음식에 대해 물어보세요.\n\n💡 *여행 외 질문은 답하지 않습니다.*")

if not openai_api_key:
    st.sidebar.warning("API 키를 입력해야 사용 가능합니다.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# ---- 대화 상태 초기화 ----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "너는 여행 전문가 챗봇이다. 반드시 실제로 존재하는 장소, 음식점, 문화만 안내해야 한다. "
                "만약 질문에 대한 사실을 모른다면 반드시 '잘 모르겠습니다'라고 답해야 한다. "
                "절대로 없는 장소, 없는 음식점, 허구의 정보를 만들어내지 마라. "
                "여행 관련 질문에만 답변하며, 한국어와 영어로 모두 제공해라."
            )
        }
    ]

# ---- 검증 함수 ----
def validate_response(text: str) -> str:
    risky_phrases = ["없는", "허구", "가짜", "잘못된"]
    if any(phrase in text for phrase in risky_phrases):
        return "⚠️ 답변이 신뢰할 수 없을 수 있습니다. 다른 여행 정보를 물어봐주세요."
    return text

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.clear()
    st.rerun()   # ✅ 에러 메시지 없이 새로고침

# ---- 대화 표시 ----
st.markdown("### 📜 대화 기록")

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# ---- 채팅 입력창 (엔터 전송) ----
if prompt := st.chat_input("메시지를 입력하세요... (엔터로 전송)"):
    # 사용자 입력 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI 응답 생성
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        response_message = response.choices[0].message.content
        validated_message = validate_response(response_message)

        st.session_state.messages.append({"role": "assistant", "content": validated_message})
        with st.chat_message("assistant"):
            st.markdown(validated_message)

    except Exception:
        st.error("❌ 오류: API 키가 잘못되었거나 요청에 문제가 있습니다.")
