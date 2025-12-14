"""
Langgraph 기반 Routing RAG CLI
질문 분석 → 검색 필요 여부 판단 → Hybrid Search → 답변 생성

스펙:
- Langgraph, LangChain, langchain-openai
- GPT-5-mini

워크플로우:
1. Route: 질문 분석 → search/direct 판단
2. Retrieve: Hybrid Search로 top-3 검색
3. Generate: 답변 생성

핵심 구현:
- StateGraph로 노드 정의 (route, retrieve, generate)
- conditional_edges로 routing
"""
import argparse
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from hybrid_search import hybrid_search

# 환경변수 로드
load_dotenv()

# LLM 초기화 (GPT-5-mini)
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)


# ===== State 정의 =====
class GraphState(TypedDict):
    """RAG 워크플로우 상태"""
    question: str           # 사용자 질문
    route_decision: str     # "search" or "direct"
    documents: list         # 검색된 문서 리스트
    answer: str             # 최종 답변
    debug: bool             # 디버그 모드


# ===== 노드 정의 =====
def route_node(state: GraphState) -> GraphState:
    """
    Route 노드: 질문을 분석하여 검색 필요 여부 판단

    Args:
        state: 현재 그래프 상태

    Returns:
        업데이트된 상태 (route_decision 포함)
    """
    question = state["question"]
    debug = state.get("debug", False)

    if debug:
        print("\n[DEBUG] Route Node: Analyzing question...")

    # LLM으로 질문 분석
    messages = [
        SystemMessage(content="""당신은 질문을 분석하는 전문가입니다.
사용자의 질문이 농협 대출 상품에 대한 구체적인 정보를 요구하는지 판단하세요.

- 대출 상품 검색이 필요한 경우: "search"
- 일반적인 질문이나 인사말: "direct"

예시:
- "의사 전용 대출이 있나요?" → search
- "공무원 대출 한도는?" → search
- "안녕하세요" → direct
- "대출이란 무엇인가요?" → direct

반드시 "search" 또는 "direct" 중 하나만 답변하세요."""),
        HumanMessage(content=question)
    ]

    response = llm.invoke(messages)
    route_decision = response.content.strip().lower()

    # "search" 또는 "direct"만 허용
    if "search" in route_decision:
        route_decision = "search"
    else:
        route_decision = "direct"

    if debug:
        print(f"[DEBUG] Route Decision: {route_decision}")

    return {**state, "route_decision": route_decision}


def retrieve_node(state: GraphState) -> GraphState:
    """
    Retrieve 노드: Hybrid Search로 top-3 문서 검색

    Args:
        state: 현재 그래프 상태

    Returns:
        업데이트된 상태 (documents 포함)
    """
    question = state["question"]
    debug = state.get("debug", False)

    if debug:
        print("\n[DEBUG] Retrieve Node: Running hybrid search...")

    # Hybrid Search 실행 (top-3)
    results = hybrid_search(question, limit=3)

    if debug:
        print(f"[DEBUG] Found {len(results)} documents")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc['product_name']} (score: {doc['rrf_score']:.4f})")

    return {**state, "documents": results}


def generate_node(state: GraphState) -> GraphState:
    """
    Generate 노드: 답변 생성
    검색이 필요한 경우 문서 기반 답변, 아니면 직접 답변

    Args:
        state: 현재 그래프 상태

    Returns:
        업데이트된 상태 (answer 포함)
    """
    question = state["question"]
    route_decision = state["route_decision"]
    documents = state.get("documents", [])
    debug = state.get("debug", False)

    if debug:
        print("\n[DEBUG] Generate Node: Creating answer...")

    if route_decision == "search":
        # 검색된 문서 기반 답변 생성
        if not documents:
            answer = "죄송합니다. 관련 대출 상품을 찾을 수 없습니다. 다른 검색어로 다시 시도해주세요."
        else:
            # 문서 정보를 컨텍스트로 구성
            context_parts = []
            for i, doc in enumerate(documents, 1):
                context_parts.append(f"""
[상품{i}] {doc['product_name']}
- 상품코드: {doc['product_code']}
- 요약: {doc['product_summary']}
- 대상: {doc.get('target_description', '정보 없음')}
- 한도: {doc.get('loan_limit_description', '정보 없음')}
""".strip())

            context = "\n\n".join(context_parts)

            # 시스템 프롬프트
            system_prompt = """당신은 농협 대출 상품 전문 상담사입니다.
검색된 대출 상품 정보를 바탕으로 고객의 질문에 정확하고 친절하게 답변합니다.

답변 원칙:
1. 제공된 문서 정보만을 기반으로 답변
2. 각 정보 뒤에 [상품N] 형태로 출처 표시
3. 불확실한 정보는 명시적으로 표시
4. 상품 비교 시 핵심 차이점 강조
5. 추가 상담이 필요한 경우 안내"""

            # 사용자 프롬프트
            user_prompt = f"""
[검색된 대출 상품 정보]
{context}

[사용자 질문]
{question}

위 정보를 바탕으로 정확하고 친절하게 답변해주세요.
반드시 출처([상품N])를 명시하세요.
""".strip()

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = llm.invoke(messages)
            answer = response.content
    else:
        # 직접 답변
        messages = [
            SystemMessage(content="당신은 친절한 농협 대출 상담사입니다. 사용자의 질문에 간단하고 친절하게 답변하세요."),
            HumanMessage(content=question)
        ]

        response = llm.invoke(messages)
        answer = response.content

    if debug:
        print(f"[DEBUG] Answer generated: {len(answer)} characters")

    return {**state, "answer": answer}


# ===== 조건부 라우팅 함수 =====
def should_retrieve(state: GraphState) -> Literal["retrieve", "generate"]:
    """
    조건부 엣지: route_decision에 따라 retrieve 또는 generate로 라우팅

    Args:
        state: 현재 그래프 상태

    Returns:
        다음 노드 이름 ("retrieve" or "generate")
    """
    route_decision = state["route_decision"]
    if route_decision == "search":
        return "retrieve"
    return "generate"


# ===== 그래프 빌드 =====
def build_graph() -> StateGraph:
    """
    Langgraph 워크플로우 구성

    워크플로우:
    START → route → [conditional] → retrieve → generate → END
                                 → generate → END

    Returns:
        컴파일된 StateGraph 인스턴스
    """
    # StateGraph 생성
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("route", route_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    # 엣지 정의
    workflow.add_edge(START, "route")

    # 조건부 엣지: route → retrieve or generate
    workflow.add_conditional_edges(
        "route",
        should_retrieve,
        {
            "retrieve": "retrieve",
            "generate": "generate"
        }
    )

    # retrieve → generate
    workflow.add_edge("retrieve", "generate")

    # generate → END
    workflow.add_edge("generate", END)

    # 컴파일
    return workflow.compile()


# ===== CLI 진입점 =====
def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="Langgraph Routing RAG CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  uv run python langgraph_rag.py "의사 전용 대출"
  uv run python langgraph_rag.py "공무원 대출" --debug
        """
    )
    parser.add_argument("question", type=str, help="질문 입력")
    parser.add_argument("--debug", action="store_true", help="디버그 모드")

    args = parser.parse_args()

    # 그래프 빌드
    app = build_graph()

    # 초기 상태
    initial_state = {
        "question": args.question,
        "route_decision": "",
        "documents": [],
        "answer": "",
        "debug": args.debug
    }

    # 워크플로우 실행
    if args.debug:
        print("="*80)
        print("Langgraph Routing RAG")
        print("="*80)
        print(f"\n질문: {args.question}\n")

    result = app.invoke(initial_state)

    # 결과 출력
    print("\n" + "="*80)
    print("답변")
    print("="*80)
    print(result["answer"])
    print()


if __name__ == "__main__":
    main()
