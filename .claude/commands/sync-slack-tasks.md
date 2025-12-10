# Slack Tasks Sync Command

어제 올라온 Slack 메시지를 스캔하여 중요한 태스크를 Notion DB에 자동으로 동기화합니다.

## 주요 기능

### 1. 채널 스캔 및 메시지 필터링
- 대상 채널: #engineering, #product, #support
- 어제 날짜의 메시지만 스캔
- 중요 메시지 기준:
  - 리액션 5개 이상
  - 긴급 키워드 포함: "urgent", "긴급", "asap", "장애"
  - @channel 또는 @here 멘션 포함
- ✅ 리액션이 있는 메시지는 제외 (이미 처리됨)

### 2. 자동 분류 시스템
**Priority 분류:**
- High: 긴급 키워드 포함 ("urgent", "긴급", "asap", "장애")
- Medium: 중요 키워드 포함 ("important", "중요", "blocker", "차단")
- Low: 그 외

**Category 분류:**
- Bug: "bug", "버그", "에러", "error", "장애"
- Feature: "feature", "기능", "개발", "추가"
- Improvement: "개선", "리팩토링", "refactor", "최적화"
- Other: 위 카테고리에 해당하지 않는 경우

### 3. Notion DB 연동
Notion 데이터베이스 URL: https://www.notion.so/koomook/d7ca1f0cc3c64dff9618932ee4ab95e7

생성되는 태스크 필드:
- **Title**: 메시지 첫 50자 요약
- **Category**: 자동 분류된 카테고리
- **Priority**: High/Medium/Low
- **Status**: 항상 "New"로 시작
- **Source Channel**: 메시지가 올라온 채널명
- **Source URL**: Slack 메시지 직접 링크
- **Content**: 메시지 전체 내용

### 4. Slack 피드백
각 처리된 메시지에:
- ✅ 리액션 추가 (중복 처리 방지)
- 스레드에 Notion 페이지 링크 답글

### 5. 일일 요약 보고서
#daily-standup 채널에 다음 내용 전송:
```
📊 **어제 Slack 태스크 동기화 결과**

**우선순위별:**
- 🔴 High: X개
- 🟡 Medium: Y개
- 🟢 Low: Z개

**카테고리별:**
- 🐛 Bug: A개
- ✨ Feature: B개
- 🔧 Improvement: C개
- 📌 Other: D개

**태스크 목록:**
[우선순위 High 태스크들...]
[우선순위 Medium 태스크들...]
[우선순위 Low 태스크들...]

📎 전체 보기: [Notion DB 링크]
```

## 실행 단계

### 1단계: 채널 정보 조회
Slack API를 사용하여 다음 채널들의 ID를 조회합니다:
- #engineering
- #product
- #support
- #daily-standup (보고서 전송용)

채널이 존재하지 않으면 현재 존재하는 채널로 대체하여 진행합니다.

**API**: `GET /conversations.list`

### 2단계: 어제 메시지 수집
각 채널에서 어제(24시간 전 ~ 오늘 00:00) 메시지를 가져옵니다.

**API**: `GET /conversations.history?oldest={yesterday_timestamp}&latest={today_timestamp}`

다음 조건을 만족하는 메시지만 선별:
- 리액션 총합이 5개 이상 OR
- 긴급 키워드 포함: "urgent", "긴급", "asap", "장애" OR
- @channel 또는 @here 멘션 포함 (텍스트에 "<!channel>" 또는 "<!here>" 포함)

**중요**: ✅ (white_check_mark) 리액션이 이미 있는 메시지는 제외 (중복 방지)

### 3단계: 메시지 자동 분류
각 선별된 메시지를 다음 기준으로 분류:

**Priority 분류** (대소문자 구분 없이):
- **High**: "urgent", "긴급", "asap", "장애", "critical" 키워드 포함
- **Medium**: "important", "중요", "blocker", "차단" 키워드 포함
- **Low**: 그 외

**Category 분류** (대소문자 구분 없이):
- **Bug**: "bug", "버그", "에러", "error", "장애", "오류" 키워드 포함
- **Feature**: "feature", "기능", "개발", "추가", "구현" 키워드 포함
- **Improvement**: "개선", "리팩토링", "refactor", "최적화", "optimize" 키워드 포함
- **Other**: 위 카테고리에 해당하지 않는 경우

### 4단계: Notion DB 구조 확인
Notion 데이터베이스를 조회하여 사용 가능한 속성을 확인합니다.

**API**: `GET /databases/{database_id}`

사용할 DB ID: `2c5673df-ae4b-81be-aa55-fc9b968b2d25` (Tasks from Slack)

필요한 속성:
- Name (title)
- Status (select): "To Do" 사용
- Priority (select): "High", "Medium", "Low"
- Category (select): "Bug", "Feature", "Other"
- Source Channel (rich_text)
- Source URL (url)

### 5단계: Notion 태스크 생성
각 선별된 메시지에 대해 Notion 페이지를 생성합니다.

**API**: `POST /pages`

생성할 속성:
- **Title**: 메시지 내용의 첫 50자 (이모지 및 특수문자 정리)
- **Status**: "To Do"로 설정
- **Priority**: 3단계에서 분류된 우선순위
- **Category**: 3단계에서 분류된 카테고리
- **Source Channel**: 메시지가 올라온 채널명 (예: #engineering)
- **Source URL**: Slack 메시지 퍼머링크
  - 형식: `https://{workspace}.slack.com/archives/{channel_id}/p{timestamp_without_dot}`
  - 예: `https://the-oneit.slack.com/archives/C09J5J2883W/p1765375856930339`

### 6단계: Slack 피드백
각 처리된 메시지에 대해:

1. **리액션 추가**
   - **API**: `POST /reactions.add`
   - 리액션: `white_check_mark` (✅)

2. **스레드 답글 작성**
   - **API**: `POST /chat.postMessage`
   - 메시지: `"Created Notion task: {notion_page_url}"`
   - `thread_ts` 파라미터에 원본 메시지의 `ts` 값 사용

### 7단계: 일일 보고서 생성 및 전송
#daily-standup 채널에 다음 형식의 보고서를 전송:

**API**: `POST /chat.postMessage`

```
📊 **어제 Slack 태스크 동기화 결과**

**처리된 메시지**: {총 개수}개

**우선순위별:**
🔴 High: {high_count}개
🟡 Medium: {medium_count}개
🟢 Low: {low_count}개

**카테고리별:**
🐛 Bug: {bug_count}개
✨ Feature: {feature_count}개
🔧 Improvement: {improvement_count}개
📌 Other: {other_count}개

**High Priority 태스크:**
{high_priority_tasks}

**Medium Priority 태스크:**
{medium_priority_tasks}

📎 전체 태스크 보기: https://www.notion.so/2c5673dfae4b81beaa55fc9b968b2d25
```

각 태스크 항목 형식: `- {title} (#{channel_name}) - {notion_url}`

### 에러 처리
- 채널을 찾을 수 없으면: 사용자에게 알리고 사용 가능한 채널로 대체
- Notion DB 접근 실패: 에러 메시지 출력 및 중단
- 개별 메시지 처리 실패: 해당 메시지 스킵하고 계속 진행
- Slack API 에러: 재시도 1회, 실패 시 에러 로그 출력

### 실행 순서 요약
1. 채널 ID 조회 (engineering, product, support, daily-standup)
2. 어제 메시지 수집 및 필터링 (리액션 5개+, 긴급 키워드, @channel/@here)
3. 메시지 자동 분류 (Priority: High/Medium/Low, Category: Bug/Feature/Improvement/Other)
4. Notion DB 구조 확인
5. Notion 태스크 생성 (각 메시지마다)
6. Slack 피드백 (✅ 리액션 + 스레드 답글)
7. daily-standup 채널에 요약 보고서 전송

완료 후 생성된 태스크 개수와 Notion DB 링크를 사용자에게 출력합니다.
