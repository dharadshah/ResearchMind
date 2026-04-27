from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_gateway import LLMGateway
from app.services.research_tools import search_wikipedia, web_search
from app.config.logging_config import get_logger
from app.constants.prompts import FACT_CHECK_PROMPT, FALLBACK_RESPONSE
from app.constants.app_constants import AgentDecision

logger = get_logger(__name__)


class FactCheckState(TypedDict):
    question: str
    history: list[dict]
    context: str
    response: str
    decision: str
    tools_used: list[str]


def retrieve_node(state: FactCheckState) -> FactCheckState:
    logger.info("fact_check_agent | retrieve_node | question: %s", state["question"])
    wiki_result = search_wikipedia.invoke(state["question"])
    web_result = web_search.invoke(state["question"])
    context = f"[Wikipedia]:\n{wiki_result}\n\n[Web Search]:\n{web_result}"
    return {
        **state,
        "context": context,
        "tools_used": ["search_wikipedia", "web_search"],
    }


def fact_check_node(state: FactCheckState) -> FactCheckState:
    logger.info("fact_check_agent | fact_check_node | checking claim")
    if not state["context"]:
        return {**state, "response": FALLBACK_RESPONSE, "decision": AgentDecision.NOT_RELEVANT}

    system_prompt = FACT_CHECK_PROMPT.format(
        question=state["question"],
        context=state["context"],
    )
    model = LLMGateway.get_model()
    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["question"]),
    ])
    return {**state, "response": result.content, "decision": AgentDecision.RELEVANT}


def build_fact_check_agent() -> StateGraph:
    graph = StateGraph(FactCheckState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("fact_check", fact_check_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "fact_check")
    graph.add_edge("fact_check", END)

    return graph.compile()


fact_check_agent = build_fact_check_agent()