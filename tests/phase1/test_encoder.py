"""Tests for HiddenStateExtractor and HiddenStateRecord."""

from unittest.mock import MagicMock

import pytest
import torch

from anse.config import ModelConfig
from anse.core.encoder import HiddenStateExtractor, HiddenStateRecord


def test_encoder_mock_initialization():
    config = ModelConfig(hidden_dim=4096)
    extractor = HiddenStateExtractor(config=config, mock_mode=True)
    assert extractor.mock_mode is True
    assert extractor._resolve_device() == "cpu"


def test_encoder_extract_mock_shape():
    config = ModelConfig(hidden_dim=4096)
    extractor = HiddenStateExtractor(config=config, mock_mode=True)
    text, record = extractor.extract("Write fibonacci")

    assert isinstance(text, str)
    assert "def solution" in text
    assert isinstance(record, HiddenStateRecord)
    assert record.hidden_state.shape == (1, 4096)
    assert record.layer_indices == [-1]
    assert record.token_count > 0


def test_encoder_to_embedding():
    tensor = torch.randn(1, 512)
    record = HiddenStateRecord(
        hidden_state=tensor,
        layer_indices=[-1],
        token_count=10,
        model_id="test-model",
        device="cpu",
    )
    emb = record.to_embedding()
    assert isinstance(emb, list)
    assert len(emb) == 512
    assert isinstance(emb[0], float)


def test_encoder_mock_deterministic():
    config = ModelConfig(hidden_dim=128)
    extractor = HiddenStateExtractor(config=config, mock_mode=True)
    prompt = "Test deterministic behavior"

    _, r1 = extractor.extract(prompt)
    _, r2 = extractor.extract(prompt)

    assert torch.equal(r1.hidden_state, r2.hidden_state)


def test_encoder_custom_config():
    cfg = ModelConfig(model_id="Custom/Test-Model", hidden_dim=256, max_new_tokens=64)
    extractor = HiddenStateExtractor(config=cfg, mock_mode=True)
    assert extractor.config.model_id == "Custom/Test-Model"
    assert extractor.config.hidden_dim == 256
    text, record = extractor.extract("Test prompt")
    assert record.hidden_state.shape == (1, 256)


def test_encoder_real_pipeline_mocked_hf():
    extractor = HiddenStateExtractor(config=ModelConfig(device="cpu"), mock_mode=False)

    # Mock tokenizer
    mock_tok = MagicMock()
    mock_tok.apply_chat_template.return_value = "User: test\nAssistant:"
    mock_tok.eos_token_id = 0
    mock_tok.pad_token_id = 0
    mock_tok.return_value = {
        "input_ids": torch.tensor([[1, 2, 3]]),
        "attention_mask": torch.tensor([[1, 1, 1]]),
    }
    mock_tok.decode.return_value = "print('hello')"

    # Mock model
    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")
    mock_outputs = MagicMock()
    mock_outputs.sequences = torch.tensor([[1, 2, 3, 4, 5]])
    # hidden_states: tuple of generation steps. Step 0 has layer states.
    last_hidden = torch.randn(1, 1, 4096)
    mock_outputs.hidden_states = ((last_hidden,),)
    mock_model.generate.return_value = mock_outputs

    extractor._tokenizer = mock_tok
    extractor._model = mock_model

    text, record = extractor.extract("Test prompt", system_prompt="Sys")
    assert text == "print('hello')"
    assert record.hidden_state.shape == (1, 4096)
    assert record.token_count == 2


def test_encoder_device_resolution_cuda(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    config = ModelConfig(device="auto")
    extractor = HiddenStateExtractor(config=config, mock_mode=False)
    assert extractor._resolve_device() == "cuda"


def test_encoder_device_resolution_mps(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    if not hasattr(torch.backends, "mps"):
        monkeypatch.setattr(torch.backends, "mps", MagicMock())
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)

    config = ModelConfig(device="auto")
    extractor = HiddenStateExtractor(config=config, mock_mode=False)
    assert extractor._resolve_device() == "mps"


def test_encoder_transformers_import_error(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "transformers", None)
    config = ModelConfig(device="cpu")
    extractor = HiddenStateExtractor(config=config, mock_mode=False)
    with pytest.raises(ImportError, match="transformers package is required"):
        extractor._load_model_if_needed()


def test_encoder_real_pipeline_no_chat_template():
    extractor = HiddenStateExtractor(config=ModelConfig(device="cpu"), mock_mode=False)

    mock_tok = MagicMock()
    mock_tok.chat_template = None
    mock_tok.eos_token_id = 0
    mock_tok.pad_token_id = 0
    mock_tok.return_value = {
        "input_ids": torch.tensor([[1, 2, 3]]),
        "attention_mask": torch.tensor([[1, 1, 1]]),
    }
    mock_tok.decode.return_value = "no chat template output"

    mock_model = MagicMock()
    mock_model.device = torch.device("cpu")
    mock_outputs = MagicMock()
    mock_outputs.sequences = torch.tensor([[1, 2, 3, 4, 5]])
    last_hidden = torch.randn(1, 1, 4096)
    mock_outputs.hidden_states = ((last_hidden,),)
    mock_model.generate.return_value = mock_outputs

    extractor._tokenizer = mock_tok
    extractor._model = mock_model

    text, record = extractor.extract("Test prompt", temperature=0.0)
    assert text == "no chat template output"
    assert record.hidden_state.shape == (1, 4096)
    assert mock_model.generate.call_args[1]["do_sample"] is False


def test_encoder_transformers_lazy_load_success(monkeypatch):
    import sys

    mock_transformers = MagicMock()
    mock_model = MagicMock()
    mock_transformers.AutoModelForCausalLM.from_pretrained.return_value = mock_model

    monkeypatch.setitem(sys.modules, "transformers", mock_transformers)

    config = ModelConfig(device="cpu", load_in_4bit=False)
    extractor = HiddenStateExtractor(config=config, mock_mode=False)

    extractor._load_model_if_needed()

    assert extractor._model is mock_model
    assert extractor._tokenizer is not None
    # Verify mock model wasn't moved to device since device is CPU and it matches
    mock_model.to.assert_called_with("cpu")


def test_encoder_transformers_lazy_load_4bit(monkeypatch):
    import sys

    mock_transformers = MagicMock()
    mock_transformers.AutoModelForCausalLM.from_pretrained.return_value = MagicMock()

    monkeypatch.setitem(sys.modules, "transformers", mock_transformers)

    config = ModelConfig(device="cuda", load_in_4bit=True)
    extractor = HiddenStateExtractor(config=config, mock_mode=False)

    extractor._load_model_if_needed()

    kwargs = mock_transformers.AutoModelForCausalLM.from_pretrained.call_args[1]
    assert kwargs.get("load_in_4bit") is True
    assert kwargs.get("device_map") == "auto"
