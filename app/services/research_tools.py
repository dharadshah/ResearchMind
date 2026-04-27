from langchain_core.tools import tool
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper, DuckDuckGoSearchAPIWrapper
from app.services.vector_store import VectorStoreGateway
from app.constants.messages import TOOL_NO_RESULTS, TOOL_EXECUTION_FAILED
from app.constants.app_constants import ToolName
from app.config.settings import settings



_wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2))
_arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=2))
_ddg = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper())


@tool
def search_documents(query: str) -> str:
    """Search the ingested documents in the local vector store.
    Use this tool first before searching the web or Wikipedia.
    Returns the most relevant chunks from ingested documents."""
    try:
        store = VectorStoreGateway.get_store()

        if settings.enable_reranking:
            results = VectorStoreGateway.search_and_rerank(query, top_k=settings.reranker_top_k)
        else:
            results = store.search(query, top_k=3)

        if not results:
            return TOOL_NO_RESULTS.format(query=query)

        return "\n\n".join(
            f"Source: {r.get('source', 'unknown')}\n"
            f"Score: {r.get('rerank_score', r.get('score', 0)):.4f}\n"
            f"{r.get('text', '')}"
            for r in results
        )
    except ValueError:
        return TOOL_NO_RESULTS.format(query=query)
    except Exception as e:
        return TOOL_EXECUTION_FAILED.format(tool_name="search_documents", error=str(e))


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for factual background information on a topic.
    Use this when the question needs general knowledge or definitions
    that may not be in the ingested documents."""
    try:
        result = _wikipedia.run(query)
        if not result:
            return TOOL_NO_RESULTS.format(query=query)
        return result
    except Exception as e:
        return TOOL_EXECUTION_FAILED.format(tool_name=ToolName.WIKIPEDIA, error=str(e))


@tool
def search_arxiv(query: str) -> str:
    """Search Arxiv for academic papers and research on a topic.
    Use this when the question is about recent research, scientific
    findings, or technical papers."""
    try:
        result = _arxiv.run(query)
        if not result:
            return TOOL_NO_RESULTS.format(query=query)
        return result
    except Exception as e:
        return TOOL_EXECUTION_FAILED.format(tool_name=ToolName.ARXIV, error=str(e))


@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo for current information.
    Use this as a last resort when the vector store, Wikipedia,
    and Arxiv do not have relevant information."""
    try:
        result = _ddg.run(query)
        if not result:
            return TOOL_NO_RESULTS.format(query=query)
        return result
    except Exception as e:
        return TOOL_EXECUTION_FAILED.format(tool_name=ToolName.WEB_SEARCH, error=str(e))


ALL_TOOLS = [search_documents, search_wikipedia, search_arxiv, web_search]  