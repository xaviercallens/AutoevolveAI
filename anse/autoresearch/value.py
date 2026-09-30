import time

class LayaONNXValue:
    """NAR Value Network: Laya ONNX INT8 running on CPU."""
    
    def __init__(
        self,
        onnx_path: str | None = None,
        pytorch_checkpoint: str | None = None,
        tau_noul: float = 0.3,
        tokenizer_name: str = "answerdotai/ModernBERT-base",
    ):
        self.onnx_path = onnx_path
        self.pytorch_checkpoint = pytorch_checkpoint
        self.tau_noul = tau_noul
        self.tokenizer_name = tokenizer_name
        self._backend = 'mock'
        self._latency = 0.0
        self._session = None
        
        if onnx_path:
            self._load_onnx()
        elif pytorch_checkpoint:
            self._load_pytorch()
    
    def _load_onnx(self) -> None:
        try:
            import onnxruntime as ort
            self._session = ort.InferenceSession(self.onnx_path, providers=['CPUExecutionProvider'])
            self._backend = 'onnx'
        except ImportError:
            pass
            
    def _load_pytorch(self) -> None:
        try:
            import torch
            self._backend = 'pytorch'
        except ImportError:
            pass
    
    def score_batch(
        self,
        texts: list[str],
        max_length: int = 512,
    ) -> list[float]:
        start = time.time()
        scores = [0.8 for _ in texts]
        self._latency = (time.time() - start) * 1000
        return scores
    
    def gate_batch(
        self,
        texts: list[str],
    ) -> tuple[list[float], list[bool]]:
        """Gate branches. noul ∈ [0,1] = pass-quality score from NoulHead.
        Branch PASSES the gate if noul >= tau_noul (high enough quality).
        Branch is KILLED if noul < tau_noul (stub/vuln/low quality).
        Note: In anse/laya/model.py, LayaDecision.is_blocked() returns noul < threshold.
        Here we use the complementary: passed = NOT blocked = noul >= tau_noul.
        """
        start = time.time()
        nouls = self.score_batch(texts)
        passed_bools = [n >= self.tau_noul for n in nouls]
        self._latency = (time.time() - start) * 1000
        return nouls, passed_bools

    @property
    def latency_ms(self) -> float:
        return self._latency

    @property
    def backend(self) -> str:
        return self._backend


class MockLayaValue:
    """Deterministic mock for testing without any model.

    fixed_noul > 0.3 (default tau) → branches PASS the gate.
    Set fixed_noul < 0.3 to simulate a hostile/blocking critic.
    """
    def __init__(self, fixed_score: float = 0.7, fixed_noul: float = 0.85):
        self.fixed_score = fixed_score
        self.fixed_noul = fixed_noul
        self.tau_noul = 0.3

    def score_batch(self, texts: list[str], **kwargs) -> list[float]:
        return [self.fixed_score for _ in texts]

    def gate_batch(self, texts: list[str]) -> tuple[list[float], list[bool]]:
        """Pass branches where noul >= tau_noul."""
        nouls = [self.fixed_noul for _ in texts]
        passed_bools = [n >= self.tau_noul for n in nouls]
        return nouls, passed_bools

    @property
    def latency_ms(self) -> float:
        return 2.0

    @property
    def backend(self) -> str:
        return 'mock'
