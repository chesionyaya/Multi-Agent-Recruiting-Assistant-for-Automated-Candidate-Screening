# LLM Agent Architecture

This module contains the large-model-driven layer for the screening system.

## Folder layout

- `clients/`: model client abstractions and providers.
- `prompts/`: prompt templates and prompt loader.
- `tools/rag/`: retrieval tools (RAG adapters).
- `agents/`: LLM-based JD/CV/Explanation agents.
- `router/`: strategy router to choose `rule`, `llm`, or `hybrid`.
- `pipeline/`: hybrid pipeline orchestration.
- `evals/`: evaluation assets and notes.

## Design principles

1. Keep deterministic scoring in rule-based components.
2. Use LLMs for unstructured understanding and richer explanations.
3. Always keep fallback paths (LLM failure should not break screening).
4. Make routing decision explicit and auditable.
