import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

api_key = os.getenv("OPENAI_API_KEY")

def make_prompt(project_description, candidates):
    prompt = f"""
    당신은 IT 인재 추천 전문가입니다.
    다음은 SI 프로젝트 정보입니다:

    {project_description}

    아래는 이 프로젝트 투입에 추천할 수 있는 인재 목록입니다. 각 인재에 대해 아래 기준으로 평가해 주세요:

    - 이 프로젝트에 **얼마나 적합한지 1~10점으로 평가**
    - 한 줄로 이유를 설명
    - 현재 다른 프로젝트에 참여 중이라면 "참여 불가"로 평가
    - 지역(거주지 vs 프로젝트 위치)이 맞지 않으면 감점

    [인재 목록]
    """

    for idx, c in enumerate(candidates, 1):
        prompt += f"""
        {idx}. 이름: {c['name']}
        기술스택: {c['skills']}
        경력요약: {c['summary']}
        프로젝트 이력: {c['projects']}
        현재 상태: {"프로젝트 참여 중" if c['in_project'] else "배정 가능"}
        거주지: {c['residence']}
        """

        prompt += "\n각 인재에 대해 아래와 같이 출력해 주세요:\n예시)\n이름: 홍길동\n1. 8점 - 기술 스택과 경력은 적합하지만 지역이 멀어 감점\n2. 참여 불가 - 현재 다른 프로젝트에 투입 중\n3. 10점 - 기술 스택과 경력이 적합하고 지역도 맞음"
    return prompt

# 1. 프로젝트 정보 입력
st.title("프로젝트 인재 추천 시스템")

project_input = st.text_area("📝 프로젝트 설명을 입력해주세요")
uploaded_file = st.file_uploader("📄 인재 데이터 CSV 파일 (이름, 경력, 기술 스택, 프로젝트 경험 등)", type="csv")

# 2. 추천 시작 버튼
if st.button("추천 시작") and uploaded_file:
    with st.spinner("추천 중..."):
        df = pd.read_csv(uploaded_file)
        candidates = df.to_dict(orient="records")
        prompt = make_prompt(project_input, candidates)
        
        response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {"type": "message", "role": "assistant", "content": prompt}
                ]
            ) 
        st.markdown(response.output_text)
