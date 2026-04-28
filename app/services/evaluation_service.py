from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from app.models.evaluation import EvaluationResult
from app.services.llm_gateway import LLMGateway
from app.config.logging_config import get_logger
from app.constants.app_constants import EvaluationMetric
from app.constants.messages import EVALUATION_NOT_FOUND
from app.constants.prompts import (
    EVALUATION_ANSWER_RELEVANCE_PROMPT,
    EVALUATION_CONTEXT_RELEVANCE_PROMPT,
    EVALUATION_GROUNDEDNESS_PROMPT,
)

logger = get_logger(__name__)


class EvaluationService:

    def __init__(self, db: Session):
        self.db = db

    def _score(self, prompt: str) -> float:
        try:
            model = LLMGateway.get_model()
            result = model.invoke([HumanMessage(content=prompt)])
            score = float(result.content.strip())
            return max(0.0, min(1.0, score))
        except Exception as e:
            logger.error(
                "evaluation | scoring failed | error: %s",
                str(e),
                exc_info=True,
            )
            return 0.0

    def evaluate(
        self,
        question: str,
        context: str,
        response: str,
        conversation_id: int | None = None,
    ) -> EvaluationResult:
        logger.info("evaluation | start | question: %s", question)

        answer_relevance = self._score(
            EVALUATION_ANSWER_RELEVANCE_PROMPT.format(
                question=question,
                response=response,
            )
        )
        logger.info("evaluation | answer_relevance: %.2f", answer_relevance)

        context_relevance = self._score(
            EVALUATION_CONTEXT_RELEVANCE_PROMPT.format(
                question=question,
                context=context,
            )
        )
        logger.info("evaluation | context_relevance: %.2f", context_relevance)

        groundedness = self._score(
            EVALUATION_GROUNDEDNESS_PROMPT.format(
                context=context,
                response=response,
            )
        )
        logger.info("evaluation | groundedness: %.2f", groundedness)

        overall_score = round(
            (answer_relevance + context_relevance + groundedness) / 3, 4
        )
        logger.info("evaluation | overall_score: %.2f", overall_score)

        result = EvaluationResult(
            question=question,
            context=context,
            response=response,
            answer_relevance=answer_relevance,
            context_relevance=context_relevance,
            groundedness=groundedness,
            overall_score=overall_score,
            conversation_id=conversation_id,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_evaluation(self, evaluation_id: int) -> EvaluationResult:
        result = self.db.query(EvaluationResult).filter(
            EvaluationResult.id == evaluation_id
        ).first()
        if not result:
            raise ValueError(
                EVALUATION_NOT_FOUND.format(evaluation_id=evaluation_id)
            )
        return result

    def list_evaluations(
        self,
        conversation_id: int | None = None,
    ) -> list[EvaluationResult]:
        query = self.db.query(EvaluationResult)
        if conversation_id:
            query = query.filter(
                EvaluationResult.conversation_id == conversation_id
            )
        return query.order_by(EvaluationResult.created_at.desc()).all()