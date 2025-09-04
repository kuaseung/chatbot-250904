import streamlit as st
from openai import OpenAI

# 앱 제목
st.title("🌍 ChatGPT 여행 챗봇")

# 사이드바 - API Key 입력
st.sidebar.title("설정")

# 세션 상태에 API 키 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.session_state.api_key = st.sidebar.text_input(
    "🔑 OpenAI API Key",
    type="password",
    value=st.session_state.api_key,
)

if not st.session_state.api_key:
    st.sidebar.warning("API 키를 입력해야 사용 가능합니다.")
    st.stop()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=st.session_state.api_key)

# 세션 상태에 메시지 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "기본적으로 한국어와 영어로 제공해 주세요. "
                "어떤 언어로 질문을 받더라도 한국어와 영어 모두 병기해서 답변해줘. "
                "당신은 여행에 관한 질문에 답하는 챗봇입니다. "
                "만약 여행 외의 질문에 대해서는 답변하지 마세요. "
                "없는 장소, 없는 음식점, 없는 관광지를 추천하지 마세요. "
                "잘 모르는 내용은 모른다고 답변하세요. "
                "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
            ),
        }
    ]

# 초기화 버튼
if st.sidebar.button("대화 초기화"):
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "기본적으로 한국어와 영어로 제공해 주세요. "
                "어떤 언어로 질문을 받더라도 한국어와 영어 모두 병기해서 답변해줘. "
                "당신은 여행에 관한 질문에 답하는 챗봇입니다. "
                "만약 여행 외의 질문에 대해서는 답변하지 마세요. "
                "없는 장소, 없는 음식점, 없는 관광지를 추천하지 마세요. "
                "잘 모르는 내용은 모른다고 답변하세요. "
                "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
            ),
        }
    ]
    st.experimental_rerun()

# 사용자 입력창 (엔터로 전송)
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
        )
        response_message = response.choices[0].message.content
        st.session_state.messages.append(
            {"role": "assistant", "content": response_message}
        )
    except Exception as e:
        st.error("❌ 오류 발생: 올바른 API 키를 입력했는지 확인해주세요.")

# 대화 출력
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"<div style='background-color:#e8f0fe; padding:10px; border-radius:10px; margin-bottom:5px;'>👤 {message['content']}</div>",
            unsafe_allow_html=True,
        )
    elif message["role"] == "assistant":
        st.markdown(
            f"<div style='background-color:#f1f3f4; padding:10px; border-radius:10px; margin-bottom:5px;'>🤖 {message['content']}</div>",
            unsafe_allow_html=True,
        )
