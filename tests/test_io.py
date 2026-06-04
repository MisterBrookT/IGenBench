"""Unit tests for igenbench.utils.io — no API keys required."""

import json

import pytest

from igenbench.utils.io import (
    extract_from_markdown,
    split_semantic_and_data_in_t2i_prompt,
)


# ─── extract_from_markdown ────────────────────────────────────────────────────


def test_extract_plain_json_string():
    text = '{"analysis": "good", "answer": "1"}'
    result = extract_from_markdown(text)
    assert result == {"analysis": "good", "answer": "1"}


def test_extract_fenced_json_block():
    text = '```json\n{"analysis": "ok", "answer": "0"}\n```'
    result = extract_from_markdown(text)
    assert result == {"analysis": "ok", "answer": "0"}


def test_extract_fenced_block_no_lang():
    text = "```\nhello world\n```"
    result = extract_from_markdown(text)
    assert result == "hello world"


def test_extract_plain_text_fallback():
    text = "Just some plain text with no code block."
    result = extract_from_markdown(text)
    assert result == text


def test_extract_nested_json_array():
    payload = [{"key": "value"}]
    text = f"```json\n{json.dumps(payload)}\n```"
    result = extract_from_markdown(text)
    assert result == payload


# ─── split_semantic_and_data_in_t2i_prompt ────────────────────────────────────


def test_split_returns_two_parts():
    prompt = "Draw a bar chart. The given data is: Q1=10, Q2=20"
    semantic, data = split_semantic_and_data_in_t2i_prompt(prompt)
    assert semantic == "Draw a bar chart. "
    assert data == " Q1=10, Q2=20"


def test_split_strips_nothing_extra():
    prompt = "Semantic part.The given data is:data part"
    semantic, data = split_semantic_and_data_in_t2i_prompt(prompt)
    assert "Semantic" in semantic
    assert "data part" in data


def test_split_raises_when_separator_missing():
    with pytest.raises(ValueError, match="separator"):
        split_semantic_and_data_in_t2i_prompt("No separator here.")


def test_split_raises_on_empty_string():
    with pytest.raises(ValueError, match="empty or None"):
        split_semantic_and_data_in_t2i_prompt("")


def test_split_raises_on_none():
    with pytest.raises((ValueError, TypeError)):
        split_semantic_and_data_in_t2i_prompt(None)  # type: ignore[arg-type]


def test_split_only_splits_on_first_occurrence():
    prompt = "A.The given data is:B.The given data is:C"
    semantic, data = split_semantic_and_data_in_t2i_prompt(prompt)
    assert semantic == "A."
    assert "B.The given data is:C" in data
