"""
anse/laya/ — Laya Coding Companion Module
==========================================
Non-autoregressive System 1 dispatcher for ANSE, built on
ModernBERT-base + LoRA rank-8, with noul/choice/score multi-task heads.
"""
from anse.laya.model import LayaCodingCompanion, LayaDecision
from anse.laya.inference import LayaInference
from anse.laya.integration import LayaANSEDispatcher

__all__ = [
    "LayaCodingCompanion",
    "LayaDecision",
    "LayaInference",
    "LayaANSEDispatcher",
]
