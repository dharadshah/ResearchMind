import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_gateway import LLMGateway
from app.services.research_tools import (
    ALL_TOOLS,
    search_documents,
    search_wikipedia,
    search_arxiv,
    web_search,
)
from app.config.settings import settings
from app.constants.prompts import (
    RAG_SYSTEM_PROMPT,
    RELEVANCE_GRADER_PROMPT,
    FALLBACK_RESPONSE,
)
from app.constants.app_constants import AgentDecision, AgentNode, ToolName


os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


class AgentState(TypedDict):
    question: str
    tool_results: list[dict]
    relevant_results: list[dict]
    response: str
    decision: str
    tools_used: list[str]


def tool_selector_node(state: AgentState) -> AgentState:
    model = LLMGateway.get_model()
    model_with_tools = model.bind_tools(ALL_TOOLS)

    result = model_with_tools.invoke([
        HumanMessage(content=state["question"])
    ])

    tool_results = []
    tools_used = []

    if result.tool_calls:
        tool_map = {
            ToolName.VECTOR_SEARCH: search_documents,
            ToolName.WIKIPEDIA: search_wikipedia,
            ToolName.ARXIV: search_arxiv,
            ToolName.WEB_SEARCH: web_search,
        }
        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"].get("query", state["question"])
            if tool_name in tool_map:
                tool_output = tool_map[tool_name].invoke(tool_input)
                tool_results.append({
                    "tool": tool_name,
                    "query": tool_input,
                    "result": tool_output,
                })
                tools_used.append(tool_name)
    else:
        result_output = search_documents.invoke(state["question"])
        tool_results.append({
            "tool": ToolName.VECTOR_SEARCH,
            "query": state["question"],
            "result": result_output,
        })
        tools_used.append(ToolName.VECTOR_SEARCH)

    return {**state, "tool_results": tool_results, "tools_used": tools_used}


def grade_node(state: AgentState) -> AgentState:
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
        AgentDecision.RELEVANT
        if relevant
        else AgentDecision.NOT_RELEVANT
    )
    return {**state, "relevant_results": relevant, "decision": decision}


def generate_node(state: AgentState) -> AgentState:
    context = "\n\n".join(
        f"[{r.get('tool', 'unknown')}]: {r.get('result', '')}"
        for r in state["relevant_results"]
    )
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    model = LLMGateway.get_model()
    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["question"]),
    ])
    return {**state, "response": result.content}


def fallback_node(state: AgentState) -> AgentState:
    return {**state, "response": FALLBACK_RESPONSE}


def route_after_grade(state: AgentState) -> str:
    if state["decision"] == AgentDecision.RELEVANT:
        return AgentDecision.GENERATE
    return AgentDecision.FALLBACK


def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)

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


agent = build_agent()


def run_agent(question: str) -> dict:
    initial_state: AgentState = {
        "question": question,
        "tool_results": [],
        "relevant_results": [],
        "response": "",
        "decision": "",
        "tools_used": [],
    }
    final_state = agent.invoke(initial_state)
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