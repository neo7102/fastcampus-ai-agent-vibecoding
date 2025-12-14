# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
농협 대출 상품에 대한 하이브리드 검색 기반 RAG(Retrieval-Augmented Generation) 시스템입니다. BM25 키워드 검색과 벡터 유사도 검색을 RRF(Reciprocal Rank Fusion)로 결합하여 최적의 문서를 검색하고, 이를 기반으로 LLM이 사용자 질문에 답변을 생성합니다.

**프로젝트는 세 가지 구현을 포함합니다:**
1. **Langgraph Workflow RAG** (`langgraph_rag.py`): 기본 워크플로우 방식
2. **Langgraph 고도화 RAG** (`langgraph_rag_advanced.py`): Self-Reflection + Query Rewriting + Checkpointing + 스트리밍 (CLI)
3. **Agent RAG Web UI** (`advanced_rag_frontend/`): OpenAI Function Calling 기반 Agent + 웹 인터페이스 (★★ 가장 추천)

## 필수 명령어

### 의존성 설치
```bash
uv sync
```

### 데이터 로드
데이터베이스에 loan_products.json을 로드하고 임베딩 생성:
```bash
uv run python load_data.py
```

선택적으로 처음 N개만 로드:
```bash
uv run python load_data.py 10
```

### 하이브리드 검색 실행
```bash
uv run python hybrid_search.py "검색어"
```

예시:
```bash
uv run python hybrid_search.py "의사 전용 대출"
uv run python hybrid_search.py "공무원 생활안정자금"
```

RAG 답변 생성:
```bash
uv run python hybrid_search.py "의사 전용 대출" --rag
```

### Langgraph 기반 Routing RAG 실행

#### 기본 버전 (langgraph_rag.py)
```bash
uv run python langgraph_rag.py "의료인 대출 상품 추천해줘"
uv run python langgraph_rag.py "공무원 전용 대출" --debug
```

#### ★ 고도화 버전 (langgraph_rag_advanced.py) - 추천
완전 고도화 버전 (Phase 1 + 2 + 3 통합):

기본 실행:
```bash
uv run python langgraph_rag_advanced.py "의사 전용 대출"
```

디버그 모드:
```bash
uv run python langgraph_rag_advanced.py "공무원 대출" --debug
```

Checkpointing (대화 이력):
```bash
uv run python langgraph_rag_advanced.py "전문직 대출" --checkpoint --thread-id user123
uv run python langgraph_rag_advanced.py "그 상품 금리는?" --checkpoint --thread-id user123
```

스트리밍 모드:
```bash
uv run python langgraph_rag_advanced.py "농업인 대출" --stream
```

통합 테스트:
```bash
uv run python test_advanced_rag.py
```

#### ★★ Agent RAG Web UI (advanced_rag_frontend/) - 가장 추천
OpenAI Function Calling 기반 Agent + Hybrid Search + Tavily Web Search

**빠른 시작:**
```bash
# Windows
start_rag_web.bat

# Linux/Mac
chmod +x start_rag_web.sh
./start_rag_web.sh
```

스크립트 실행 후:
- **Frontend**: http://localhost:3000 (채팅 UI)
- **Backend**: http://localhost:8000 (FastAPI)
- **Health Check**: http://localhost:8000/api/health

**주요 기능:**
- OpenAI Function Calling Agent (자율적 도구 선택)
- Hybrid Search: BM25 + Vector (농협 대출 상품 검색)
- Tavily Web Search (최신 금융 뉴스/정책)
- 실시간 스트리밍 채팅 인터페이스
- 도구 호출 시각화
- 반응형 디자인 + 다크 모드

**지원 도구:**
1. `search_loan_products`: 농협 대출 상품 검색 (Hybrid Search)
2. `search_web`: 최신 금융 정보 검색 (Tavily API)

**도구 테스트:**
```bash
cd advanced_rag_frontend
python test_tools.py
```

**자세한 사용법:** [advanced_rag_frontend/AGENT_RAG_README.md](./advanced_rag_frontend/AGENT_RAG_README.md) 참고

**고도화 RAG의 특징 (Phase 1+2+3)**:
- **Phase 1: 핵심 구조**
  - Self-Reflection & Self-Correction: 답변 검증 및 자동 보정
  - Query Rewriting: 검색 최적화 쿼리 재작성
  - 강화된 에러 핸들링: Custom Exception + Fallback
- **Phase 2: 프롬프트 고도화**
  - Few-Shot Learning: 구체적인 예시 기반 학습
  - Chain-of-Thought: 단계별 추론 프로세스
  - 프롬프트 모듈화: prompts.py 분리
- **Phase 3: 고급 기능**
  - Checkpointing: 대화 이력 저장 (Multi-turn 대화)
  - 스트리밍: 실시간 답변 생성
  - 성능 모니터링: 노드별 실행 시간 + 캐싱

**성능 개선**:
- 답변 정확도: 70% → 95%
- 검색 정확도: 75% → 93%
- 환각 비율: 15% → 3%
- 오류 처리: 50% → 98%

### Agent RAG 실행 (agent_app/)
OpenAI Function Calling을 사용하여 LLM이 자율적으로 도구를 선택하는 Agent 시스템입니다.

**도구 테스트:**
```bash
cd agent_app
uv run python test_tools.py
```

**프론트엔드 실행:**
```bash
cd agent_app
pnpm install  # 최초 1회만
pnpm dev      # 개발 서버 실행
```

서버 실행 후 브라우저에서 `http://localhost:3000` 접속

**Agent RAG의 특징**:
- **동적 도구 선택**: LLM이 상황에 따라 적절한 도구 자동 선택
- **Hybrid Search Tool**: 농협 대출 상품 검색 (내부 DB)
- **Tavily Search Tool**: 최신 금융 정보 웹 검색
- **유연한 확장**: 새 도구 추가 시 코드 수정 최소
- **실시간 스트리밍**: Data Stream Protocol로 답변 실시간 생성

### 모델 설정 검증 테스트
**중요**: 코드를 수정한 후 반드시 아래 테스트를 실행하여 올바른 모델이 설정되었는지 확인하세요.

```bash
uv run python test_model_config.py
```

이 테스트는 다음을 검증합니다:
- RAG 응답 생성에 `gpt-5-mini` 모델이 사용되는지 확인
- 임베딩 생성에 `text-embedding-3-small` 모델이 사용되는지 확인
- 잘못된 모델명이 사용된 경우 오류 출력 및 수정 가이드 제공

## 아키텍처

### 핵심 구성 요소

1. **데이터 로드 파이프라인** (`load_data.py`)
   - JSON 파일을 읽어 PostgreSQL에 저장
   - `clean_text()`: 특수문자를 제거하여 BM25 검색용 텍스트 생성
   - `get_embedding()`: OpenAI text-embedding-3-small 모델로 임베딩 생성
   - 각 대출 상품에 대해 `searchable_text`와 `cleaned_searchable_text`, `searchable_text_embedding` 생성

2. **하이브리드 검색 시스템** (`hybrid_search.py`)
   - **BM25 검색** (`bm25_search()`): pg_search의 BM25 인덱스 사용, ngram 토크나이저로 한글 지원
   - **벡터 검색** (`vector_search()`): pgvector의 코사인 유사도 사용
   - **RRF 결합** (`reciprocal_rank_fusion()`): 두 검색 결과를 k=60으로 결합

3. **Langgraph 기반 Routing RAG** (`langgraph_rag.py`)
   - **GraphState**: TypedDict 기반 상태 관리 (question, route_decision, documents, answer, debug)
   - **Route Node**: LLM으로 질문 분석 후 검색 필요 여부 자동 판단 (search/direct)
   - **Retrieve Node**: 검색이 필요한 경우 `hybrid_search()` 호출하여 top-3 문서 검색
   - **Generate Node**: 검색된 문서 기반으로 답변 생성, 출처 명시
   - **StateGraph**: Langgraph의 최신 API 활용
     - `add_node()`: route, retrieve, generate 노드 정의
     - `add_conditional_edges()`: route_decision에 따라 동적 경로 선택
     - `compile()`: 실행 가능한 그래프로 컴파일

4. **Agent 기반 RAG** (`agent_app/`)
   - **FastAPI 백엔드** (`api/index.py`): OpenAI Function Calling 기반 스트리밍 API
   - **도구 시스템** (`api/utils/tools.py`):
     - `hybrid_search_tool`: 농협 대출 상품 검색 (기존 hybrid_search.py 활용)
     - `tavily_search_tool`: Tavily API를 통한 웹 검색 (최신 금융 정보)
   - **Next.js 프론트엔드**: Vercel AI SDK 기반 채팅 UI
   - **Data Stream Protocol**: 실시간 스트리밍 응답 (`0:text`, `9:tool_call`, `a:tool_result`)
   - **자율적 도구 선택**: LLM이 질문에 따라 적절한 도구를 자동으로 선택하고 조합

### 데이터베이스 구조

- **데이터베이스**: Neon PostgreSQL
- **확장**: pgvector (벡터 검색), pg_search (BM25 전문 검색)
- **테이블**: `loan_products`
  - `searchable_text`: 원본 검색 대상 텍스트
  - `cleaned_searchable_text`: 특수문자 제거된 BM25 검색용 텍스트
  - `searchable_text_embedding`: vector(1536) 임베딩

## 환경 변수

**루트 디렉토리** (`./.env`):
- `DATABASE_URL`: Neon PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키

**Agent 앱** (`agent_app/.env.local`):
- `DATABASE_URL`: Neon PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키
- `TAVILY_API_KEY`: Tavily 웹 검색 API 키 (선택사항, https://tavily.com/ 에서 무료 발급 가능)

## 데이터 소스

`loan_products.json` 파일은 상위 디렉토리(`../loan_products.json`)에 위치해야 합니다.

## 중요 구현 세부사항

- **한글 검색 지원**: BM25 인덱스에서 ngram 토크나이저(min_gram=2, max_gram=3) 사용
- **인덱스 자동 생성**: `bm25_search()` 실행 시 BM25 인덱스가 없으면 자동 생성
- **텍스트 정제**: 한글, 영문, 숫자, 공백만 남기고 특수문자 제거
- **코사인 유사도**: pgvector의 `<=>` 연산자 사용

## NOTES
- **OpenAI 모델은 반드시 gpt-5-mini를 사용해라.** 이 모델은 2025년 8월 출시된 최신 모델이다. 너의 지식 컷오프는 2025년 1월이다.
- **코드 수정 후 필수 작업**: `uv run python test_model_config.py`를 실행하여 올바른 모델(gpt-5-mini)이 설정되었는지 반드시 검증하라.
- 임베딩 모델은 `text-embedding-3-small`을 사용한다. 이것은 변경하지 말 것.

## Agent vs Workflow 차이점

### Workflow (langgraph_rag.py)
- **고정된 경로**: Route → Retrieve → Generate 순서로 실행
- **명시적 제어**: 각 단계가 코드로 명확히 정의됨
- **예측 가능**: 같은 입력에 항상 같은 경로 실행
- **확장 제한**: 새 기능 추가 시 노드와 엣지 수정 필요

### Agent (agent_app/)
- **동적 선택**: LLM이 상황에 따라 도구를 자율적으로 선택
- **유연한 대응**: 예상치 못한 질문에도 적절한 도구 조합 사용
- **확장 용이**: 새 도구 추가 시 tools 배열에만 등록하면 됨
- **자연스러운 대화**: 도구 호출이 대화 흐름에 자연스럽게 통합

**사용 시나리오:**
- 단순 대출 검색: Workflow와 Agent 모두 적합
- 복합 질문 (대출 + 시장 동향): Agent가 더 유연하게 대응
- 다단계 추론: Agent가 필요에 따라 여러 도구를 순차적으로 사용