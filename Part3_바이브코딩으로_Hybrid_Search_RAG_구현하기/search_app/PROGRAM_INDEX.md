# search_app 프로그램 내역 정리

농협 대출 상품 하이브리드 검색 시스템의 전체 구성 요소 및 파일 설명서

---

## 📁 디렉토리 구조

```
search_app/
├── 📄 설정 파일
│   ├── pyproject.toml           # Python 프로젝트 설정 및 의존성
│   ├── .env.example             # 환경 변수 템플릿
│   └── .gitignore               # Git 제외 파일 목록
│
├── 🗄️ 데이터베이스
│   └── init_db.sql              # 데이터베이스 스키마 초기화 스크립트
│
├── 🔧 핵심 기능 (Python 스크립트)
│   ├── load_data.py             # 데이터 로드 및 임베딩 생성
│   ├── hybrid_search.py         # 하이브리드 검색 (BM25 + 벡터)
│   ├── langgraph_rag.py         # Langgraph 기반 Workflow RAG
│   └── test_model_config.py     # 모델 설정 검증 테스트
│
├── 📚 문서
│   ├── README.md                # 프로젝트 전체 문서
│   ├── QUICKSTART.md            # 빠른 시작 가이드
│   ├── CLAUDE.md                # Claude Code 가이드라인
│   ├── BM25_ISSUE_REPORT.md     # BM25 한글 검색 문제 해결 리포트
│   └── PROGRAM_INDEX.md         # 이 파일 (프로그램 내역 정리)
│
└── 🌐 Agent RAG 웹 애플리케이션
    └── agent_app/               # Next.js + FastAPI 기반 Agent RAG
        ├── api/                 # FastAPI 백엔드
        ├── app/                 # Next.js 페이지
        ├── components/          # React 컴포넌트
        └── ...
```

---

## 📄 핵심 파일 상세 설명

### 1. 설정 파일

#### `pyproject.toml`
- **역할**: Python 프로젝트 의존성 관리 (uv 패키지 매니저 사용)
- **주요 의존성**:
  - `psycopg2-binary`: PostgreSQL 클라이언트
  - `openai`: OpenAI API (임베딩 및 LLM)
  - `langgraph`, `langchain`: Workflow/Agent RAG 프레임워크
  - `python-dotenv`: 환경 변수 로드

#### `.env.example`
- **역할**: 환경 변수 템플릿
- **필수 변수**:
  ```
  DATABASE_URL=postgresql://...        # Neon PostgreSQL 연결 문자열
  OPENAI_API_KEY=sk-...                # OpenAI API 키
  ```

### 2. 데이터베이스

#### `init_db.sql`
- **역할**: PostgreSQL 데이터베이스 스키마 초기화
- **주요 작업**:
  - pgvector, pg_search 확장 활성화
  - `loan_products` 테이블 생성 (25개 컬럼)
  - HNSW 벡터 인덱스 생성 (코사인 거리)
- **실행 방법**:
  ```bash
  psql $DATABASE_URL -f init_db.sql
  ```

### 3. 핵심 Python 스크립트

#### `load_data.py` - 데이터 로드 및 임베딩 생성
- **역할**: loan_products.json을 DB에 로드하고 임베딩 생성
- **주요 기능**:
  - `load_json_data()`: JSON 파일 파싱
  - `clean_text()`: 특수문자 제거 (BM25용)
  - `get_embedding()`: OpenAI text-embedding-3-small로 임베딩 생성
  - `insert_product()`: DB에 데이터 삽입 (UPSERT)
- **실행 방법**:
  ```bash
  uv run python load_data.py           # 전체 데이터
  uv run python load_data.py 10        # 처음 10개만
  ```
- **주의사항**: OpenAI API 호출로 시간 및 비용 발생

#### `hybrid_search.py` - 하이브리드 검색 엔진
- **역할**: BM25와 벡터 검색을 RRF로 결합한 하이브리드 검색
- **주요 함수**:
  - `bm25_search()`: pg_search BM25 인덱스 검색 (ngram 토크나이저)
  - `vector_search()`: pgvector 코사인 유사도 검색
  - `reciprocal_rank_fusion()`: RRF 알고리즘 (k=60)
  - `hybrid_search()`: 전체 검색 파이프라인
- **실행 방법**:
  ```bash
  uv run python hybrid_search.py "의사 전용 대출"
  ```
- **특징**:
  - BM25 인덱스 자동 생성 (없는 경우)
  - ngram 토크나이저로 한글 검색 완벽 지원
  - Top 20개씩 검색 후 RRF로 Top 10 반환

#### `langgraph_rag.py` - Workflow RAG
- **역할**: Langgraph를 사용한 고정 경로 RAG 시스템
- **워크플로우**: Route → Retrieve → Generate
- **주요 노드**:
  - **Route Node**: 질문 분석, 검색 필요 여부 판단
  - **Retrieve Node**: hybrid_search() 호출, Top 3 검색
  - **Generate Node**: Few-shot 프롬프트 기반 답변 생성
- **실행 방법**:
  ```bash
  uv run python langgraph_rag.py "의료인 대출 상품 추천해줘"
  uv run python langgraph_rag.py "공무원 대출" --debug  # 디버그 모드
  ```
- **특징**:
  - Few-shot 예시로 고품질 답변
  - 출처 명시 강제 ([상품N])
  - 검색 신뢰도 평가
  - 면책 사항 자동 포함

#### `test_model_config.py` - 모델 설정 검증
- **역할**: 코드에서 올바른 OpenAI 모델 사용 여부 검증
- **검증 항목**:
  - RAG 응답 생성: `gpt-5-mini` 사용 확인
  - 임베딩 생성: `text-embedding-3-small` 사용 확인
- **실행 방법**:
  ```bash
  uv run python test_model_config.py
  ```
- **주의**: 코드 수정 후 반드시 실행 필요

---

## 📚 문서 파일

### `README.md`
- **내용**: 프로젝트 전체 문서
- **포함 내용**:
  - 기술 스택 소개
  - 설치 및 설정 가이드
  - 사용법 및 예시
  - 구현 상세 (BM25, 벡터, RRF)
  - 데이터베이스 스키마
  - 참고 자료

### `QUICKSTART.md`
- **내용**: 빠른 시작 가이드
- **타겟**: 처음 사용하는 개발자
- **포함 내용**:
  - 5단계 실행 가이드
  - 문제 해결 FAQ
  - 테스트 예시

### `CLAUDE.md`
- **내용**: Claude Code AI 가이드라인
- **목적**: Claude가 이 프로젝트를 작업할 때 참고하는 문서
- **포함 내용**:
  - 필수 명령어
  - 아키텍처 설명
  - 환경 변수
  - 중요 구현 세부사항
  - Agent vs Workflow 차이점

### `BM25_ISSUE_REPORT.md`
- **내용**: BM25 한글 검색 문제 해결 리포트
- **문제**: 기본 토크나이저로 한글 단어 검색 실패
- **해결**: ngram 토크나이저 적용
- **가치**: 트러블슈팅 과정 기록, 향후 참고 자료

---

## 🌐 Agent RAG 웹 애플리케이션

### `agent_app/` 디렉토리
- **기술 스택**: Next.js (프론트엔드) + FastAPI (백엔드)
- **특징**: OpenAI Function Calling 기반 자율 에이전트

#### 주요 구성 요소

```
agent_app/
├── api/                         # FastAPI 백엔드
│   ├── index.py                 # 메인 API 엔드포인트
│   └── utils/
│       └── tools.py             # 검색 도구 (hybrid_search, tavily)
│
├── app/                         # Next.js 페이지
│   └── page.tsx                 # 메인 채팅 UI
│
├── components/                  # React 컴포넌트
│   ├── chat/
│   └── ui/
│
├── package.json                 # Node.js 의존성
├── next.config.js               # Next.js 설정
├── .env.example                 # 환경 변수 템플릿
├── QUICKSTART.md                # Agent 앱 시작 가이드
└── IMPLEMENTATION_REPORT.md     # 구현 상세 리포트
```

#### 실행 방법
```bash
cd agent_app
pnpm install          # 최초 1회
pnpm dev             # 개발 서버 실행 (http://localhost:3000)
```

#### 주요 기능
- **Hybrid Search Tool**: 농협 대출 상품 검색 (내부 DB)
- **Tavily Search Tool**: 최신 금융 정보 웹 검색
- **실시간 스트리밍**: Data Stream Protocol로 답변 생성
- **자율적 도구 선택**: LLM이 질문에 따라 적절한 도구 자동 선택

---

## 🔄 전체 실행 흐름

### 초기 설정 (한 번만)
1. `.env` 파일 설정
2. `init_db.sql` 실행 (DB 스키마 생성)
3. `uv sync` (Python 의존성 설치)
4. `uv run python load_data.py 10` (샘플 데이터 로드)

### 검색 시스템 사용
```bash
# 1. 하이브리드 검색만
uv run python hybrid_search.py "공무원 대출"

# 2. Workflow RAG (고정 경로)
uv run python langgraph_rag.py "의사 전용 대출"

# 3. Agent RAG (웹 UI)
cd agent_app && pnpm dev
```

---

## 🎯 프로젝트 주요 특징

### 1. 하이브리드 검색
- **BM25**: 키워드 기반 전문 검색 (ngram 한글 지원)
- **벡터**: 의미 기반 유사도 검색 (1536차원 임베딩)
- **RRF**: 두 결과를 최적으로 결합

### 2. 두 가지 RAG 구현
- **Workflow (Langgraph)**: 고정 경로, 예측 가능
- **Agent (OpenAI)**: 동적 선택, 유연한 대응

### 3. 완전한 한글 지원
- ngram 토크나이저로 BM25 한글 검색 완벽 지원
- OpenAI 임베딩 모델로 한글 의미 파악

### 4. 프로덕션 준비
- 환경 변수 분리
- 에러 핸들링
- 자동 인덱스 생성
- 모델 검증 테스트

---

## 📊 데이터베이스 스키마

### `loan_products` 테이블
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | VARCHAR(255) | 기본키 |
| product_code | VARCHAR(50) | 상품 코드 |
| product_name | VARCHAR(255) | 상품명 |
| searchable_text | TEXT | 원본 검색 텍스트 |
| cleaned_searchable_text | TEXT | BM25용 정제 텍스트 |
| searchable_text_embedding | vector(1536) | 벡터 임베딩 |
| ... | ... | 기타 상품 정보 25개 필드 |

### 인덱스
- **BM25 인덱스**: `idx_loan_products_bm25` (ngram 토크나이저)
- **벡터 인덱스**: `idx_loan_products_embedding` (HNSW, 코사인 거리)

---

## 🔧 기술 스택 요약

### Backend
- **언어**: Python 3.11+
- **패키지 매니저**: uv
- **데이터베이스**: Neon PostgreSQL 17
- **확장**: pgvector, pg_search (ParadeDB)
- **프레임워크**: Langgraph, LangChain, FastAPI

### Frontend (Agent 앱)
- **프레임워크**: Next.js 14
- **UI 라이브러리**: Vercel AI SDK
- **스타일링**: Tailwind CSS

### AI/ML
- **임베딩**: OpenAI text-embedding-3-small (1536차원)
- **LLM**: OpenAI gpt-5-mini
- **검색**: BM25 (pg_search) + 벡터 (pgvector)
- **융합**: RRF (Reciprocal Rank Fusion, k=60)

---

## 📝 참고 자료

- [ParadeDB Hybrid Search Guide](https://docs.paradedb.com/documentation/guides/hybrid)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [pg_search Extension](https://github.com/paradedb/paradedb/tree/dev/pg_search)
- [Langgraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Vercel AI SDK](https://sdk.vercel.ai/)

---

## 🚀 다음 단계

1. **전체 데이터 로드**: `uv run python load_data.py` (시간 소요)
2. **검색 품질 평가**: 다양한 쿼리로 테스트
3. **Agent 웹 앱 탐색**: `cd agent_app && pnpm dev`
4. **커스터마이징**: 검색 파라미터 조정, 프롬프트 개선

---

**문서 작성일**: 2025-12-14
**프로젝트 버전**: 0.1.0
**마지막 업데이트**: 2025-12-14
