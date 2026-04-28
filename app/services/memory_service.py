from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.conversation_service import ConversationService
from app.services.vector_store import VectorStoreGateway
from app.services.llm_gateway import LLMGateway
from app.config.settings import settings
from app.constants.prompts import CONVERSATION_SUMMARY_PROMPT
from app.constants.messages import MEMORY_SUMMARY_FAILED, MEMORY_RETRIEVAL_FAILED
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class MemoryService:

    def __init__(self, db: Session):
        self.db = db
        self.conversation_service = ConversationService(db)

    def get_window_history(self, conversation_id: int) -> list[dict]:
        """Buffer Window Memory — returns last N turns only."""
        conversation = self.conversation_service.get_conversation(conversation_id)
        turns = conversation.turns[-settings.memory_window_size:]
        history = []
        for turn in turns:
            history.append({"role": "user", "content": turn.question})
            history.append({"role": "assistant", "content": turn.response})
        logger.info(
            "memory | window history | conversation_id: %d | turns: %d",
            conversation_id,
            len(turns),
        )
        return history

    def get_summary_history(self, conversation_id: int) -> str:
        """Conversation Summary Memory — summarises turns older than window."""
        conversation = self.conversation_service.get_conversation(conversation_id)
        all_turns = conversation.turns
        old_turns = all_turns[:-settings.memory_window_size]

        if not old_turns:
            logger.info(
                "memory | summary history | no old turns to summarise | conversation_id: %d",
                conversation_id,
            )
            return ""

        try:
            history_text = "\n".join(
                f"User: {turn.question}\nAssistant: {turn.response}"
                for turn in old_turns
            )
            prompt = CONVERSATION_SUMMARY_PROMPT.format(history=history_text)
            model = LLMGateway.get_model()
            result = model.invoke([HumanMessage(content=prompt)])
            summary = result.content.strip()

            logger.info(
                "memory | summary generated | conversation_id: %d | old_turns: %d",
                conversation_id,
                len(old_turns),
            )
            return summary

        except Exception as e:
            logger.error(
                "memory | summary failed | error: %s",
                str(e),
                exc_info=True,
            )
            return MEMORY_SUMMARY_FAILED

    def store_turn_in_vector_memory(
        self,
        conversation_id: int,
        question: str,
        response: str,
    ) -> None:
        """Vector Store Retriever Memory — stores turn as embedding."""
        try:
            text = f"User asked: {question}\nAssistant answered: {response}"
            metadata = {
                "type": "conversation_memory",
                "conversation_id": str(conversation_id),
                "source": f"conversation_{conversation_id}",
            }
            store = VectorStoreGateway.get_store()
            store.add([text], [metadata])
            logger.info(
                "memory | stored turn in vector memory | conversation_id: %d",
                conversation_id,
            )
        except Exception as e:
            logger.error(
                "memory | vector store failed | error: %s",
                str(e),
                exc_info=True,
            )

    def retrieve_relevant_memory(self, query: str, conversation_id: int) -> str:
        """Vector Store Retriever Memory — retrieves semantically relevant past turns."""
        try:
            store = VectorStoreGateway.get_store()
            results = store.search(query, top_k=3)

            relevant = [
                r for r in results
                if r.get("type") == "conversation_memory"
                and r.get("conversation_id") == str(conversation_id)
            ]

            if not relevant:
                return ""

            memory_text = "\n\n".join(r.get("text", "") for r in relevant)
            logger.info(
                "memory | retrieved %d relevant memories | conversation_id: %d",
                len(relevant),
                conversation_id,
            )
            return memory_text

        except Exception as e:
            logger.error(
                "memory | retrieval failed | error: %s",
                str(e),
                exc_info=True,
            )
            return ""

    def get_full_memory_context(self, conversation_id: int, question: str) -> dict:
        """Returns all three memory layers combined for injection into the agent."""
        conversation = self.conversation_service.get_conversation(conversation_id)
        total_turns = len(conversation.turns)

        window_history = self.get_window_history(conversation_id)

        summary = ""
        if total_turns > settings.memory_summary_threshold:
            summary = self.get_summary_history(conversation_id)

        relevant_memory = self.retrieve_relevant_memory(question, conversation_id)

        logger.info(
            "memory | full context | conversation_id: %d | total_turns: %d | "
            "window: %d | has_summary: %s | has_relevant: %s",
            conversation_id,
            total_turns,
            len(window_history) // 2,
            bool(summary),
            bool(relevant_memory),
        )

        return {
            "window_history": window_history,
            "summary": summary,
            "relevant_memory": relevant_memory,
        }