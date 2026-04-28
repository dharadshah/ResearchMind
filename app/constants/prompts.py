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

SUPERVISOR_INTENT_PROMPT = (
    "You are a supervisor agent. Classify the user question into exactly one intent.\n\n"
    "Intents:\n"
    "- research: questions asking what something is, how it works, or requesting information\n"
    "- summarise: questions asking for a summary of a document or topic\n"
    "- fact_check: questions asking to verify a claim or check if something is true\n\n"
    "Question: {question}\n\n"
    "Respond with only one word: research, summarise, or fact_check."
)

SUMMARISATION_PROMPT = (
    "You are a summarisation assistant. Based only on the provided context, "
    "produce a clear and concise summary.\n\n"
    "Context:\n{context}"
)

FACT_CHECK_PROMPT = (
    "You are a fact checking assistant. Based on the provided context, "
    "determine whether the claim is supported, contradicted, or unverifiable.\n\n"
    "Claim: {question}\n\n"
    "Context:\n{context}\n\n"
    "Respond with: Supported, Contradicted, or Unverifiable — followed by a brief explanation."
)

CONVERSATION_SUMMARY_PROMPT = (
    "Summarise the following conversation history into a concise paragraph. "
    "Capture the key topics discussed, questions asked, and answers given. "
    "Be factual and brief.\n\n"
    "Conversation:\n{history}"
)

MEMORY_AWARE_SYSTEM_PROMPT = (
    "You are a research assistant with memory of past conversations.\n\n"
    "{summary_section}"
    "{relevant_memory_section}"
    "Answer the user's question using the provided context.\n\n"
    "Context:\n{context}"
)

SUMMARY_SECTION = (
    "Summary of earlier conversation:\n{summary}\n\n"
)

RELEVANT_MEMORY_SECTION = (
    "Relevant past exchanges:\n{relevant_memory}\n\n"
)

EVALUATION_ANSWER_RELEVANCE_PROMPT = (
    "You are an evaluation assistant. Score how relevant the response is "
    "to the question on a scale of 0.0 to 1.0.\n\n"
    "Question: {question}\n\n"
    "Response: {response}\n\n"
    "Return only a decimal number between 0.0 and 1.0. Nothing else."
)

EVALUATION_CONTEXT_RELEVANCE_PROMPT = (
    "You are an evaluation assistant. Score how relevant the context is "
    "to the question on a scale of 0.0 to 1.0.\n\n"
    "Question: {question}\n\n"
    "Context: {context}\n\n"
    "Return only a decimal number between 0.0 and 1.0. Nothing else."
)

EVALUATION_GROUNDEDNESS_PROMPT = (
    "You are an evaluation assistant. Score how grounded the response is "
    "in the provided context on a scale of 0.0 to 1.0.\n"
    "A score of 1.0 means every claim in the response is supported by the context.\n"
    "A score of 0.0 means the response is entirely unsupported by the context.\n\n"
    "Context: {context}\n\n"
    "Response: {response}\n\n"
    "Return only a decimal number between 0.0 and 1.0. Nothing else."
)