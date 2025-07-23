import streamlit as st
import pandas as pd
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import re
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
index_name = os.getenv("AZURE_SEARCH_INDEX", "user03-rag-003")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
)

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
    - 현재 다른 프로젝트에 참여 중이라면 "참여 불가"로 평가 (현재 날짜는 2025-08-01 로 가정)
    - 지역(거주지 vs 프로젝트 위치)이 맞지 않으면 감점
    - history 내역이므로 중복된 인재가 있다면 1번만 출력
    - 긍정적으로 평가

    [인재 목록] (JSON 형식)
    """
    for result in search_results:
        prompt += f"""
        {result}
        """

    prompt += "\n각 인재에 대해 아래와 같이 출력해 주세요:\n예시)\n이름: 홍길동\n역할: PM\n8점: 기술 스택과 경력은 적합하지만 지역이 멀어 감점"
    return prompt

def make_search_query(project_description):
    prompt = f"""
    당신은 IT 인재 추천 전문가입니다.
    다음은 SI 프로젝트 정보입니다:

    {project_description}

    이 프로젝트에 적합한 인재를 찾기 위해 Azure Cognitive Search(Azure AI Search)에서 검색할 쿼리를 작성해 주세요.
    불필요한 설명은 제외하고, 검색 쿼리만 작성해 주세요.

    Search 에는 다음과 같은 필드가 있습니다:
    - name: 인재 이름
    - residence_city: 거주 도시
    - department: 소속 부서
    - project_name: 프로젝트 이름
    - project_role: 프로젝트 역할
    - start_date: 프로젝트 시작일
    - end_date: 프로젝트 종료일
    - tech_stack: 기술 스택
    - region_city: 지역 도시
    """
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

        # 3. 프로젝트 설명을 기반으로 Azure Cognitive Search 쿼리 생성
        search_query_prompt = make_search_query(project_input)

        # 4. OpenAI API를 사용하여 검색 쿼리 생성
        search_query_response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": search_query_prompt},
            ]
        )
        # 5. 검색 쿼리 결과 추출
        search_query_result = search_query_response.choices[0].message.content.strip()

        # 6. Azure Cognitive Search를 사용하여 인재 검색
        search_results = search_client.search(
            search_text=search_query_result,  # Use project description as the search query
            select=['name', 'residence_city', 'department', 'project_name', 'project_role', 'start_date', 'end_date', 'tech_stack','region_city']
        )

        prompt = make_prompt(project_input, search_results)

        # st.markdown(prompt)

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