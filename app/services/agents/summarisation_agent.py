from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_gateway import LLMGateway
from app.services.research_tools import search_documents
from app.config.logging_config import get_logger
from app.constants.prompts import SUMMARISATION_PROMPT, FALLBACK_RESPONSE
from app.constants.app_constants import AgentDecision

logger = get_logger(__name__)


class SummarisationState(TypedDict):
    question: str
    history: list[dict]
    context: str
    response: str
    decision: str
    tools_used: list[str]


def retrieve_node(state: SummarisationState) -> SummarisationState:
    logger.info("summarisation_agent | retrieve_node | question: %s", state["question"])
    result = search_documents.invoke(state["question"])
    return {**state, "context": result, "tools_used": ["search_documents"]}


def summarise_node(state: SummarisationState) -> SummarisationState:
    logger.info("summarisation_agent | summarise_node | generating summary")
    if not state["context"]:
        return {**state, "response": FALLBACK_RESPONSE, "decision": AgentDecision.NOT_RELEVANT}

    system_prompt = SUMMARISATION_PROMPT.format(context=state["context"])
    model = LLMGateway.get_model()
    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["question"]),
    ])
    return {**state, "response": result.content, "decision": AgentDecision.RELEVANT}


def build_summarisation_agent() -> StateGraph:
    graph = StateGraph(SummarisationState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("summarise", summarise_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "summarise")
    graph.add_edge("summarise", END)

    return graph.compile()


summarisation_agent = build_summarisation_agent()