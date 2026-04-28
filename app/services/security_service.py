from sqlalchemy.orm import Session
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from langchain_core.messages import HumanMessage
from app.models.security_log import SecurityLog
from app.services.llm_gateway import LLMGateway
from app.config.logging_config import get_logger
from app.constants.app_constants import (
    SecurityFlag,
    PROMPT_INJECTION_PATTERNS,
    GuardrailStatus,
    TECHNICAL_TERMS_ALLOWLIST,
)
from app.constants.messages import (
    PROMPT_INJECTION_DETECTED,
    PII_MASKED,
    SECURITY_LOG_NOT_FOUND,
    GUARDRAIL_CHECK_FAILED,
)
from app.constants.prompts import INPUT_GUARDRAIL_PROMPT, OUTPUT_GUARDRAIL_PROMPT
import json

logger = get_logger(__name__)


class SecurityService:

    _analyzer: AnalyzerEngine | None = None
    _anonymizer: AnonymizerEngine | None = None

    @classmethod
    def get_analyzer(cls) -> AnalyzerEngine:
        if cls._analyzer is None:
            logger.info("security | loading presidio analyzer")
            cls._analyzer = AnalyzerEngine()
        return cls._analyzer

    @classmethod
    def get_anonymizer(cls) -> AnonymizerEngine:
        if cls._anonymizer is None:
            logger.info("security | loading presidio anonymizer")
            cls._anonymizer = AnonymizerEngine()
        return cls._anonymizer

    def __init__(self, db: Session):
        self.db = db

    def _detect_injection(self, text: str) -> tuple[bool, str | None]:
        text_lower = text.lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern in text_lower:
                logger.warning(
                    "security | injection detected | pattern: %s", pattern
                )
                return True, f"Matched pattern: '{pattern}'"
        return False, None

    def _detect_and_mask_pii(self, text: str) -> tuple[str, list[str]]:
        try:
            analyzer = self.get_analyzer()
            anonymizer = self.get_anonymizer()
            results = analyzer.analyze(text=text, language="en")

            if not results:
                return text, []

            filtered_results = []
            for r in results:
                detected_text = text[r.start:r.end].lower()
                if detected_text in TECHNICAL_TERMS_ALLOWLIST:
                    logger.info(
                        "security | skipping allowlisted term: %s", detected_text
                    )
                    continue
                filtered_results.append(r)

            if not filtered_results:
                return text, []

            entity_types = list({r.entity_type for r in filtered_results})
            anonymized = anonymizer.anonymize(
                text=text, analyzer_results=filtered_results
            )
            logger.info("security | PII detected | entities: %s", entity_types)
            return anonymized.text, entity_types

        except Exception as e:
            logger.error(
                "security | PII detection failed | error: %s",
                str(e),
                exc_info=True,
            )
            return text, []

    def _run_llm_guardrail(self, prompt: str) -> tuple[bool, str | None]:
        try:
            model = LLMGateway.get_model()
            result = model.invoke([HumanMessage(content=prompt)])
            content = result.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            is_safe = data.get("is_safe", True)
            reason = data.get("reason", None)
            return is_safe, reason
        except Exception as e:
            logger.error(
                "security | guardrail LLM check failed | error: %s",
                str(e),
                exc_info=True,
            )
            return True, GUARDRAIL_CHECK_FAILED

    def check_input_guardrail(self, text: str) -> dict:
        prompt = INPUT_GUARDRAIL_PROMPT.format(input=text)
        is_safe, reason = self._run_llm_guardrail(prompt)
        status = GuardrailStatus.PASSED if is_safe else GuardrailStatus.BLOCKED
        logger.info(
            "security | input guardrail | status: %s | reason: %s",
            status, reason,
        )
        return {
            "is_safe": is_safe,
            "reason": reason,
            "status": status,
        }

    def check_output_guardrail(self, output: str) -> dict:
        prompt = OUTPUT_GUARDRAIL_PROMPT.format(output=output)
        is_safe, reason = self._run_llm_guardrail(prompt)
        status = GuardrailStatus.PASSED if is_safe else GuardrailStatus.BLOCKED
        logger.info(
            "security | output guardrail | status: %s | reason: %s",
            status, reason,
        )
        return {
            "is_safe": is_safe,
            "reason": reason,
            "status": status,
        }

    def scan(self, text: str) -> dict:
        is_injection, injection_reason = self._detect_injection(text)

        if is_injection:
            log = SecurityLog(
                original_input=text,
                sanitised_input=None,
                flag=SecurityFlag.PROMPT_INJECTION,
                reason=injection_reason,
                pii_entities=None,
                blocked=True,
            )
            self.db.add(log)
            self.db.commit()
            logger.warning("security | input blocked | reason: %s", injection_reason)
            return {
                "original_input": text,
                "sanitised_input": text,
                "flag": SecurityFlag.PROMPT_INJECTION,
                "reason": injection_reason,
                "pii_entities": [],
                "blocked": True,
            }

        masked_text, pii_entities = self._detect_and_mask_pii(text)

        if pii_entities:
            log = SecurityLog(
                original_input=text,
                sanitised_input=masked_text,
                flag=SecurityFlag.PII_DETECTED,
                reason=PII_MASKED,
                pii_entities=",".join(pii_entities),
                blocked=False,
            )
            self.db.add(log)
            self.db.commit()
            return {
                "original_input": text,
                "sanitised_input": masked_text,
                "flag": SecurityFlag.PII_DETECTED,
                "reason": PII_MASKED,
                "pii_entities": pii_entities,
                "blocked": False,
            }

        return {
            "original_input": text,
            "sanitised_input": text,
            "flag": SecurityFlag.CLEAN,
            "reason": None,
            "pii_entities": [],
            "blocked": False,
        }

    def update_log_with_guardrails(
        self,
        log_id: int,
        input_guardrail_status: str,
        input_guardrail_reason: str | None,
        output_guardrail_status: str,
        output_guardrail_reason: str | None,
    ) -> None:
        log = self.db.query(SecurityLog).filter(
            SecurityLog.id == log_id
        ).first()
        if log:
            log.input_guardrail_status = input_guardrail_status
            log.input_guardrail_reason = input_guardrail_reason
            log.output_guardrail_status = output_guardrail_status
            log.output_guardrail_reason = output_guardrail_reason
            self.db.commit()

    def create_security_log(
        self,
        original_input: str,
        sanitised_input: str,
        flag: str,
        reason: str | None,
        pii_entities: list[str],
        blocked: bool,
        input_guardrail_status: str | None = None,
        input_guardrail_reason: str | None = None,
        output_guardrail_status: str | None = None,
        output_guardrail_reason: str | None = None,
    ) -> SecurityLog:
        log = SecurityLog(
            original_input=original_input,
            sanitised_input=sanitised_input,
            flag=flag,
            reason=reason,
            pii_entities=",".join(pii_entities) if pii_entities else None,
            blocked=blocked,
            input_guardrail_status=input_guardrail_status,
            input_guardrail_reason=input_guardrail_reason,
            output_guardrail_status=output_guardrail_status,
            output_guardrail_reason=output_guardrail_reason,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_log(self, log_id: int) -> SecurityLog:
        log = self.db.query(SecurityLog).filter(
            SecurityLog.id == log_id
        ).first()
        if not log:
            raise ValueError(SECURITY_LOG_NOT_FOUND.format(log_id=log_id))
        return log

    def list_logs(self, blocked_only: bool = False) -> list[SecurityLog]:
        query = self.db.query(SecurityLog)
        if blocked_only:
            query = query.filter(SecurityLog.blocked == True)
        return query.order_by(SecurityLog.created_at.desc()).all()