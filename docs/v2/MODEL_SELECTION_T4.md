# Choosing the Qwen model for v2 on a Tesla T4

Status 2026-09-21: **partly measured.** Every number below is tagged MEASURED or NOT YET
MEASURED; nothing in the second group should be treated as a result.

## The constraint that decides it

v2 is not just inference. Its core loop (Phase C) is a **nightly QLoRA update of the model that
also serves during the day**. That gives two different questions:

1. What is the best model that *fits for inference* on the T4? (a 27B at ~3 bit)
2. What is the best model that *can also be fine-tuned* on the T4? (a 7-9B in 4-bit)

A quantised GGUF (AD-IQ3_S, IQ3_XXS ...) is **inference-only**: LoRA cannot be trained on it, and
bitsandbytes 4-bit of a 27B needs roughly 14-15 GiB for weights alone against a T4 that reports
**15,360 MiB (15.0 GiB) total**, not 16 GB. So a 27B cannot be the model that v2 trains here.

## Hardware facts (MEASURED)

- Tesla T4, compute capability 7.5, 15,360 MiB. No bfloat16 (train in fp16), no FlashAttention-2.
- Ollama 0.34.1 loads the `qwen3_5` architecture (Gated DeltaNet + gated attention hybrid).
- Qwen3.8 exists only as **27B dense** (plus a 2.4T MoE and a "Flash-Next" variant). There is
  **no small Qwen3.8**. Its architecture tag is `qwen3_5`, the same as the Qwen3.5 series, so
  **Qwen3.5-9B is the small sibling of the same family**.

## Candidates

| Model | Role | Fits the T4? | Speed | Trainable on the T4? |
|---|---|---|---|---|
| qwen3:8b Q4_K_M (baseline) | v1 | yes, 5.6 GB, MEASURED | ~36 tok/s MEASURED | yes |
| **Qwen3.5-9B Q4_K_M** (`unsloth/Qwen3.5-9B-GGUF`) | v2 day-to-day model and QLoRA base | **yes, MEASURED** | **32.5 tok/s, MEASURED** | yes (bnb 4-bit, est. 6-8 GB, NOT YET MEASURED) |
| Qwen3.8-27B AD-IQ3_S (13.84 GB) | strongest inference, verifier or teacher | claimed ~8K ctx; **NOT YET MEASURED** on 15.0 GiB | NOT YET MEASURED | **no** |
| Qwen3.8-27B AD-IQ3_S-IQ3_XXS (12.98 GB) | same, more headroom | NOT YET MEASURED | NOT YET MEASURED | **no** |

### Qwen3.5-9B Q4_K_M, MEASURED (q8 KV cache, flash attention, 300 generated tokens)

| num_ctx | VRAM used | On GPU | Generation |
|---|---|---|---|
| 4,096 | 6,327 MiB | 100 % | 32.7 tok/s |
| 16,384 | 6,577 MiB | 100 % | 32.6 tok/s |
| 32,768 | 6,929 MiB | 100 % | 32.0 tok/s |

Context is nearly free: 8x more context cost about 600 MiB and 2 % speed, because only 1 in 4
layers uses full attention (the rest are Gated DeltaNet). That is the opposite of the 27B, whose
article quotes ~256 KB of KV per token. First load took 243 s (cold disk read); later loads 13-14 s.

## Recommendation (provisional, pending the unmeasured items)

1. **Train and serve Qwen3.5-9B** with QLoRA rank 16 (fp16 compute, 4-bit NF4, seq 2048, batch 1,
   gradient accumulation 16). It is the only candidate that is both current-generation and
   trainable within 15 GiB, and it leaves room for the embedding model.
2. **Treat the 27B as an optional frozen "big brain"** for inference-only jobs: hard-task
   verification, reference solutions for the Phase 3 ladder, judging. It cannot share the GPU with
   the 9B, so it would be time-shared (day: one or the other; night: training needs the whole card).
3. **Keep the 27B decision open until it is measured.** The article's "about 8K context" assumes
   16 GB and fp16 KV. Here: 12.9 GiB of weights + ~1 GiB (q8 KV at 8K) + compute buffers + CUDA
   context is close to 15.0 GiB. If AD-IQ3_S does not load 100 % on GPU at 8K, use
   AD-IQ3_S-IQ3_XXS; a partial CPU offload of a dense 27B is not worth it.

## To finish (resume here)

Isolated Ollama on port 11435 (own model store `~/.ollama`, started with
`OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_MAX_LOADED_MODELS=1`); the main service
on 11434 is untouched. Restart it if the session that launched it is gone.

```
# 1. 27B: does it fit and how fast? (the pull `hf.co/AtomicChat/Qwen3.8-27B-GGUF:AD-IQ3_S` may need re-running)
python v2_runners/t4_fit_probe.py --model hf.co/AtomicChat/Qwen3.8-27B-GGUF:AD-IQ3_S --ctx 4096 8192 16384
# 2. Quality, same 20-task gate as v1 (baseline qwen3:8b: 16/20 = 80 %)
ANSE_OLLAMA_URL=http://127.0.0.1:11435 python run_llm_phase1.py --model hf.co/unsloth/Qwen3.5-9B-GGUF:Q4_K_M --out .scratchpad/llm_phase1_q35_9b
ANSE_OLLAMA_URL=http://127.0.0.1:11435 python run_llm_phase1.py --model hf.co/AtomicChat/Qwen3.8-27B-GGUF:AD-IQ3_S --out .scratchpad/llm_phase1_q38_27b
# 3. Phase 3 ladder with each (does a stronger model find the pooling insight?)
ANSE_OLLAMA_URL=http://127.0.0.1:11435 python run_llm_phase3.py --model <model> --trials 4 --max-turns 5
```

Decision rule: pick the 27B for inference roles only if it beats the 9B by >= 5 points on Phase 1
**and** loads fully on the GPU at >= 8K context with >= 8 tok/s; otherwise the 9B does both jobs.
Also run a training smoke test (card A-3 / C-6 style): one QLoRA step on Qwen3.5-9B must fit in
15 GiB, otherwise fall back to Qwen3.5-4B.
