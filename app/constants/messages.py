# app/constants/messages.py

DOCUMENT_NOT_FOUND = "Document with id {document_id} was not found."
DOCUMENT_INGESTED = "Document ingested successfully."
DOCUMENT_INGESTION_FAILED = "Document ingestion failed. Please try again."

QUERY_EMPTY = "Query cannot be empty."
QUERY_TOO_LONG = "Query exceeds the maximum allowed length."

LLM_UNAVAILABLE = "The LLM provider is currently unavailable. Please try again."
PROVIDER_NOT_SUPPORTED = "LLM provider '{provider}' is not supported."