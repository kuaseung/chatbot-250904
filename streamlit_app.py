import openai
import streamlit as st
from openai import OpenAI
import os

st.title("ChatGPT와 대화 챗봇")

st.sidebar.title("설정")
openai_api_key = st.sidebar.text_input("OpenAI 키를 입력하세요", type="password")

if not openai_api_key:
    st.sidebar.warning("OpenAI 키를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [  
        {"role": "system", 
         "content": "기본적으로 한국어와 영어로 제공해 주세요."
          "어떤 언어로 질문을 받더라도 한국어와 영어 모두 병기해서 답변해줘"
          "당신은 여행에 관한 질문에 답하는 챗봇입니다. "
          "만약에 여행 외에 질문에 대해서는 답변하지 마세요."
          "너가 잘 모르는 내용은 만들어서 답변하지 마렴. 환각증세를 철저하게 없애 주세요."
          "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
        }  
    ]



# 사용자 입력
user_input = st.text_input("사용자: ", key="user_input")

if st.button("전송") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )

        # OpenAI 응답 추가
        response_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response_message})

    except Exception as e:
        st.error(f"오류 발생: 잘못된 키가 입력되었습니다.")

    # 사용자 입력 초기화
    user_input = ""

# 대화 내용 표시
for message in st.session_state.messages:
    if message["role"] != "system":  # 시스템 메시지가 아닌 경우에만 표시
        icon = "👤"  if message["role"] == "user" else "🤖"
        st.markdown(f"{icon}: {message['content']}")
