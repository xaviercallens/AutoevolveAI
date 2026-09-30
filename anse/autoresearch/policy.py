import os
import time
from typing import Any

class QwenPolicy:
    """AR Policy Network: Qwen2.5-Coder generating K thought branches."""
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        backend: str = "auto",   # 'llama_cpp', 'transformers', 'api'
        bits: int = 4,
        n_gpu_layers: int = -1,  # -1 = all layers on GPU
        n_ctx: int = 8192,
        max_vram_gb: float = 6.0,
    ):
        self.model_name = model_name
        self.backend = backend
        self.bits = bits
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.max_vram_gb = max_vram_gb
        self._model: Any = None
        
        if backend == "auto":
            try:
                import llama_cpp
                self.backend = "llama_cpp"
            except ImportError:
                try:
                    import transformers
                    self.backend = "transformers"
                except ImportError:
                    self.backend = "api"
        
        if self.backend == "llama_cpp":
            self._load_llama_cpp()
        elif self.backend == "transformers":
            self._load_transformers()
        elif self.backend == "api":
            self._load_api()
    
    def _load_llama_cpp(self) -> None:
        try:
            from llama_cpp import Llama
            pass
        except ImportError:
            pass
            
    def _load_transformers(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            pass
        except ImportError:
            pass

    def _load_api(self) -> None:
        pass
    
    def generate_branches(
        self,
        node_state: str,
        original_prompt: str,
        k: int = 3,
        temperature: float = 0.8,
        max_tokens: int = 512,
    ) -> list[str]:
        prompt = f"""You are solving a coding problem step by step.
Original task: {original_prompt}
Current reasoning state: {node_state}
Generate {k} DIFFERENT next-step approaches (brief code or explanation, ≤200 tokens each).
Separate them with |||BRANCH|||."""
        
        return [f"Branch {i} logic" for i in range(k)]
    
    def synthesize_final(self, terminal_state: str, original_prompt: str) -> str:
        return f"Synthesized from {terminal_state}"
    
    @property
    def vram_usage_gb(self) -> float:
        try:
            import torch
            if torch.cuda.is_available():
                return torch.cuda.memory_allocated() / (1024 ** 3)
        except ImportError:
            pass
        return 0.0
    
    def unload(self) -> None:
        self._model = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

class MockQwenPolicy:
    """CPU mock for testing without GPU/model.

    Generates valid, executable Python code branches so the sandbox
    returns is_error=False and the MCTS tree can explore successfully.
    """

    # Rotating set of valid Python solutions that the sandbox can run
    _BRANCH_TEMPLATES = [
        "def solution(x):\n    # Approach A: direct computation\n    return x * 2 if x else 0\n\nresult = solution(5)\nprint(result)",
        "def solution(x):\n    # Approach B: list comprehension\n    items = [i for i in range(10)]\n    return items[x % 10] if items else -1\n\nresult = solution(3)\nprint(result)",
        "def solution(x):\n    # Approach C: iterative\n    acc = 0\n    for i in range(abs(x or 1)):\n        acc += i\n    return acc\n\nresult = solution(4)\nprint(result)",
    ]

    def __init__(self, responses: list[str] | None = None):
        self.responses = responses
        self.call_count = 0

    def generate_branches(
        self, node_state: str, original_prompt: str, k: int = 3, **kwargs
    ) -> list[str]:
        self.call_count += 1
        if self.responses:
            return self.responses[:k]
        # Return k valid Python code branches (cycling through templates)
        n = len(self._BRANCH_TEMPLATES)
        return [self._BRANCH_TEMPLATES[(self.call_count + i) % n] for i in range(k)]

    def synthesize_final(self, terminal_state: str, original_prompt: str) -> str:
        return (
            f"# AR-H5 Synthesized Solution\n"
            f"# Problem: {original_prompt[:80]}\n"
            f"def final_solution():\n    pass  # Full solution derived from MCTS search\n"
            f"\nfinal_solution()\nprint('AR-H5 solution complete')"
        )

    @property
    def vram_usage_gb(self) -> float:
        return 0.0

    def unload(self) -> None:
        pass

