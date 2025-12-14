# 환경 변수 설정 가이드

## Tavily API 키 설정 방법

Agent RAG의 웹 검색 기능을 사용하려면 Tavily API 키가 필요합니다.

### 1. Tavily API 키 발급

1. **Tavily 웹사이트 방문**: https://tavily.com
2. **무료 계정 생성**:
   - "Get Started" 또는 "Sign Up" 클릭
   - 이메일/비밀번호로 가입
3. **API 키 발급**:
   - 로그인 후 Dashboard로 이동
   - "API Keys" 메뉴 선택
   - API 키 복사 (형식: `tvly-...`)

**무료 플랜**:
- 월 1,000 requests 무료
- 대출 검색 Agent에는 충분한 양

### 2. 환경 변수 파일 생성

**Windows (PowerShell):**
```powershell
cd Part3_바이브코딩으로_Hybrid_Search_RAG_구현하기/search_app
Copy-Item .env.example .env
```

**Linux/Mac:**
```bash
cd Part3_바이브코딩으로_Hybrid_Search_RAG_구현하기/search_app
cp .env.example .env
```

### 3. .env 파일 수정

`.env` 파일을 열어서 다음과 같이 설정:

```bash
# PostgreSQL Database URL (필수)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# OpenAI API Key (필수)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Tavily API Key (선택 - Agent RAG 웹 검색 사용 시)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

**설정 값 예시**:
```bash
DATABASE_URL=postgresql://myuser:mypass@ep-cool-sound-123456.us-east-2.aws.neon.tech/neondb
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz
TAVILY_API_KEY=tvly-abcd1234efgh5678ijkl
```

### 4. 환경 변수 확인

**테스트 스크립트 실행**:
```bash
cd advanced_rag_frontend
python test_tools.py
```

**예상 출력**:
```
================================================================================
테스트 1: 대출 상품 검색 (search_loan_products)
================================================================================
검색어: 의사 전용 대출
성공 여부: True
✓ 테스트 1 완료

================================================================================
테스트 2: 웹 검색 (search_web)
================================================================================
검색어: 2025년 금리 전망
성공 여부: True
검색된 결과 수: 3
✓ 테스트 2 완료
```

---

## 환경 변수별 필요성

| 변수 | 필수 여부 | 용도 | 설정 안 하면? |
|------|----------|------|--------------|
| `DATABASE_URL` | ✅ 필수 | Hybrid Search (대출 상품 검색) | Agent 실행 불가 |
| `OPENAI_API_KEY` | ✅ 필수 | LLM 답변 생성 | Agent 실행 불가 |
| `TAVILY_API_KEY` | ⚠️ 선택 | 웹 검색 (최신 뉴스/정책) | 웹 검색 도구만 사용 불가, 대출 검색은 정상 작동 |

---

## Tavily 없이 사용하기

Tavily API 키가 없어도 **대출 상품 검색 기능**은 정상적으로 작동합니다:

```
👤 사용자: "의사 전용 대출이 있나요?"
🤖 Agent: search_loan_products 도구 사용
   → 정상 작동 ✅

👤 사용자: "2025년 금리 전망은?"
🤖 Agent: search_web 도구 시도
   → ⚠️ "TAVILY_API_KEY not configured" 오류
   → "죄송합니다. 웹 검색 기능을 사용할 수 없습니다." 안내
```

---

## 트러블슈팅

### 문제 1: "TAVILY_API_KEY not configured"

**원인**: `.env` 파일에 Tavily API 키가 없음

**해결**:
1. https://tavily.com 에서 API 키 발급
2. `.env` 파일에 `TAVILY_API_KEY=tvly-...` 추가
3. 서버 재시작

### 문제 2: "Invalid API key"

**원인**: 잘못된 API 키 또는 만료된 키

**해결**:
1. Tavily Dashboard에서 API 키 재확인
2. 새 API 키 발급 (필요시)
3. `.env` 파일 업데이트

### 문제 3: 환경 변수가 로드되지 않음

**원인**: `.env` 파일 위치 문제

**확인**:
```bash
# .env 파일이 올바른 위치에 있는지 확인
ls Part3_바이브코딩으로_Hybrid_Search_RAG_구현하기/search_app/.env

# 파일 내용 확인
cat Part3_바이브코딩으로_Hybrid_Search_RAG_구현하기/search_app/.env
```

**해결**: `.env` 파일이 `search_app/` 디렉토리에 있어야 함

---

## 빠른 설정 체크리스트

- [ ] `.env.example`을 `.env`로 복사
- [ ] `DATABASE_URL` 설정 (Neon PostgreSQL 등)
- [ ] `OPENAI_API_KEY` 설정
- [ ] `TAVILY_API_KEY` 설정 (선택)
- [ ] `python test_tools.py` 실행하여 확인
- [ ] 서버 시작: `npm run dev`

---

## 참고 링크

- **Tavily API 문서**: https://docs.tavily.com/
- **Tavily 가격**: https://tavily.com/pricing (무료 플랜 1000 requests/월)
- **OpenAI API 키**: https://platform.openai.com/api-keys
- **Neon PostgreSQL**: https://neon.tech/

---

문제가 계속되면 `test_tools.py` 실행 결과를 공유해주세요!
