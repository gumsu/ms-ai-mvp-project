# 신규 프로젝트 인재 추천 도우미

## 링크
👉[신규 프로젝트 인재 추천 도우미](https://user03-dev-recommand.azurewebsites.net/) - 애플리케이션 데모 사이트로 이동

## 데모 영상
![데모 영상](https://github.com/user-attachments/assets/ad625094-0bb8-4633-8669-bf504c52e184)

## 샘플 입력 데이터
```
    프로젝트 이름: AI 기반 통신 데이터 분석 프로젝트
    프로젝트 설명: AI를 활용하여 대규모 통신 데이터 분석 및 예측 모델 개발
    프로젝트 기간: 2026-01-01 ~ 2026-12-31
    필요한 기술 스택: Python, Azure, AI
    필요한 역할: PM, 개발자, 데이터 분석가
    지역: 서초구
```

## 📌 개요 및 목적
- 프로젝트에서는 PM, DBA, 백엔드, 프론트엔드 등 다양한 역할과 기술 스택이 요구됩니다. 본 AI 도우미는 프로젝트 요구사항과 인재 DB(기술 스택, 프로젝트 경험 등)를 기반으로 최적의 인재를 자동으로 추천해주는 시스템입니다.
- 프로젝트 투입 시점에 맞는 인재 추천 자동화
- 기술 스택, 경험, 지역 등을 고려한 정교한 매칭
- PM의 인력 선발 판단 보조 및 업무 효율 향상

## 🔧 활용 기술 및 Azure 서비스
- Azure OpenAI (GPT-4o): 프로젝트 요건과 인재 정보를 분석하고 자연어 기반 추천 사유 설명
- Azure SQL Database: 인재 정보 및 프로젝트 정보 저장
- Azure AI Search: 인재 검색 및 매칭
- Streamlit: 사용자 인터페이스 제공

## 🧩 아키텍처
1. 프로젝트 정보 입력 (Streamlit UI)
2. Azure AI Search 쿼리 생성 및 실행
3. OpenAI API를 활용한 검색 결과 분석 및 적합도 평가
4. Top-N 인재 추천 및 결과 출력 (Streamlit UI)

## 🎯 기대 효과
- PM의 인력 매칭 소요 시간 단축
- 프로젝트 적합도 기반 추천으로 투입 인력 만족도 향상
- 인력 공백 리스크 사전 예방 및 운영 계획 최적화

## ⚠️ 구현 시 고려사항
- 인재 DB 최신화 및 기술 스택의 표준화 필요
- 추천 로직의 공정성 및 설명 가능성 확보
- LLM을 활용하여 프로젝트에 적합한 인재를 추출하고, 기술 스택, 지역, 경험 등을 종합적으로 고려하여 평가 점수를 생성

## 📂 주요 파일 구조
- `app.py`: Streamlit 기반의 메인 애플리케이션 코드
- `requirements.txt`: 프로젝트 의존성 패키지 목록
- `resources/candidates_data_sample.csv`: 샘플 인재 데이터 파일

## 🛠️ 실행 방법
1. Python 환경 설정
   - `pip install -r requirements.txt` 명령어로 필요한 패키지 설치
2. 환경 변수 설정
   - `.env` 파일에 Azure OpenAI 및 Cognitive Search 관련 키와 엔드포인트 설정
3. 애플리케이션 실행
   - `streamlit run app.py` 명령어 실행 후 브라우저에서 확인
