import streamlit as st
import pandas as pd
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import re
import pymysql
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
api_type = os.getenv("OPENAI_API_TYPE")
api_version = os.getenv("OPENAI_API_VERSION")
deployment = "user03-gpt-4o-mini"

search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
search_key= os.environ["AZURE_AI_SEARCH_QUERY_KEY"]
credential = AzureKeyCredential(search_key)
index_name = os.getenv("AZURE_SEARCH_INDEX", "user03-rag-002")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
)

db = pymysql.connect(
    host=os.getenv("DB_HOSTNAME"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db.cursor()

# Initialize Azure Cognitive Search Client
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=credential
)

def extract_top_n_candidates(response, n=5):
    pattern = r"이름:\s*(.*?)\n\s*역할:\s*(.*?)\n\s*(\d+)점:\s*(.*)"
    matches = re.findall(pattern, response)

    candidates = []
    for match in matches:
        name, role, score, reason = match[0], match[1], match[2], match[3]
        candidates.append({
            "name": name,
            "role": role,
            "score": score,
            "reason": reason
        })

    return sorted(candidates, key=lambda x: x['score'], reverse=True)[:n]

def make_prompt(project_description, candidates):
    prompt = f"""
    당신은 IT 인재 추천 전문가입니다.
    다음은 SI 프로젝트 정보입니다:

    {project_description}

    아래는 이 프로젝트 투입에 추천할 수 있는 인재 목록입니다. 각 인재에 대해 아래 기준으로 평가해 주세요:

    - 이 프로젝트에 **얼마나 적합한지 1~10점으로 평가**
    - 한 줄로 이유를 설명
    - 현재 다른 프로젝트에 참여 중이라면 "참여 불가"로 평가 (웬만하면 후순위)
    - 지역(거주지 vs 프로젝트 위치)이 맞지 않으면 감점
    - history 내역이므로 중복된 인재가 있다면 1번만 출력

    [인재 목록] (JSON 형식)
    """
    for result in search_results:
        prompt += f"""
        {result}
        """

    prompt += "\n각 인재에 대해 아래와 같이 출력해 주세요:\n예시)\n이름: 홍길동\n역할: PM\n8점: 기술 스택과 경력은 적합하지만 지역이 멀어 감점"
    return prompt

# 1. 프로젝트 정보 입력
st.title("프로젝트 인재 추천 시스템")
placeholder = """예)
    프로젝트 이름: AI 기반 통신 데이터 분석 프로젝트
    프로젝트 설명: AI를 활용하여 대규모 통신 데이터 분석 및 예측 모델 개발
    프로젝트 기간: 2026-01-01 ~ 2026-12-31
    필요한 기술 스택: Python, Azure, AI
    필요한 역할: PM, 개발자, 데이터 분석가
    지역: 서울 
"""
project_input = st.text_area("📝 프로젝트 설명을 입력해주세요", placeholder=placeholder, height=200)

# 2. 추천 시작 버튼
st.markdown("## 🔍 AI 검색 결과")
if st.button("AI 검색 실행"):
    with st.spinner("검색 중..."):
        search_results = search_client.search(
            search_text=project_input,  # Use project description as the search query
            select=['name', 'residence_city', 'department', 'project_name', 'project_role', 'start_date', 'end_date', 'tech_stack','region_city']
        )

        prompt = make_prompt(project_input, search_results)

        st.markdown(prompt)

        response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": prompt},
                ]
            ) 
        
        
        st.markdown("### 검색 결과")
        top_candidates = extract_top_n_candidates(response.choices[0].message.content)
        if top_candidates:
            for idx, candidate in enumerate(top_candidates):
                st.write(f"**{idx+1}번**")
                st.write(f"**이름:** {candidate['name']}")
                st.write(f"**역할:** {candidate['role']}")
                st.write(f"**점수:** {candidate['score']}점")
                st.write(f"**이유:** {candidate['reason']}")
                st.write("---")
        else:
            st.write("추천할 인재가 없습니다.")