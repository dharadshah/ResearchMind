from sentence_transformers import CrossEncoder
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class Reranker:

    _model: CrossEncoder | None = None

    @classmethod
    def get_model(cls) -> CrossEncoder:
        if cls._model is None:
            logger.info("reranker | loading cross-encoder model: %s", settings.reranker_model)
            cls._model = CrossEncoder(settings.reranker_model)
            logger.info("reranker | model loaded successfully")
        return cls._model

    @classmethod
    def rerank(cls, query: str, results: list[dict], top_k: int | None = None) -> list[dict]:
        if not results:
            return results

        top_k = top_k or settings.reranker_top_k

        try:
            model = cls.get_model()
            pairs = [[query, r.get("text", "")] for r in results]
            scores = model.predict(pairs)

            scored_results = [
                {**result, "rerank_score": float(score)}
                for result, score in zip(results, scores)
            ]

            scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)
            top_results = scored_results[:top_k]

            logger.info(
                "reranker | reranked %d results to top %d",
                len(results),
                len(top_results),
            )
            return top_results

        except Exception as e:
            logger.error("reranker | reranking failed | error: %s", str(e), exc_info=True)
            return results[:top_k]