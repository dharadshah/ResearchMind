import os
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
from app.config.settings import settings
from app.config.logging_config import get_logger
from app.constants.prompts import (
    RELEVANCE_GRADER_PROMPT,
    FALLBACK_RESPONSE,
    MEMORY_AWARE_SYSTEM_PROMPT,
    SUMMARY_SECTION,
    RELEVANT_MEMORY_SECTION,
)
from app.constants.app_constants import AgentDecision, AgentNode, ToolName

logger = get_logger(__name__)

os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


class ResearchState(TypedDict):
    question: str
    history: list[dict]
    memory_context: dict
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
            logger.info(
                "research_agent | tool_call | name: %s | args: %s",
                tool_name,
                tool_args,
            )
            if tool_name in tool_map:
                tool_output = tool_map[tool_name].invoke(tool_args)
                tool_results.append({
                    "tool": tool_name,
                    "query": tool_args.get("query", state["question"]),
                    "result": tool_output,
                })
                tools_used.append(tool_name)
    else:
        logger.warning(
            "research_agent | no tool calls returned, defaulting to search_documents"
        )
        tool_output = search_documents.invoke({
            "query": state["question"],
            "top_k": 3,
            "source_filter": None,
        })
        tool_results.append({
            "tool": "search_documents",
            "query": state["question"],
            "result": tool_output,
        })
        tools_used.append("search_documents")

    return {**state, "tool_results": tool_results, "tools_used": tools_used}


def grade_node(state: ResearchState) -> ResearchState:
    logger.info(
        "research_agent | grade_node | grading %d results",
        len(state["tool_results"]),
    )
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

    decision = (
        AgentDecision.RELEVANT if relevant else AgentDecision.NOT_RELEVANT
    )
    logger.info("research_agent | grade_node | decision: %s", decision)
    return {**state, "relevant_results": relevant, "decision": decision}


def generate_node(state: ResearchState) -> ResearchState:
    logger.info(
        "research_agent | generate_node | generating from %d relevant results",
        len(state["relevant_results"]),
    )

    context = "\n\n".join(
        f"[{r.get('tool', 'unknown')}]: {r.get('result', '')}"
        for r in state["relevant_results"]
    )

    memory_context = state.get("memory_context", {})
    summary = memory_context.get("summary", "")
    relevant_memory = memory_context.get("relevant_memory", "")

    summary_section = SUMMARY_SECTION.format(summary=summary) if summary else ""
    relevant_memory_section = (
        RELEVANT_MEMORY_SECTION.format(relevant_memory=relevant_memory)
        if relevant_memory else ""
    )

    system_prompt = MEMORY_AWARE_SYSTEM_PROMPT.format(
        summary_section=summary_section,
        relevant_memory_section=relevant_memory_section,
        context=context,
    )

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
    logger.warning(
        "research_agent | fallback_node | no relevant results for: %s",
        state["question"],
    )
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


def run_research_agent(
    question: str,
    history: list[dict] | None = None,
    memory_context: dict | None = None,
) -> dict:
    logger.info("run_research_agent | start | question: %s", question)
    initial_state: ResearchState = {
        "question": question,
        "history": history or [],
        "memory_context": memory_context or {},
        "tool_results": [],
        "relevant_results": [],
        "response": "",
        "decision": "",
        "tools_used": [],
    }
    final_state = research_agent.invoke(initial_state)
    logger.info(
        "run_research_agent | complete | decision: %s | tools_used: %s",
        final_state["decision"],
        final_state["tools_used"],
    )
    return {
        "question": final_state["question"],
        "response": final_state["response"],
        "decision": final_state["decision"],
        "tools_used": final_state["tools_used"],
        "sources": [
            r.get("tool", "") for r in final_state["relevant_results"]
        ],
        "chunk_count": len(final_state["relevant_results"]),
    }