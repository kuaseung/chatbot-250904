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
        {"role": "system", "content": (
            "기본적으로 한국어와 영어로 제공해 주세요."
            "어떤 언어로 질문을 받더라도 한국어와 영어 모두 병기해서 답변해줘. "
            "당신은 여행에 관한 질문에 답하는 챗봇입니다. "
            "만약에 여행 외에 질문에 대해서는 답변하지 마세요. "
            "모르는 내용은 지어내지 말고, 환각증세를 철저히 없애 주세요. "
            "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
                "너는 여행 전문가 챗봇이다. 반드시 실제로 존재하는 장소, 음식점, 문화만 안내해라. "
    "만약 질문에 대한 사실을 모른다면 '잘 모르겠습니다'라고 답해라. "
    "절대로 없는 장소, 없는 음식점, 허구의 정보를 만들어내지 마라. "
    "여행 관련 질문에만 답변하며, 한국어와 영어로 모두 제공해라."
        )}
    ]

# ---- 채팅 입력창 ----
with st.container():
    st.markdown("### 💬 대화하기")
    user_input = st.text_input("메시지를 입력하세요...", key="user_input", placeholder="예: 일본 여행 준비물 추천해줘")

    send_col, clear_col = st.columns([4,1])
    with send_col:
        send_clicked = st.button("🚀 전송", use_container_width=True)
    with clear_col:
        clear_clicked = st.button("🧹 초기화", use_container_width=True)

# ---- 초기화 버튼 ----
if clear_clicked:
    st.session_state.messages = st.session_state.messages[:1]  # system 메시지만 유지
    st.experimental_rerun()

# ---- OpenAI API 호출 ----
if send_clicked and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        response_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response_message})

    except Exception:
        st.error("❌ 오류: API 키가 잘못되었거나 요청에 문제가 있습니다.")

# ---- 대화 표시 ----
st.markdown("### 📜 대화 기록")

user_style = """
<div style='
    background: rgba(100, 149, 237, 0.15); 
    padding: 12px; 
    border-radius: 12px; 
    margin-bottom: 10px;
    color: inherit;
'>
<b>👤 사용자:</b><br>{content}
</div>
"""

assistant_style = """
<div style='
    background: rgba(231, 76, 60, 0.15); 
    padding: 12px; 
    border-radius: 12px; 
    margin-bottom: 10px;
    color: inherit;
'>
<b>🤖 챗봇:</b><br>{content}
</div>
"""

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(user_style.format(content=message['content']), unsafe_allow_html=True)
    elif message["role"] == "assistant":
        st.markdown(assistant_style.format(content=message['content']), unsafe_allow_html=True)
