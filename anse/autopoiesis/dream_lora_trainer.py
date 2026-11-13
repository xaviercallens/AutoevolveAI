import os
import sys
import time
import logging
from pathlib import Path
import numpy as np
import torch

# Ensure we can import from checkpoints/laya
laya_dir = Path(__file__).resolve().parent.parent.parent / "checkpoints" / "laya"
sys.path.insert(0, str(laya_dir))

logger = logging.getLogger(__name__)


class LayaDreamLoRATrainer:
    """
    Implements nightly LoRA + RLCD (Reinforcement Learning for Calibrated Decisions) 
    fine-tuning on the Laya System 1 model using Hippocampus traces.
    """
    def __init__(self, model_dir: Path | str | None = None, device: str | None = None):
        if device is None:
            try:
                from anse.infrastructure.agent_environment import resolve_capability_profile
                prof = resolve_capability_profile()
                device = prof.device
            except Exception:
                device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model_dir = Path(model_dir) if model_dir else laya_dir
        self.model = None
        self.cfg = None

    def _load_model_for_training(self):
        try:
            from rl_common import load_cfg, DecisionModel, build_sequence, collate_items, proper_reward, QTYPES
            from transformers import AutoConfig, AutoModel, AutoTokenizer
            
            logger.info("Loading Laya model architecture for LoRA Dream Phase...")
            cfg_path = self.model_dir / "rl_agent_config.json"
            if not cfg_path.exists():
                raise FileNotFoundError(f"Config not found at {cfg_path}")
                
            self.cfg = load_cfg(str(cfg_path))
            logger.info(f"Loaded config from {cfg_path}")
            
            tok_dir = self.model_dir / "tokenizer"
            if tok_dir.exists():
                self.tok = AutoTokenizer.from_pretrained(str(tok_dir))
            else:
                self.tok = AutoTokenizer.from_pretrained(self.cfg.get("encoder", "answerdotai/ModernBERT-base"))
            if self.tok.pad_token_id is None:
                self.tok.pad_token = self.tok.eos_token or "<pad>"
            
            encoder_dir = self.model_dir / "encoder"
            if (encoder_dir / "model.safetensors").exists():
                encoder = AutoModel.from_pretrained(encoder_dir, attn_implementation="sdpa")
                logger.info(f"Loaded encoder directly from {encoder_dir}")
            elif encoder_dir.exists():
                ecfg = AutoConfig.from_pretrained(encoder_dir)
                encoder = AutoModel.from_config(ecfg, attn_implementation="sdpa")
            else:
                encoder = AutoModel.from_pretrained(self.cfg["encoder"], attn_implementation="sdpa")
            
            self.model = DecisionModel(encoder, head_layers=self.cfg["head_layers"], n_act=len(self.cfg["act_costs"]) + 1)
            
            weights_path = self.model_dir / "model.safetensors"
            if weights_path.exists():
                from safetensors.torch import load_file
                self.model.load_state_dict(load_file(weights_path), strict=True)
                logger.info("Successfully loaded Laya base weights (842MB).")
            else:
                raise FileNotFoundError(f"Weights not found at {weights_path}")

        except Exception as e:
            logger.error(f"Failed to load Laya model: {e}")
            raise e


    def apply_lora(self, r=4, alpha=8, dropout=0.05, target_modules: list[str] | str | None = None):
        """Wraps the bidirectional encoder in a PEFT LoRA adapter and freezes non-saved head weights."""
        if self.model is None:
            self._load_model_for_training()

        if target_modules is None:
            # ModernBERT layers: attn.Wo, attn.Wqkv, mlp.Wi, mlp.Wo
            target_modules = ["attn.Wqkv", "attn.Wo"]

        # Freeze DecisionModel head parameters so 100% of gradient optimization is captured
        # in the saved encoder LoRA adapters (`checkpoints/laya/lora_adapters`).
        for name, param in self.model.named_parameters():
            if not name.startswith("encoder."):
                param.requires_grad = False

        try:
            from peft import LoraConfig, get_peft_model
            lora_config = LoraConfig(
                r=r,
                lora_alpha=alpha,
                target_modules=target_modules,
                lora_dropout=dropout,
                bias="none",
                task_type="FEATURE_EXTRACTION"
            )
            self.model.encoder = get_peft_model(self.model.encoder, lora_config)
            logger.info(f"LoRA successfully injected into Laya's encoder using targets={target_modules}.")
        except ImportError:
            logger.warning("PEFT not installed. Freezing encoder to simulate LoRA...")
            for param in self.model.encoder.parameters():
                param.requires_grad = False
        
        self.model.to(self.device)

    @staticmethod
    def _select_balanced_traces(traces: list[dict], max_traces: int | None) -> list[dict]:
        """Select a domain- and class-balanced subset of traces (prioritizing contrast, unsound, and anchor memories)."""
        if not max_traces or len(traces) <= max_traces:
            return list(traces)

        priority: list[dict] = []
        sound_pool: list[dict] = []
        unsound_pool: list[dict] = []
        other_pool: list[dict] = []
        seen_ids: set[str] = set()

        for t in reversed(traces):
            tid = str(t.get("trace_id", ""))
            energy = float(t.get("energy", 0.0))
            if tid.startswith("chroma_contrast_"):
                if tid not in seen_ids:
                    priority.append(t)
                    seen_ids.add(tid)
            elif energy >= 10.0:
                unsound_pool.append(t)
            elif energy <= 1.0 or t.get("is_anchor", False):
                sound_pool.append(t)
            else:
                other_pool.append(t)

        selected: list[dict] = list(priority[:max_traces])
        remaining = max_traces - len(selected)
        half = max(1, remaining // 2)
        for t in unsound_pool[:half]:
            if len(selected) < max_traces:
                selected.append(t)
        for t in sound_pool[: remaining - len(unsound_pool[:half])]:
            if len(selected) < max_traces:
                selected.append(t)
        for t in other_pool:
            if len(selected) >= max_traces:
                break
            selected.append(t)
        return selected

    def train_on_traces(
        self,
        traces: list[dict],
        epochs: int = 2,
        batch_size: int = 2,
        seq_len: int = 128,
        max_traces: int | None = None,
        save_adapter: bool = True,
        lr: float = 5e-4,
    ):
        """
        Executes the RLCD (RCFL) strictly proper scoring rule on historical traces.
        High energy (>= 10.0) -> Unsound/Fail
        Low/Negative energy (<= 1.0 or anchor) -> Sound/Success
        Intermediate energy (1.0 < E < 10.0) -> Needs Investigation
        """
        if self.model is None:
            self._load_model_for_training()
            self.apply_lora()

        if max_traces is None and self.device.type == "cpu":
            max_traces = 18

        effective_traces = self._select_balanced_traces(traces, max_traces)
            
        self.model.train()
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.encoder.parameters()),
            lr=lr,
            weight_decay=1e-4,
        )
        
        logger.info(
            f"Starting LoRA + RLCD Dream Phase on {len(effective_traces)} balanced traces "
            f"(device={self.device.type}, epochs={epochs}, seq_len={seq_len})..."
        )
        t0 = time.time()
        
        total_loss = 0.0
        num_batches = 0
        from rl_common import build_sequence, collate_items, proper_reward, QTYPES

        head_max_len = 48 if seq_len >= 96 else min(48, max(16, seq_len // 2))

        for epoch in range(epochs):
            for i in range(0, len(effective_traces), batch_size):
                batch = effective_traces[i:i+batch_size]
                
                items = []
                for t in batch:
                    domain = t.get("domain", "general")
                    prompt = t.get("prompt", "")
                    thought = t.get("thought", "") or t.get("thought_summary", "")
                    energy = float(t.get("energy", 0.0))
                    
                    q = {
                        "t": "choice",
                        "ins": f"Domain {domain}: Evaluate soundness of candidate logic for {prompt[:60]}",
                        "crit": {
                            "sound": "Non-positive energy, physically sound",
                            "unsound": "Execution error or energy threshold exceeded",
                            "needs_investigation": "Inconclusive, requires sandbox verification",
                        }
                    }
                    state = {"domain": domain, "thought": thought}
                    
                    if energy >= 10.0:
                        target = [0.0, 1.0, 0.0]  # Unsound
                    elif energy <= 1.0 or bool(t.get("is_anchor", False)):
                        target = [1.0, 0.0, 0.0]  # Sound
                    else:
                        target = [0.0, 0.0, 1.0]  # Needs investigation
                        
                    ids, markers = build_sequence(
                        self.tok, state, q, max_len=seq_len, head_max_len=head_max_len
                    )
                    if len(markers) == 3:
                        items.append({
                            "ids": ids,
                            "markers": markers,
                            "qtype": QTYPES["choice"],
                            "target": target,
                            "label": int(np.argmax(target)),
                            "episode": 0,
                            "ep_step": 0,
                            "ep_len": 1,
                        })
                
                if not items:
                    continue
                    
                b = collate_items([items], self.tok.pad_token_id or 0)
                if b is None:
                    continue
                    
                input_ids = b["input_ids"].to(self.device)
                attention_mask = b["attention_mask"].to(self.device)
                marker_pos = b["marker_pos"].to(self.device)
                marker_mask = b["marker_mask"].to(self.device)
                qtype = b["qtype"].to(self.device)
                target_tensor = b["target"].to(self.device)
                
                optimizer.zero_grad()
                logits, _ = self.model(input_ids, attention_mask, marker_pos, marker_mask, qtype)
                q_probs = torch.softmax(logits, dim=-1)
                
                # RLCD Strictly Proper Scoring Rule Reward
                r = proper_reward(q_probs, target_tensor, qtype, marker_mask)
                loss = -r.mean()
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.encoder.parameters(), 1.0)
                optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1

                
        duration = time.time() - t0
        avg_loss = total_loss / max(num_batches, 1)
        logger.info(f"Dream Phase complete in {duration:.2f}s. Avg Loss: {avg_loss:.4f}")
        
        adapter_path = self.model_dir / "lora_adapters"
        if save_adapter and hasattr(self.model.encoder, "save_pretrained"):
            adapter_path.mkdir(parents=True, exist_ok=True)
            self.model.encoder.save_pretrained(str(adapter_path))
            logger.info(f"LoRA adapters successfully saved to {adapter_path}")
        
        return {
            "avg_loss": round(avg_loss, 4),
            "duration_sec": round(duration, 2),
            "traces_processed": len(effective_traces),
            "device": str(self.device),
            "adapter_saved": save_adapter,
        }
