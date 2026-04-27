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