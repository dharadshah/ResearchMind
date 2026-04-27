import time
from sqlalchemy.orm import Session
from app.models.prompt_template import PromptTemplate
from app.models.prompt_result import PromptResult
from app.schemas.prompt_template import PromptTemplateCreate, PromptRunRequest
from app.services.llm_gateway import LLMGateway
from app.constants.messages import TEMPLATE_NOT_FOUND, TEMPLATE_NAME_EXISTS
from langchain_core.messages import HumanMessage, SystemMessage


class PromptStudioService:

    def __init__(self, db: Session):
        self.db = db

    def create_template(self, data: PromptTemplateCreate) -> PromptTemplate:
        existing = self.db.query(PromptTemplate).filter(
            PromptTemplate.name == data.name
        ).first()
        if existing:
            raise ValueError(TEMPLATE_NAME_EXISTS.format(name=data.name))

        template = PromptTemplate(**data.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_all_templates(self) -> list[PromptTemplate]:
        return self.db.query(PromptTemplate).all()

    def get_template(self, template_id: int) -> PromptTemplate:
        template = self.db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()
        if not template:
            raise ValueError(TEMPLATE_NOT_FOUND.format(template_id=template_id))
        return template

    def run_prompt(self, request: PromptRunRequest) -> PromptResult:
        template = self.get_template(request.template_id)

        filled_prompt = template.user_prompt.format(**request.variable_values)

        messages = []
        if template.system_prompt:
            messages.append(SystemMessage(content=template.system_prompt))
        messages.append(HumanMessage(content=filled_prompt))

        model = LLMGateway.get_model(provider=request.provider)

        start = time.time()
        result = model.invoke(messages)
        latency_ms = int((time.time() - start) * 1000)

        prompt_result = PromptResult(
            template_id=template.id,
            provider=request.provider,
            filled_prompt=filled_prompt,
            response=result.content,
            latency_ms=latency_ms,
        )
        self.db.add(prompt_result)
        self.db.commit()
        self.db.refresh(prompt_result)
        return prompt_result