"""
Pretrained Hugging Face Models for Reddit Audience Research & Candidate Generation.
Leverages locally cached 'answerdotai/ModernBERT-base' for semantic relevance scoring
and 'Qwen/Qwen2.5-0.5B-Instruct' for zero-cost CPU candidate generation and de-escalation.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _extract_mean_pooled_embedding(outputs: Any, attention_mask: Any) -> Any:
    """Extract mean-pooled embedding from model hidden states."""
    mask = attention_mask.unsqueeze(-1)
    return (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1)


class ModernBERTSemanticScorer:
    """
    Semantic relevance scorer utilizing ModernBERT-base representations.
    Scores semantic alignment between Reddit thread context and scientific papers.
    """

    def __init__(self, model_id: str = "answerdotai/ModernBERT-base") -> None:
        self.model_id = model_id
        self._tokenizer: Any = None
        self._model: Any = None
        self._is_available: bool = False
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Attempt to load ModernBERT from local cache."""
        try:
            from transformers import AutoModel, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_id, local_files_only=True
            )
            self._model = AutoModel.from_pretrained(
                self.model_id, local_files_only=True
            )
            self._model.eval()
            self._is_available = True
            logger.info("Successfully loaded ModernBERT from local cache.")
        except Exception as exc:
            logger.debug("ModernBERT not available locally: %s", exc)
            self._is_available = False

    @property
    def is_available(self) -> bool:
        return self._is_available

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute cosine similarity between two texts using ModernBERT embeddings.
        Returns float in [0.0, 1.0].
        """
        if not self._is_available or self._tokenizer is None or self._model is None:
            return self._heuristic_jaccard_similarity(text_a, text_b)

        try:
            import torch

            inputs = self._tokenizer(
                [text_a, text_b],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            with torch.no_grad():
                outputs = self._model(**inputs)
                embeds = _extract_mean_pooled_embedding(outputs, inputs.attention_mask)
                sim = torch.cosine_similarity(embeds[0:1], embeds[1:2]).item()
                # Normalize cosine similarity [-1, 1] to [0, 1]
                return max(0.0, min(1.0, float((sim + 1.0) / 2.0)))
        except Exception as exc:
            logger.debug("ModernBERT embedding calculation error: %s", exc)
            return self._heuristic_jaccard_similarity(text_a, text_b)

    def _heuristic_jaccard_similarity(self, text_a: str, text_b: str) -> float:
        """Fallback token overlap metric when neural weights are unavailable."""
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return float(intersection / max(1, union))


class QwenCPUGenerator:
    """
    CPU-native text generator utilizing Qwen2.5-0.5B-Instruct.
    Synthesizes modest, non-clickbait Reddit drafts and grounded replies.
    """

    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct") -> None:
        self.model_id = model_id
        self._tokenizer: Any = None
        self._model: Any = None
        self._is_available: bool = False
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Attempt to load Qwen2.5-0.5B-Instruct from local cache."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_id, local_files_only=True
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                dtype=torch.float32,
                device_map="cpu",
                local_files_only=True,
            )
            self._model.eval()
            self._is_available = True
            logger.info("Successfully loaded Qwen2.5-0.5B from local cache.")
        except Exception as exc:
            logger.debug("Qwen2.5-0.5B not available locally: %s", exc)
            self._is_available = False

    @property
    def is_available(self) -> bool:
        return self._is_available

    def generate_candidate_title(
        self, paper_title: str, archetype: str
    ) -> str:
        """Generate a focused, modest Reddit title using the local SLM."""
        if not self._is_available or self._tokenizer is None or self._model is None:
            return self._heuristic_title(paper_title, archetype)

        prompt = (
            "<|im_start|>system\n"
            "You are a scientific editor. Write exactly one modest, non-clickbait title "
            "for an academic Reddit post. No hype words.<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Paper: {paper_title}\nFraming: {archetype}\nTitle:<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        return self._execute_generation(prompt, max_new_tokens=40)

    def generate_comment_reply(
        self, user_comment: str, paper_summary: str
    ) -> str:
        """Synthesize a de-escalating, technically grounded reply to a comment."""
        if not self._is_available or self._tokenizer is None or self._model is None:
            return (
                f"Thank you for the thoughtful point. Regarding your observation: "
                f"in our experiments ({paper_summary}), the boundary conditions are explicitly restricted. "
                f"We welcome any counter-examples or benchmark comparisons."
            )

        prompt = (
            "<|im_start|>system\n"
            "You are an academic researcher answering a Reddit question. "
            "Be humble, respectful, mathematically grounded, and de-escalate cynicism.<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Comment: {user_comment}\nContext: {paper_summary}\nResponse:<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        return self._execute_generation(prompt, max_new_tokens=120)

    def _execute_generation(self, prompt: str, max_new_tokens: int) -> str:
        """Run token generation on CPU."""
        try:
            inputs = self._tokenizer(prompt, return_tensors="pt")
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
            )
            input_len = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_len:]
            text = self._tokenizer.decode(generated_tokens, skip_special_tokens=True)
            return text.strip().strip('"').strip("'")
        except Exception as exc:
            logger.debug("Qwen generation error: %s", exc)
            return ""

    def _heuristic_title(self, paper_title: str, archetype: str) -> str:
        """Fallback rule-based title formulation."""
        if archetype == "problem_curiosity":
            return f"Why do standard models fail on {paper_title.lower()}? An invariant-preserving formulation"
        if archetype == "benchmark_comparison":
            return f"[R] Benchmark & ablation study: {paper_title}"
        return f"[R] {paper_title}: Formal verification and implementation"


import urllib.request
import json

class OllamaQwenGenerator:
    """
    CPU-native text generator utilizing Ollama (qwen2.5-coder:1.5b).
    Synthesizes modest, non-clickbait Reddit drafts and grounded replies.
    """

    def __init__(self, model_id: str = "qwen2.5-coder:1.5b") -> None:
        self.model_id = model_id
        self._is_available: bool = False
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = [m["name"] for m in data.get("models", [])]
                if self.model_id in models:
                    self._is_available = True
                    logger.info(f"Ollama loaded successfully with {self.model_id}.")
                else:
                    logger.debug(f"{self.model_id} not found in Ollama tags.")
        except Exception as exc:
            logger.debug(f"Ollama not reachable: {exc}")

    @property
    def is_available(self) -> bool:
        return self._is_available

    def generate_candidate_title(self, paper_title: str, archetype: str) -> str:
        if not self._is_available:
            return self._heuristic_title(paper_title, archetype)
        prompt = (
            "You are a scientific editor. Write exactly one modest, non-clickbait title "
            "for an academic Reddit post. No hype words.\\n"
            f"Paper: {paper_title}\\nFraming: {archetype}\\nTitle:"
        )
        return self._execute_generation(prompt)

    def generate_comment_reply(self, user_comment: str, paper_summary: str) -> str:
        if not self._is_available:
            return (
                f"Thank you for the thoughtful point. Regarding your observation: "
                f"in our experiments ({paper_summary}), the boundary conditions are explicitly restricted. "
                f"We welcome any counter-examples or benchmark comparisons."
            )
        prompt = (
            "You are an academic researcher answering a Reddit question. "
            "Be humble, respectful, mathematically grounded, and de-escalate cynicism.\\n"
            f"Comment: {user_comment}\\nContext: {paper_summary}\\nResponse:"
        )
        return self._execute_generation(prompt)

    def _execute_generation(self, prompt: str) -> str:
        try:
            data = json.dumps({
                "model": self.model_id,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120.0) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "").strip().strip('"').strip("'")
        except Exception as exc:
            logger.debug(f"Ollama generation error: {exc}")
            return ""

    def _heuristic_title(self, paper_title: str, archetype: str) -> str:
        if archetype == "problem_curiosity":
            return f"Why do standard models fail on {paper_title.lower()}? An invariant-preserving formulation"
        if archetype == "benchmark_comparison":
            return f"[R] Benchmark & ablation study: {paper_title}"
        return f"[R] {paper_title}: Formal verification and implementation"
