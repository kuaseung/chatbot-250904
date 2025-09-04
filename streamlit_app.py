import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="부동산 투자 챗봇 🏠", page_icon="🏢", layout="centered")

st.title("🏠 부동산 투자 챗봇")
st.markdown(
    "<p style='opacity:0.7;'>지역별 시세, 임대 수익률 계산, 투자 전략 및 리스크 분석까지 자동으로 제공하는 챗봇입니다.</p>",
    unsafe_allow_html=True
)

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
                "당신은 부동산 투자 전문가입니다. "
                "사용자가 입력한 지역과 임대/매매 조건을 바탕으로 예상 수익률, 투자 전략, 리스크 분석까지 자동으로 표와 리스트로 정리합니다. "
                "잘 모르는 정보는 모른다고 답합니다."
            )
        }
    ]

# ---- 초기화 버튼 ----
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = st.session_state.messages[:1]
    st.experimental_rerun()

# ---- 수익률 계산 함수 ----
def calculate_rental_yield(deposit: float, monthly_rent: float, maintenance: float = 0):
    annual_income = monthly_rent * 12
    annual_cost = maintenance * 12
    net_income = annual_income - annual_cost
    if deposit == 0:
        return 0
    yield_percent = (net_income / deposit) * 100
    return round(yield_percent, 2)

# ---- 검증 함수 (환각 방지) ----
def validate_response(text: str):
    risky_phrases = ["없는", "허구", "가짜", "잘못된"]
    if any(phrase in text for phrase in risky_phrases):
        return "⚠️ 답변이 신뢰할 수 없을 수 있습니다. 다른 부동산 정보를 물어봐주세요."
    return text

# ---- 지역 선택 ----
st.markdown("### 📍 투자 지역 선택")
region = st.selectbox("지역을 선택하세요", ["서울 강남", "서울 서초", "경기 수원", "부산 해운대", "기타"])

# ---- 수익률 입력 ----
st.markdown("### 🏦 임대 수익률 계산 (선택 입력)")
col1, col2, col3 = st.columns(3)
deposit = col1.number_input("보증금 (만원)", min_value=0, value=0)
monthly_rent = col2.number_input("월세 (만원)", min_value=0, value=0)
maintenance = col3.number_input("관리비 (만원)", min_value=0, value=0)

rental_yield = None
if deposit > 0 and monthly_rent > 0:
    rental_yield = calculate_rental_yield(deposit, monthly_rent, maintenance)
    st.markdown(f"**예상 연 수익률: {rental_yield}%**")

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

# ---- 채팅 입력창 (엔터 전송) ----
if prompt := st.chat_input("궁금한 부동산 질문을 입력하세요..."):
    user_msg = f"[지역: {region}, 보증금: {deposit}만원, 월세: {monthly_rent}만원, 관리비: {maintenance}만원] {prompt}"
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    try:
        # ---- AI 답변 생성 ----
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_message = validate_response(response.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": ai_message})

        with st.chat_message("assistant"):
            st.markdown(ai_message)

        # ---- 수익률 표 + 투자 전략 & 리스크 ----
        if rental_yield is not None:
            st.markdown(
                f"""
                <table style='border:1px solid #ccc; border-collapse: collapse;'>
                    <tr><th style='border:1px solid #ccc; padding:5px;'>지역</th>
                        <th style='border:1px solid #ccc; padding:5px;'>보증금</th>
                        <th style='border:1px solid #ccc; padding:5px;'>월세</th>
                        <th style='border:1px solid #ccc; padding:5px;'>관리비</th>
                        <th style='border:1px solid #ccc; padding:5px;'>예상 연 수익률</th></tr>
                    <tr>
                        <td style='border:1px solid #ccc; padding:5px;'>{region}</td>
                        <td style='border:1px solid #ccc; padding:5px;'>{deposit} 만원</td>
                        <td style='border:1px solid #ccc; padding:5px;'>{monthly_rent} 만원</td>
                        <td style='border:1px solid #ccc; padding:5px;'>{maintenance} 만원</td>
                        <td style='border:1px solid #ccc; padding:5px;'>{rental_yield}%</td>
                    </tr>
                </table>
                """, unsafe_allow_html=True
            )
            st.markdown("### 📊 추천 투자 전략 & 리스크 분석")
            st.markdown(
                f"""
                - **추천 전략**: 단기/장기 투자, 임대/매매 유형 자동 분석
                - **리스크 요소**: 공실률, 금리 상승, 정책 변화, 지역별 변동성
                - **참고**: 실제 투자 전 반드시 전문가 상담 권장
                """, unsafe_allow_html=True
            )

    except Exception:
        st.error("❌ 오류 발생: 올바른 API 키를 입력했는지 확인해주세요.")
