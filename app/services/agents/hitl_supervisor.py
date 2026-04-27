from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.services.llm_gateway import LLMGateway
from app.services.agents.research_agent import research_agent
from app.services.agents.summarisation_agent import summarisation_agent
from app.services.agents.fact_check_agent import fact_check_agent
from app.config.database import checkpointer
from app.config.logging_config import get_logger
from app.constants.prompts import SUPERVISOR_INTENT_PROMPT
from app.constants.app_constants import AgentName, QueryIntent

logger = get_logger(__name__)


class HITLSupervisorState(TypedDict):
    question: str
    history: list[dict]
    intent: str
    response: str
    decision: str
    tools_used: list[str]
    agent_used: str


def classify_intent_node(state: HITLSupervisorState) -> HITLSupervisorState:
    logger.info("hitl_supervisor | classify_intent | question: %s", state["question"])
    model = LLMGateway.get_model()
    prompt = SUPERVISOR_INTENT_PROMPT.format(question=state["question"])
    result = model.invoke([HumanMessage(content=prompt)])
    intent = result.content.strip().lower()

    if intent not in QueryIntent.ALL:
        logger.warning("hitl_supervisor | unknown intent '%s', defaulting to research", intent)
        intent = QueryIntent.RESEARCH

    logger.info("hitl_supervisor | intent classified as: %s", intent)
    return {**state, "intent": intent}


def route_to_agent(state: HITLSupervisorState) -> str:
    return state["intent"]


def research_node(state: HITLSupervisorState) -> HITLSupervisorState:
    logger.info("hitl_supervisor | delegating to research_agent")
    result = research_agent.invoke({
        "question": state["question"],
        "history": state["history"],
        "tool_results": [],
        "relevant_results": [],
        "response": "",
        "decision": "",
        "tools_used": [],
    })
    return {
        **state,
        "response": result["response"],
        "decision": result["decision"],
        "tools_used": result["tools_used"],
        "agent_used": AgentName.RESEARCH,
    }


def summarisation_node(state: HITLSupervisorState) -> HITLSupervisorState:
    logger.info("hitl_supervisor | delegating to summarisation_agent")
    result = summarisation_agent.invoke({
        "question": state["question"],
        "history": state["history"],
        "context": "",
        "response": "",
        "decision": "",
        "tools_used": [],
    })
    return {
        **state,
        "response": result["response"],
        "decision": result["decision"],
        "tools_used": result["tools_used"],
        "agent_used": AgentName.SUMMARISATION,
    }


def fact_check_node(state: HITLSupervisorState) -> HITLSupervisorState:
    logger.info("hitl_supervisor | delegating to fact_check_agent")
    result = fact_check_agent.invoke({
        "question": state["question"],
        "history": state["history"],
        "context": "",
        "response": "",
        "decision": "",
        "tools_used": [],
    })
    return {
        **state,
        "response": result["response"],
        "decision": result["decision"],
        "tools_used": result["tools_used"],
        "agent_used": AgentName.FACT_CHECK,
    }


def build_hitl_supervisor() -> StateGraph:
    graph = StateGraph(HITLSupervisorState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node(AgentName.RESEARCH, research_node)
    graph.add_node(AgentName.SUMMARISATION, summarisation_node)
    graph.add_node(AgentName.FACT_CHECK, fact_check_node)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_to_agent,
        {
            QueryIntent.RESEARCH: AgentName.RESEARCH,
            QueryIntent.SUMMARISE: AgentName.SUMMARISATION,
            QueryIntent.FACT_CHECK: AgentName.FACT_CHECK,
        },
    )
    graph.add_edge(AgentName.RESEARCH, END)
    graph.add_edge(AgentName.SUMMARISATION, END)
    graph.add_edge(AgentName.FACT_CHECK, END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=[
            AgentName.RESEARCH,
            AgentName.SUMMARISATION,
            AgentName.FACT_CHECK,
        ],
    )


hitl_supervisor = build_hitl_supervisor()