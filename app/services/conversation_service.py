from sqlalchemy.orm import Session
from app.models.conversation import Conversation, ConversationTurn
from app.constants.messages import CONVERSATION_NOT_FOUND


class ConversationService:

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, title: str | None = None) -> Conversation:
        conversation = Conversation(title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int) -> Conversation:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise ValueError(
                CONVERSATION_NOT_FOUND.format(conversation_id=conversation_id)
            )
        return conversation

    def list_conversations(self) -> list[Conversation]:
        return self.db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).all()

    def add_turn(
        self,
        conversation_id: int,
        question: str,
        response: str,
        decision: str | None = None,
        tools_used: list[str] | None = None,
        sources: list[str] | None = None,
    ) -> ConversationTurn:
        turn = ConversationTurn(
            conversation_id=conversation_id,
            question=question,
            response=response,
            decision=decision,
            tools_used=",".join(tools_used) if tools_used else None,
            sources=",".join(sources) if sources else None,
        )
        self.db.add(turn)
        self.db.commit()
        self.db.refresh(turn)
        return turn

    def get_history(self, conversation_id: int) -> list[dict]:
        conversation = self.get_conversation(conversation_id)
        history = []
        for turn in conversation.turns:
            history.append({
                "role": "user",
                "content": turn.question,
            })
            history.append({
                "role": "assistant",
                "content": turn.response,
            })
        return history