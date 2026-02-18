"""
Shared utilities for graph nodes.
"""

import json
import re


def extract_json(text: str) -> dict:
    """
    Robustly extract a JSON object from an LLM response.

    Handles:
    - Plain JSON: {"key": "value"}
    - Markdown-fenced JSON: ```json\\n{...}\\n```
    - Markdown-fenced without language tag: ```\\n{...}\\n```
    - Leading/trailing whitespace or extra text around the JSON block
    """
    # Strip whitespace
    text = text.strip()

    # Try 1: direct parse (clean JSON response)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try 2: strip markdown code fences (```json ... ``` or ``` ... ```)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # Try 3: find the first {...} block anywhere in the text
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    # Try 4: find the first [...] block (for array responses)
    bracket_match = re.search(r"\[.*\]", text, re.DOTALL)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from response: {text[:200]}")
