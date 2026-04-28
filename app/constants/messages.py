# app/constants/messages.py

DOCUMENT_NOT_FOUND = "Document with id {document_id} was not found."
DOCUMENT_INGESTED = "Document ingested successfully."
DOCUMENT_INGESTION_FAILED = "Document ingestion failed. Please try again."

QUERY_EMPTY = "Query cannot be empty."
QUERY_TOO_LONG = "Query exceeds the maximum allowed length."

LLM_UNAVAILABLE = "The LLM provider is currently unavailable. Please try again."
PROVIDER_NOT_SUPPORTED = "LLM provider '{provider}' is not supported."

TEMPLATE_NOT_FOUND = "Prompt template with id {template_id} was not found."
TEMPLATE_NAME_EXISTS = "A prompt template with name '{name}' already exists."
TEMPLATE_CREATED = "Prompt template created successfully."
PROMPT_RUN_FAILED = "Failed to run prompt. Please try again."

VECTOR_STORE_NOT_INITIALIZED = "Vector store has not been initialized yet. Please ingest documents first."
VECTOR_STORE_PROVIDER_NOT_SUPPORTED = "Vector store provider '{provider}' is not supported."
EMBEDDING_FAILED = "Failed to generate embeddings. Please try again."

INGESTION_STARTED = "Document ingestion started for '{source}'."
INGESTION_COMPLETE = "Document '{source}' ingested successfully with {chunk_count} chunks."
INGESTION_FAILED = "Failed to ingest document '{source}'. Please try again."
URL_FETCH_FAILED = "Failed to fetch content from URL '{url}'."

TOOL_EXECUTION_FAILED = "Tool '{tool_name}' failed to execute: {error}"
TOOL_NO_RESULTS = "No results found for query: '{query}'"

AGENT_RUN_FAILED = "The research agent failed to process your query. Please try again."

CONVERSATION_NOT_FOUND = "Conversation with id {conversation_id} was not found."
CONVERSATION_CREATED = "Conversation created successfully."

HITL_AWAITING_APPROVAL = "Agent paused. Please review the intent and approve or override to continue."
HITL_RESUMED = "Agent resumed successfully."
HITL_THREAD_NOT_FOUND = "No paused session found for thread_id '{thread_id}'."
HITL_REJECTED = "Query rejected by user."

RERANKING_FAILED = "Reranking failed, falling back to original ranking."

MEMORY_SUMMARY_FAILED = "Failed to summarise conversation history."
MEMORY_RETRIEVAL_FAILED = "Failed to retrieve relevant memory."

EVALUATION_FAILED = "Evaluation failed. Please try again."
EVALUATION_NOT_FOUND = "Evaluation with id {evaluation_id} was not found."

PROMPT_INJECTION_DETECTED = "Input blocked: prompt injection pattern detected."
PII_MASKED = "PII detected and masked in input."
SECURITY_SCAN_FAILED = "Security scan failed. Please try again."
SECURITY_LOG_NOT_FOUND = "Security log with id {log_id} was not found."

INPUT_GUARDRAIL_BLOCKED = "Your input was blocked by the guardrail. Please rephrase your question."
OUTPUT_GUARDRAIL_BLOCKED = "The response was blocked by the output guardrail. Please try a different question."
GUARDRAIL_CHECK_FAILED = "Guardrail check failed. Proceeding with caution."