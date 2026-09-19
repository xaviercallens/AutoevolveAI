"""Tests for code parser and block extraction strategies."""

import pytest

from anse.symbolic.parser import NoCodeFoundError, extract_all_code_blocks, extract_code


def test_parser_python_fenced_block():
    text = "Here is the code:\n```python\ndef add(a, b):\n    return a + b\n```\nHope this helps!"
    res = extract_code(text)
    assert "def add(a, b):" in res.code
    assert res.confidence == 0.95
    assert res.extraction_method == "fenced_python"


def test_parser_generic_fenced_block():
    text = "Here is the solution:\n```\nx = 42\nprint(x)\n```"
    res = extract_code(text)
    assert "x = 42" in res.code
    assert res.confidence == 0.75
    assert res.extraction_method == "fenced_generic"


def test_parser_heuristic_code():
    text = "Here is how you do it:\n\ndef helper():\n    pass\n\nEnjoy!"
    res = extract_code(text)
    assert "def helper():" in res.code
    assert res.confidence == 0.40
    assert res.extraction_method == "heuristic"


def test_parser_no_code_error():
    text = "Just plain conversational text without any code."
    with pytest.raises(NoCodeFoundError):
        extract_code(text)


def test_parser_extract_all_blocks():
    text = (
        "Block 1:\n```python\nx = 1\n```\n"
        "Block 2:\n```python\ny = 2\n```\n"
        "Block 3:\n```\nz = 3\n```"
    )
    blocks = extract_all_code_blocks(text)
    assert len(blocks) == 2
    assert blocks[0].code == "x = 1"
    assert blocks[1].code == "y = 2"


def test_parser_extract_all_generic_blocks():
    # When no python blocks exist, it should fallback to all generic blocks
    text = (
        "Block A:\n```\na = 10\n```\n"
        "Block B:\n```\nb = 20\n```\n"
    )
    blocks = extract_all_code_blocks(text)
    assert len(blocks) == 2
    assert blocks[0].code == "a = 10"
    assert blocks[1].code == "b = 20"
    assert blocks[0].extraction_method == "fenced_generic"
