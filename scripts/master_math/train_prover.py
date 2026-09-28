#!/usr/bin/env python3
"""QLoRA SFT of the model that actually proves (DeepSeek-Prover-V2-7B), with a
real promotion gate (TODO #1 and #2 / card P4-5).

Why this exists: `night_training_workflow.py` fine-tunes Qwen2.5-Coder, which
never proves anything in this pipeline, so no retrain could move the prover.

Data   kernel-clean *Lean* proofs from the lake corpus (verdict PASSED, Lean
       tasks only), frozen-split rows dropped with the trainer's own match.
Train  4-bit NF4, fp16 compute (sm_75 has no bf16), LoRA on attention
       projections, loss on completion tokens only.
Eval   the frozen hardness split (`results/hardness/ladder.json` ids listed in
       `frozen_split.json`), greedy, one sample, BASE and ADAPTER in this same
       HF harness (never against the Ollama Q8 numbers). Every proof goes
       through the kernel gate `build_ladder.compile_one`.
Gate   PROMOTE only if adapter true-pass > base true-pass, 0 false items
       accepted, and n_true >= 30. Otherwise BLOCKED with the reason.

GPU    one job on the shared T4: waits for Ollama to hold no model, holds the
       lease under its own holder name (holder identity is the name, so
       sharing "autoevolveai" with the nightly timer would NOT exclude it) and
       renews it inside the train and eval loops (TTL 30 min).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "hardness"))
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import release, wait_and_acquire  # noqa: E402

from scripts.hardness import run_ladder as rl  # noqa: E402

bl = rl.bl
BASE = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/models/DeepSeek-Prover-V2-7B")
LAKE = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/data/redis/redis_ltm_lora_dataset.jsonl")
ADAPTER = Path("/mnt/disks/disk-socrateai-local-1/AutoevolveAI/training_runs/candidates/deepseek_prover_lora")
OUT = REPO / "results" / "master_math_run2"
HOLDER = "autoevolveai-prover"


def renew(purpose: str) -> None:
    if not wait_and_acquire(HOLDER, purpose, ttl_s=1800, timeout_s=120):
        raise TimeoutError("lost the GPU lease")


def wait_gpu_free(min_free_mib: int, max_wait_s: int = 4 * 3600) -> int:
    """Wait until Ollama holds no model and enough VRAM is free. Never stops
    Ollama: another session may still need it."""
    import torch

    t0 = time.time()
    while time.time() - t0 < max_wait_s:
        try:
            loaded = httpx.get("http://localhost:11434/api/ps", timeout=5).json().get("models", [])
        except Exception:
            loaded = []
        free = torch.cuda.mem_get_info()[0] // 2**20
        if not loaded and free >= min_free_mib:
            return free
        print(f"waiting: ollama models={[m['name'] for m in loaded]} free={free} MiB", flush=True)
        time.sleep(60)
    raise TimeoutError("GPU never became free")


def lean_rows() -> tuple[list[dict], int]:
    frozen = [f["prop"] for f in json.loads((REPO / "results/hardness/frozen_split.json").read_text())]
    rows, excluded = [], 0
    for line in LAKE.read_text().splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(r.get("verdict", "")).upper() != "PASSED":
            continue
        text = " ".join(" ".join(str(r.get(k, "")) for k in ("prompt", "completion")).split())
        if "theorem" not in text:
            continue  # Lean rows only; the hidden-test Python episodes do not teach proving
        if any(p in text for p in frozen):
            excluded += 1
            continue
        rows.append(r)
    return rows, excluded


def as_chat(tok, prompt: str) -> str:
    return tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                   add_generation_prompt=True)


def target_for(row: dict) -> str:
    """Train on a complete fenced Lean block, the form extract_proof reads."""
    comp = str(row["completion"])
    if "theorem" in comp or "lemma" in comp:
        return "```lean4\n" + comp.strip() + "\n```"
    stmt = str(row["prompt"]).split("```lean4")[-1].split(":= by")[0]
    stmt = stmt[stmt.find("theorem"):] if "theorem" in stmt else stmt
    return "```lean4\n" + stmt.strip() + " := " + comp.strip() + "\n```"


def load(adapter: bool):
    import torch
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig, PreTrainedTokenizerFast

    # NOT AutoTokenizer: under transformers 5.x it rebuilds this checkpoint as a
    # LlamaTokenizer that silently drops spaces and non-ASCII ("a b : ℕ" ->
    # "ab:"), measured 2026-09-28; the smoke run's 0/2 was this, not the model.
    tok = PreTrainedTokenizerFast.from_pretrained(str(BASE))
    probe = "theorem x (a b : ℕ) : a + b = b + a := by\n  omega"
    if tok.decode(tok.encode(probe, add_special_tokens=False)) != probe:
        raise RuntimeError("tokenizer does not round-trip Lean text; refusing to train/evaluate")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    # Checkpoint is stored bf16; sm_75 has no bf16, so non-quantized layers
    # (norms, lm_head) load as fp16.
    net = AutoModelForCausalLM.from_pretrained(
        str(BASE), device_map={"": 0}, dtype=torch.float16,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True))
    if adapter:
        from peft import PeftModel

        net = PeftModel.from_pretrained(net, str(ADAPTER))
    net.eval()
    return tok, net


def train(rows: list[dict], steps: int, lr: float) -> dict:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    tok, net = load(adapter=False)
    net = prepare_model_for_kbit_training(net, use_gradient_checkpointing=True)
    net = get_peft_model(net, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]))
    opt = torch.optim.AdamW([p for p in net.parameters() if p.requires_grad], lr=lr)
    examples = []
    for r in rows:
        p_ids = tok(as_chat(tok, str(r["prompt"])), add_special_tokens=False)["input_ids"]
        t_ids = tok(target_for(r) + tok.eos_token, add_special_tokens=False)["input_ids"]
        ids = (p_ids + t_ids)[:1536]
        labels = ([-100] * len(p_ids) + t_ids)[:1536]
        examples.append((ids, labels))
    losses: list[float] = []
    net.train()
    for i in range(steps):
        if i % 20 == 0:
            renew("train deepseek-prover lora")
        ids, labels = examples[i % len(examples)]
        out = net(input_ids=torch.tensor([ids], device="cuda"),
                  labels=torch.tensor([labels], device="cuda"))
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_([p for p in net.parameters() if p.requires_grad], 1.0)
        opt.step()
        opt.zero_grad()
        losses.append(round(float(out.loss.item()), 4))
    ADAPTER.mkdir(parents=True, exist_ok=True)
    net.save_pretrained(str(ADAPTER))
    peak = torch.cuda.max_memory_allocated() // 2**20
    del net
    torch.cuda.empty_cache()
    return {"steps": steps, "rows": len(rows), "lr": lr, "loss_first": losses[0],
            "loss_last": losses[-1], "losses": losses, "peak_mib": peak,
            "adapter": str(ADAPTER)}


def evaluate(arm: str, items: list[dict], max_new: int) -> list[dict]:
    import torch

    tok, net = load(adapter=(arm == "adapter"))
    rows = []
    for k, it in enumerate(items):
        if k % 5 == 0:
            renew(f"eval deepseek-prover {arm}")
        enc = tok(as_chat(tok, rl.prompt_for(it)), return_tensors="pt", add_special_tokens=False).to("cuda")
        t0 = time.time()
        with torch.no_grad():
            gen = net.generate(**enc, max_new_tokens=max_new, do_sample=False,
                               pad_token_id=tok.pad_token_id)
        text = tok.decode(gen[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
        proof = rl.extract_proof(text, it)
        row = {"arm": arm, "id": it["id"], "tier": it["tier"], "truth": it["truth"],
               "gen_s": round(time.time() - t0, 1), "proof": proof}
        if proof is None:
            row.update(extracted=False, clean=False)
        else:
            v = bl.compile_one(bl.lean_file(it, proof), f"prover_{arm}_{it['id']}")
            row.update(extracted=True, clean=v["clean"], rc=v["rc"], errors=v["errors"][:400])
        rows.append(row)
        print(json.dumps({k2: row.get(k2) for k2 in ("arm", "id", "truth", "clean", "gen_s")}), flush=True)
    del net
    torch.cuda.empty_cache()
    return rows


def score(rows: list[dict]) -> dict:
    t = [r for r in rows if r["truth"] is True]
    f = [r for r in rows if r["truth"] is False]
    by_tier: dict = {}
    for r in t:
        s = by_tier.setdefault(r["tier"], [0, 0])
        s[0] += int(bool(r["clean"]))
        s[1] += 1
    return {"true_n": len(t), "true_pass": sum(bool(r["clean"]) for r in t),
            "false_n": len(f), "false_accepted": sum(bool(r["clean"]) for r in f),
            "by_tier": {k: f"{a}/{b}" for k, (a, b) in sorted(by_tier.items())}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="10 steps, 2 eval items, no gate")
    ap.add_argument("--steps", type=int, default=150)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--max-new", type=int, default=1024)
    args = ap.parse_args()
    tag = "smoke" if args.smoke else "full"
    journal: dict = {"started": datetime.now(UTC).isoformat(), "mode": tag, "base": str(BASE)}
    out_path = OUT / f"prover_training_{tag}.json"

    def save() -> None:
        OUT.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(journal, indent=1))

    rows, excluded = lean_rows()
    journal["data"] = {"lean_passed_rows": len(rows), "excluded_frozen_split": excluded,
                       "tasks": sorted({str(r.get("task")) for r in rows})}
    if not rows:
        journal["outcome"] = "BLOCKED: no kernel-verified Lean rows"
        save()
        return 1
    frozen_ids = {f["id"] for f in json.loads((REPO / "results/hardness/frozen_split.json").read_text())}
    items = [it for it in json.loads((REPO / "results/hardness/ladder.json").read_text())
             if it["id"] in frozen_ids]
    if args.smoke:
        items = [i for i in items if i["tier"] == "T0"][:2]
    free = wait_gpu_free(10_000)
    journal["free_mib_at_start"] = free
    if not wait_and_acquire(HOLDER, f"deepseek-prover {tag}", ttl_s=1800, timeout_s=4 * 3600):
        journal["outcome"] = "BLOCKED: GPU lease not acquired"
        save()
        return 2
    try:
        journal["train"] = train(rows, 10 if args.smoke else args.steps, args.lr)
        save()
        base_rows = evaluate("base", items, args.max_new)
        journal["eval_base"] = score(base_rows)
        save()
        ad_rows = evaluate("adapter", items, args.max_new)
        journal["eval_adapter"] = score(ad_rows)
        journal["eval_rows"] = base_rows + ad_rows
    finally:
        release(HOLDER)
    b, a = journal["eval_base"], journal["eval_adapter"]
    if args.smoke:
        journal["outcome"] = "SMOKE (not a gate decision)"
    elif a["false_accepted"] or b["false_accepted"]:
        journal["outcome"] = "BLOCKED: a false item was accepted -- gate failure, investigate"
    elif a["true_n"] < 30:
        journal["outcome"] = f"BLOCKED: n_true={a['true_n']} < 30"
    elif a["true_pass"] > b["true_pass"]:
        journal["outcome"] = f"PROMOTE: adapter {a['true_pass']} > base {b['true_pass']} of {a['true_n']}"
    else:
        journal["outcome"] = (f"BLOCKED: adapter {a['true_pass']} <= base {b['true_pass']} "
                              f"of {a['true_n']} on the frozen split")
    journal["finished"] = datetime.now(UTC).isoformat()
    save()
    print(journal["outcome"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
