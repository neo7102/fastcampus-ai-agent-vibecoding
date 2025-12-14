# Quick Start Guide

농협 대출 상품 하이브리드 검색 시스템을 빠르게 시작하는 가이드입니다.

## 사전 준비

1. **Neon PostgreSQL 데이터베이스**
   - 프로젝트명: `nonghyup-loan`
   - 필요한 확장: `vector`, `pg_search`

2. **OpenAI API Key**
   - text-embedding-3-small 모델 사용

3. **Python 3.11+ 및 uv**

## 실행 단계

### Step 1: 환경 변수 설정

```bash
cd search_app
cp .env.example .env
```

`.env` 파일을 열어서 다음 값들을 설정하세요:

```
DATABASE_URL=postgresql://user:password@host/neondb?sslmode=require
OPENAI_API_KEY=sk-...
```

### Step 2: 데이터베이스 초기화

Neon 콘솔에 접속하여 SQL Editor에서 `init_db.sql` 파일의 내용을 실행합니다.

또는 psql을 사용:

```bash
psql $DATABASE_URL -f init_db.sql
```

### Step 3: 의존성 설치

```bash
uv sync
```

### Step 4: 데이터 로드 (테스트)

처음에는 소량의 데이터로 테스트하는 것을 권장합니다:

```bash
# 처음 10개 상품만 로드
uv run python load_data.py 10
```

각 상품마다 OpenAI API를 호출하므로 시간이 걸립니다 (10개 기준 약 1-2분).

### Step 5: 검색 테스트

```bash
uv run python hybrid_search.py "공무원 대출"
```

예상 출력:
```
검색어: 공무원 대출

Running BM25 search...
  Found 3 results
Running vector search...
  Found 10 results
Combining with RRF...

================================================================================
검색 결과: 10개
================================================================================

1. 공무원가계자금대출
   상품코드: 40000003
   RRF 점수: 0.0328
   요약: 공무원연금공단에서 융자추천을 받은 공무원 대상 협약대출 상품...
   ...
```

## 전체 데이터 로드 (선택사항)

테스트가 성공적이면 전체 데이터를 로드할 수 있습니다:

```bash
uv run python load_data.py
```

**주의:** 전체 데이터는 수백 개의 상품이 있어 시간이 오래 걸리고 OpenAI API 비용이 발생합니다.

## 문제 해결

### 1. BM25 인덱스 오류

```
ERROR: extension "pg_search" is not available
```

해결: Neon 콘솔에서 `pg_search` 확장을 활성화하세요.

### 2. 벡터 임베딩 오류

```
ERROR: type "vector" does not exist
```

해결: Neon 콘솔에서 `vector` 확장을 활성화하세요.

### 3. OpenAI API 오류

```
openai.AuthenticationError
```

해결: `.env` 파일의 `OPENAI_API_KEY`가 올바른지 확인하세요.

## 다음 단계

- [README.md](README.md)에서 전체 문서 확인
- 다양한 검색어로 테스트 수행
- 검색 결과 품질 분석
