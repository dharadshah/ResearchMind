from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.services.llm_gateway import LLMGateway
from app.services.research_tools import (
    ALL_TOOLS,
    search_documents,
    search_wikipedia,
    search_arxiv,
    web_search,
)
from app.config.logging_config import get_logger
from app.constants.prompts import RAG_SYSTEM_PROMPT, RELEVANCE_GRADER_PROMPT, FALLBACK_RESPONSE
from app.constants.app_constants import AgentDecision, AgentNode

logger = get_logger(__name__)


class ResearchState(TypedDict):
    question: str
    history: list[dict]
    tool_results: list[dict]
    relevant_results: list[dict]
    response: str
    decision: str
    tools_used: list[str]


def tool_selector_node(state: ResearchState) -> ResearchState:
    logger.info("research_agent | tool_selector_node | question: %s", state["question"])
    model = LLMGateway.get_model()
    model_with_tools = model.bind_tools(ALL_TOOLS, tool_choice="auto")

    messages = []
    for turn in state["history"]:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=state["question"]))

    result = model_with_tools.invoke(messages)

    tool_results = []
    tools_used = []

    tool_map = {
        "search_documents": search_documents,
        "search_wikipedia": search_wikipedia,
        "search_arxiv": search_arxiv,
        "web_search": web_search,
    }

    if result.tool_calls:
        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            logger.info("research_agent | tool_call | name: %s | args: %s", tool_name, tool_args)
            if tool_name in tool_map:
                tool_output = tool_map[tool_name].invoke(tool_args)
                tool_results.append({
                    "tool": tool_name,
                    "query": tool_args.get("query", state["question"]),
                    "result": tool_output,
                })
                tools_used.append(tool_name)
    else:
        logger.warning("research_agent | no tool calls returned, defaulting to search_documents")
        result_output = search_documents.invoke(state["question"])
        tool_results.append({
            "tool": "search_documents",
            "query": state["question"],
            "result": result_output,
        })
        tools_used.append("search_documents")

    return {**state, "tool_results": tool_results, "tools_used": tools_used}


def grade_node(state: ResearchState) -> ResearchState:
    logger.info("research_agent | grade_node | grading %d results", len(state["tool_results"]))
    model = LLMGateway.get_model()
    relevant = []

    for tool_result in state["tool_results"]:
        prompt = RELEVANCE_GRADER_PROMPT.format(
            question=state["question"],
            result=tool_result.get("result", ""),
        )
        grade = model.invoke([HumanMessage(content=prompt)])
        if grade.content.strip().lower() == "yes":
            relevant.append(tool_result)

    decision = AgentDecision.RELEVANT if relevant else AgentDecision.NOT_RELEVANT
    logger.info("research_agent | grade_node | decision: %s", decision)
    return {**state, "relevant_results": relevant, "decision": decision}


def generate_node(state: ResearchState) -> ResearchState:
    logger.info("research_agent | generate_node | generating response")
    context = "\n\n".join(
        f"[{r.get('tool', 'unknown')}]: {r.get('result', '')}"
        for r in state["relevant_results"]
    )
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    messages = [SystemMessage(content=system_prompt)]
    for turn in state["history"]:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=state["question"]))

    model = LLMGateway.get_model()
    result = model.invoke(messages)
    return {**state, "response": result.content}


def fallback_node(state: ResearchState) -> ResearchState:
    logger.warning("research_agent | fallback_node | no relevant results")
    return {**state, "response": FALLBACK_RESPONSE}


def route_after_grade(state: ResearchState) -> str:
    if state["decision"] == AgentDecision.RELEVANT:
        return AgentDecision.GENERATE
    return AgentDecision.FALLBACK


def build_research_agent() -> StateGraph:
    graph = StateGraph(ResearchState)

    graph.add_node(AgentNode.TOOL_SELECTOR, tool_selector_node)
    graph.add_node(AgentNode.GRADE, grade_node)
    graph.add_node(AgentNode.GENERATE, generate_node)
    graph.add_node(AgentNode.FALLBACK, fallback_node)

    graph.set_entry_point(AgentNode.TOOL_SELECTOR)
    graph.add_edge(AgentNode.TOOL_SELECTOR, AgentNode.GRADE)
    graph.add_conditional_edges(
        AgentNode.GRADE,
        route_after_grade,
        {
            AgentDecision.GENERATE: AgentNode.GENERATE,
            AgentDecision.FALLBACK: AgentNode.FALLBACK,
        },
    )
    graph.add_edge(AgentNode.GENERATE, END)
    graph.add_edge(AgentNode.FALLBACK, END)

    return graph.compile()


research_agent = build_research_agent()