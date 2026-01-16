def build_factual_qa_judgment_prompt(question: str) -> str:
    return f"""
You are a strict factual evaluator.

Your task:
Inspect the infographic image (provided separately) and answer the binary factual question below.

Rules:
- Answer **1** ONLY if the requirement is clearly satisfied in the image.
- Answer **0** if the requirement is NOT satisfied, unclear, ambiguous, partially met, or cannot be confirmed.
- No partial credit. Ambiguity = 0.
- Base your judgment ONLY on visible evidence in the infographic.
- Even if the image is empty, blank, corrupted, unreadable, or clearly incorrect, you MUST still output a valid JSON object following the required format. In such cases, the answer should be 0.

-------------------------------------
FACTUAL QUESTION:
{question}
-------------------------------------

**Output Format (JSON ONLY)**:
```json
{{
  "analysis": "<your reasoning based strictly on what is visible>",
  "answer": "<0 or 1>"
}}
```
The response must contain only valid JSON.
"""
