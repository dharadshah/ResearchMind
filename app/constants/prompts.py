# app/constants/prompts.py

HEALTH_CHECK_MESSAGE = "ResearchMind is running."

# Document ingestion prompts will be added in Phase 3
FEW_SHOT_EXAMPLE_PROMPT = (
    "You are a helpful assistant. Here are some examples:\n\n"
    "{examples}\n\n"
    "Now answer the following:\n{question}"
)

CHAIN_OF_THOUGHT_PROMPT = (
    "You are a careful reasoner. Think step by step before giving your final answer.\n\n"
    "Question: {question}"
)

SYSTEM_USER_ROLE_PROMPT = (
    "You are {role}. Your task is to {task}.\n\n"
    "Input: {input}"
)

RAG_SYSTEM_PROMPT = (
    "You are a research assistant. Answer the user's question using only the "
    "provided context. If the context does not contain enough information to "
    "answer the question, say so clearly. Do not make up information.\n\n"
    "Context:\n{context}"
)

RELEVANCE_GRADER_PROMPT = (
    "You are a relevance grader. Given a user question and a retrieved result, "
    "decide if the result is relevant to answering the question.\n\n"
    "Question: {question}\n\n"
    "Result: {result}\n\n"
    "Respond with only 'yes' or 'no'."
)

FALLBACK_RESPONSE = (
    "I could not find relevant information to answer your question. "
    "Please try rephrasing or ingesting more documents."
)