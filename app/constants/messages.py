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