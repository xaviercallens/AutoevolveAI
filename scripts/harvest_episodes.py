#!/usr/bin/env python3
"""Harvest genuinely verified training episodes, so the nightly loop has real data.

WHY THIS EXISTS

The nightly trainer refuses to run, and it is right to. Measured today:

    data/interactions.jsonl : 9 rows, 1 distinct task, hidden_state dim 16,
                              0 rows with metadata.tests_total > 0
    data/episodes/          : empty

`anse/jepa/dataset.py` requires `metadata["tests_total"] > 0` (else the row is
counted into `skipped["unverified"]` and silently dropped), a non-empty
`hidden_state` of consistent width, and finite energy. It also falls back to an
item-level split when fewer than 2 distinct tasks are present (`:386`), which
recreates the leakage that produced the bogus Phase-2 r=0.40 headline.

So "retrain the models" is not a command that can be issued -- it needs data that
satisfies that contract. This script produces it, honestly:

  1. A bank of small Python tasks, each with a HIDDEN reference test. The test is
     never shown to the model; only the statement is.
  2. The LOCAL model proposes a solution (free, on the T4).
  3. `anse/symbolic/sandbox.py` EXECUTES the candidate against the hidden test.
     `tests_passed`/`tests_total` come from that execution, not from an opinion.
  4. Energy is computed from the measured outcome (failures, runtime, memory).
  5. `hidden_state` is a real 1024-d embedding of the (statement, code) pair.

Every episode therefore carries a verifier-issued verdict. Failed attempts are kept
and labelled -- a wrong answer that a test caught is a legitimate training signal,
and discarding failures is how a corpus becomes biased.

Usage:
    .venv/bin/python scripts/harvest_episodes.py --tasks 10 --samples 2
    .venv/bin/python scripts/harvest_episodes.py --dry-run     # bank + verifier only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "episodes"
sys.path.insert(0, "/mnt/disks/disk-socrateai-local-1/gpu_lease")

from gpu_lease import gpu_lease  # noqa: E402

OLLAMA = "http://localhost:11434"
LEASE_HOLDER = "autoevolve-harvest-episodes"
CODER_MODEL = "qwen2.5-coder:7b-instruct"


@dataclass(frozen=True)
class Task:
    """A problem whose reference test is hidden from the solver."""

    task_id: str
    statement: str
    entry_point: str
    hidden_test: str
    # Known-correct solution. Dry-run must score it full marks, which proves the hidden test is
    # satisfiable and not a wrong test that the model is then blamed for failing.
    reference: str = ""


# Deliberately small and unambiguous: the point is to exercise the data contract
# and the nightly path, not to benchmark capability. Each test asserts behaviour
# the statement describes, and none of them appears in the prompt.
TASKS: tuple[Task, ...] = (
    Task("py-sum-even", "Write `def sum_even(xs: list[int]) -> int` returning the sum of even values.",
         "sum_even",
         "assert sum_even([1,2,3,4])==6\nassert sum_even([])==0\nassert sum_even([-2,3])==-2"),
    Task("py-reverse-words", "Write `def reverse_words(s: str) -> str` reversing word order, single-spaced.",
         "reverse_words",
         "assert reverse_words('a b c')=='c b a'\nassert reverse_words('hi')=='hi'"),
    Task("py-is-palindrome", "Write `def is_palindrome(s: str) -> bool`, case-insensitive, ignoring non-alphanumerics.",
         "is_palindrome",
         "assert is_palindrome('A man, a plan, a canal: Panama')\nassert not is_palindrome('abc')"),
    Task("py-gcd", "Write `def gcd(a: int, b: int) -> int` returning the greatest common divisor.",
         "gcd",
         "assert gcd(12,18)==6\nassert gcd(7,13)==1\nassert gcd(0,5)==5"),
    Task("py-flatten", "Write `def flatten(xs: list) -> list` flattening one level of nesting.",
         "flatten",
         "assert flatten([[1,2],[3]])==[1,2,3]\nassert flatten([])==[]"),
    Task("py-run-length", "Write `def encode(s: str) -> str` run-length encoding, e.g. 'aab' -> 'a2b1'.",
         "encode",
         "assert encode('aab')=='a2b1'\nassert encode('')==''"),
    Task("py-second-largest", "Write `def second_largest(xs: list[int]) -> int | None` returning the second largest distinct value, or None.",
         "second_largest",
         "assert second_largest([1,3,2])==2\nassert second_largest([5,5])is None"),
    Task("py-binary-search", "Write `def bsearch(xs: list[int], t: int) -> int` returning the index of t in a sorted list, or -1.",
         "bsearch",
         "assert bsearch([1,3,5,7],5)==2\nassert bsearch([1,3],2)==-1"),
    Task("py-chunk", "Write `def chunk(xs: list, n: int) -> list[list]` splitting into consecutive chunks of size n.",
         "chunk",
         "assert chunk([1,2,3,4,5],2)==[[1,2],[3,4],[5]]\nassert chunk([],3)==[]"),
    Task("py-word-count", "Write `def word_count(s: str) -> dict[str,int]` counting whitespace-separated words.",
         "word_count",
         "assert word_count('a b a')=={'a':2,'b':1}\nassert word_count('')=={}"),
    Task("py-transpose", "Write `def transpose(m: list[list]) -> list[list]` transposing a rectangular matrix.",
         "transpose",
         "assert transpose([[1,2],[3,4]])==[[1,3],[2,4]]\nassert transpose([])==[]"),
    Task("py-digit-sum", "Write `def digit_sum(n: int) -> int` summing the decimal digits of abs(n).",
         "digit_sum",
         "assert digit_sum(123)==6\nassert digit_sum(-45)==9\nassert digit_sum(0)==0"),
)


# Harder bank. Each statement is precise about the edge case a small coder model tends to miss
# (truncation direction, touching intervals, strictness, tie-breaking, cycles). Every hidden
# test is checked against its reference solution in --dry-run before any model is called.
HARD_TASKS: tuple[Task, ...] = (
    Task("hard-rpn-trunc", "Write `def eval_rpn(tokens: list[str]) -> int` evaluating Reverse Polish notation with + - * /. Integer division truncates toward zero.",
         "eval_rpn",
         "assert eval_rpn(['2','1','+','3','*'])==9\nassert eval_rpn(['4','13','5','/','+'])==6\nassert eval_rpn(['-7','2','/'])==-3\nassert eval_rpn(['-7'])==-7",
         "def eval_rpn(tokens):\n    st = []\n    for t in tokens:\n        if len(t) == 1 and t in '+-*/':\n            b = st.pop(); a = st.pop()\n            if t == '+': st.append(a + b)\n            elif t == '-': st.append(a - b)\n            elif t == '*': st.append(a * b)\n            else: st.append(int(a / b))\n        else:\n            st.append(int(t))\n    return st[-1]\n"),
    Task("hard-merge-touching", "Write `def merge(intervals: list[list[int]]) -> list[list[int]]` merging overlapping AND touching closed intervals, returning them sorted. Input may be unsorted; empty input gives [].",
         "merge",
         "assert merge([[1,4],[4,5]])==[[1,5]]\nassert merge([[1,3],[2,6],[8,10],[15,18]])==[[1,6],[8,10],[15,18]]\nassert merge([])==[]\nassert merge([[5,6],[1,2]])==[[1,2],[5,6]]",
         "def merge(intervals):\n    out = []\n    for s, e in sorted(intervals):\n        if out and s <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], e)\n        else:\n            out.append([s, e])\n    return out\n"),
    Task("hard-lis-strict", "Write `def lis_length(xs: list[int]) -> int` returning the length of the longest STRICTLY increasing subsequence; 0 for empty input.",
         "lis_length",
         "assert lis_length([10,9,2,5,3,7,101,18])==4\nassert lis_length([2,2,2])==1\nassert lis_length([])==0\nassert lis_length([1,3,2,4])==3",
         "def lis_length(xs):\n    best = [1] * len(xs)\n    for i in range(len(xs)):\n        for j in range(i):\n            if xs[j] < xs[i]:\n                best[i] = max(best[i], best[j] + 1)\n    return max(best, default=0)\n"),
    Task("hard-min-window", "Write `def min_window(s: str, t: str) -> str` returning the shortest substring of s containing every character of t with multiplicity; return '' if none. On ties return the leftmost.",
         "min_window",
         "assert min_window('ADOBECODEBANC','ABC')=='BANC'\nassert min_window('a','aa')==''\nassert min_window('aa','aa')=='aa'\nassert min_window('ab','b')=='b'",
         "def min_window(s, t):\n    from collections import Counter\n    need = Counter(t); missing = len(t)\n    best = (0, 0); lo = 0\n    best_len = float('inf')\n    for hi, ch in enumerate(s, 1):\n        if need[ch] > 0: missing -= 1\n        need[ch] -= 1\n        while missing == 0:\n            if hi - lo < best_len:\n                best_len = hi - lo; best = (lo, hi)\n            need[s[lo]] += 1\n            if need[s[lo]] > 0: missing += 1\n            lo += 1\n    return s[best[0]:best[1]] if best_len != float('inf') else ''\n"),
    Task("hard-topo-lex", "Write `def topo_order(n: int, edges: list[tuple[int,int]]) -> list[int] | None` returning the lexicographically smallest topological order of nodes 0..n-1 for directed edges (a,b meaning a before b), or None if there is a cycle.",
         "topo_order",
         "assert topo_order(3,[(0,1),(1,2)])==[0,1,2]\nassert topo_order(2,[(0,1),(1,0)]) is None\nassert topo_order(3,[(2,0),(1,0)])==[1,2,0]\nassert topo_order(0,[])==[]",
         "def topo_order(n, edges):\n    import heapq\n    indeg = [0] * n; adj = [[] for _ in range(n)]\n    for a, b in edges:\n        adj[a].append(b); indeg[b] += 1\n    heap = [i for i in range(n) if indeg[i] == 0]\n    heapq.heapify(heap); out = []\n    while heap:\n        u = heapq.heappop(heap); out.append(u)\n        for v in adj[u]:\n            indeg[v] -= 1\n            if indeg[v] == 0: heapq.heappush(heap, v)\n    return out if len(out) == n else None\n"),
    Task("hard-caesar-any-shift", "Write `def caesar(s: str, k: int) -> str` shifting ASCII letters by k (any integer, including negative and k > 26), preserving case; leave all other characters unchanged.",
         "caesar",
         "assert caesar('Hello, World!',3)=='Khoor, Zruog!'\nassert caesar('abc',-1)=='zab'\nassert caesar('xyz',29)=='abc'\nassert caesar('A1 b',0)=='A1 b'",
         "def caesar(s, k):\n    out = []\n    for ch in s:\n        if 'a' <= ch <= 'z':\n            out.append(chr((ord(ch) - 97 + k) % 26 + 97))\n        elif 'A' <= ch <= 'Z':\n            out.append(chr((ord(ch) - 65 + k) % 26 + 65))\n        else:\n            out.append(ch)\n    return ''.join(out)\n"),
    Task("hard-balanced-brackets", "Write `def balanced(s: str) -> bool` returning True iff every ()[]{} bracket pair is properly nested; all other characters are ignored.",
         "balanced",
         "assert balanced('a(b[c]{d})e')\nassert not balanced('(]')\nassert balanced('')\nassert not balanced('(a')\nassert not balanced(')(')",
         "def balanced(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    st = []\n    for ch in s:\n        if ch in '([{': st.append(ch)\n        elif ch in pairs:\n            if not st or st.pop() != pairs[ch]: return False\n    return not st\n"),
    Task("hard-kth-duplicates", "Write `def kth_largest(xs: list[int], k: int) -> int` returning the k-th largest element counting duplicates (k=1 is the maximum). Raise ValueError if k is outside 1..len(xs).",
         "kth_largest",
         "assert kth_largest([3,2,3,1,2,4,5,5,6],4)==4\nassert kth_largest([5,5],2)==5\nassert exec(\"try:\\n    kth_largest([1],2)\\nexcept ValueError:\\n    pass\\nelse:\\n    raise AssertionError\") is None",
         "def kth_largest(xs, k):\n    if k < 1 or k > len(xs):\n        raise ValueError('k out of range')\n    return sorted(xs, reverse=True)[k - 1]\n"),
    Task("hard-dijkstra-directed", "Write `def shortest(n: int, edges: list[tuple[int,int,int]], src: int, dst: int) -> int` returning the minimum total weight of a directed path from src to dst (edges (u,v,w), w >= 0), or -1 if unreachable. Return 0 when src == dst.",
         "shortest",
         "assert shortest(4,[(0,1,1),(1,3,2),(0,2,5),(2,3,1)],0,3)==3\nassert shortest(3,[(0,1,1)],0,2)==-1\nassert shortest(2,[],1,1)==0\nassert shortest(2,[(1,0,4)],0,1)==-1",
         "def shortest(n, edges, src, dst):\n    import heapq\n    adj = [[] for _ in range(n)]\n    for u, v, w in edges: adj[u].append((v, w))\n    dist = [None] * n; dist[src] = 0; pq = [(0, src)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if d != dist[u]: continue\n        for v, w in adj[u]:\n            nd = d + w\n            if dist[v] is None or nd < dist[v]:\n                dist[v] = nd; heapq.heappush(pq, (nd, v))\n    return -1 if dist[dst] is None else dist[dst]\n"),
    Task("hard-deep-merge", "Write `def deep_merge(a: dict, b: dict) -> dict` returning a new dict where nested dicts merge recursively, values from b override a for non-dict values, and neither input is mutated.",
         "deep_merge",
         "assert deep_merge({'x':{'y':1}},{'x':{'z':3}})=={'x':{'y':1,'z':3}}\nassert deep_merge({'a':1},{'a':{'b':2}})=={'a':{'b':2}}\nassert (lambda a,b: (lambda r: r=={'x':{'y':1,'z':3}} and a=={'x':{'y':1}} and b=={'x':{'z':3}} and r is not a)(deep_merge(a,b)))({'x':{'y':1}},{'x':{'z':3}})",
         "def deep_merge(a, b):\n    import copy\n    out = copy.deepcopy(a)\n    for k, v in b.items():\n        if isinstance(v, dict) and isinstance(out.get(k), dict):\n            out[k] = deep_merge(out[k], v)\n        else:\n            out[k] = copy.deepcopy(v)\n    return out\n"),
    Task("hard-window-max", "Write `def window_max(xs: list[int], k: int) -> list[int]` returning the maximum of each window of length k, in order; return [] when k < 1 or k > len(xs).",
         "window_max",
         "assert window_max([1,3,-1,-3,5,3,6,7],3)==[3,3,5,5,6,7]\nassert window_max([1],2)==[]\nassert window_max([4,2],0)==[]\nassert window_max([2,2],2)==[2]",
         "def window_max(xs, k):\n    if k < 1 or k > len(xs): return []\n    return [max(xs[i:i + k]) for i in range(len(xs) - k + 1)]\n"),
    Task("hard-islands-4conn", "Write `def count_islands(grid: list[str]) -> int` counting 4-connected components of '1' cells in a grid of '0'/'1' strings; diagonal neighbours do NOT connect; an empty grid gives 0.",
         "count_islands",
         "assert count_islands(['11000','11000','00100','00011'])==3\nassert count_islands(['10','01'])==2\nassert count_islands([])==0\nassert count_islands(['1'])==1",
         "def count_islands(grid):\n    from collections import deque\n    seen = set(); count = 0\n    for r in range(len(grid)):\n        for c in range(len(grid[r])):\n            if grid[r][c] == '1' and (r, c) not in seen:\n                count += 1; q = deque([(r, c)]); seen.add((r, c))\n                while q:\n                    y, x = q.popleft()\n                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):\n                        ny, nx = y + dy, x + dx\n                        if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]) and grid[ny][nx] == '1' and (ny, nx) not in seen:\n                            seen.add((ny, nx)); q.append((ny, nx))\n    return count\n"),
)


def extract_code(raw: str) -> str:
    """Pull the Python block out of a model reply."""
    fenced = re.findall(r"```(?:python)?\s*\n(.*?)```", raw, flags=re.DOTALL)
    if fenced:
        return max(fenced, key=len).strip()
    return raw.strip()


def call_coder(statement: str, temperature: float) -> str:
    import httpx

    prompt = (
        "Write a single self-contained Python function. Output ONLY a ```python code "
        "block, no explanation, no tests, no example usage.\n\n" + statement
    )
    r = httpx.post(
        f"{OLLAMA}/api/generate",
        json={
            "model": CODER_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 400},
        },
        timeout=900,
    )
    r.raise_for_status()
    return r.json().get("response", "")


def verify(code: str, task: Task) -> dict[str, Any]:
    """Execute the candidate against the hidden test. This is the only verdict.

    Each assertion in the hidden test is counted individually, so a partially
    correct solution yields a partial score rather than a binary one.
    """
    from anse.symbolic.sandbox import SandboxExecutor

    assertions = [ln for ln in task.hidden_test.splitlines() if ln.strip()]
    tests_total = len(assertions)

    # Run assertions one at a time so tests_passed is a real count.
    passed = 0
    last_stderr = ""
    total_ms = 0.0
    peak_ram = 0.0
    executor = SandboxExecutor()
    for assertion in assertions:
        program = f"{code}\n\n{assertion}\nprint('OK')\n"
        # force_tier=1 keeps this in the subprocess sandbox: Docker (tier 2) may be
        # absent, and escalating on an AST scan would turn a missing daemon into a
        # spurious test failure. Timeout comes from SandboxConfig, not this call.
        result = executor.execute(program, trusted=False, force_tier=1)
        total_ms += result.duration_ms
        peak_ram = max(peak_ram, result.peak_ram_mb)
        if result.returncode == 0 and "OK" in result.stdout:
            passed += 1
        else:
            last_stderr = (result.stderr or "")[-400:]

    return {
        "tests_total": tests_total,
        "tests_passed": passed,
        "returncode": 0 if passed == tests_total else 1,
        "duration_ms": total_ms,
        "peak_ram_mb": peak_ram,
        "stderr": last_stderr,
    }


def energy_of(v: dict[str, Any]) -> float:
    """Energy from measured outcome: failures dominate, runtime is a tiebreak.

    Zero only when every hidden assertion passed. Finite always, because
    `anse/jepa/dataset.py` drops non-finite energies.
    """
    failed = v["tests_total"] - v["tests_passed"]
    return float(failed * 100.0 + min(v["duration_ms"], 10_000.0) / 1000.0)


def embed(text: str) -> list[float]:
    from anse.memory.ollama_embeddings import OllamaEmbeddingFunction

    return OllamaEmbeddingFunction()([text[:6000]])[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-set", choices=("easy", "hard"), default="easy",
                    help="easy: the original 12 tasks (the model passes all of them); hard: edge-case bank")
    ap.add_argument("--tasks", type=int, default=None)
    ap.add_argument("--samples", type=int, default=2, help="attempts per task")
    ap.add_argument("--dry-run", action="store_true",
                    help="verify the bank against reference solutions; no model calls")
    ap.add_argument("--out", type=Path, default=OUT / "harvest.jsonl")
    args = ap.parse_args(argv)

    bank = HARD_TASKS if args.task_set == "hard" else TASKS
    selected = bank[: args.tasks] if args.tasks is not None else bank
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run and args.task_set == "hard":
        # Every hard task's reference must pass its hidden test; a failing reference means the
        # test itself is wrong, and such a task must not be used to score the model.
        failures = []
        for task in HARD_TASKS:
            result = verify(task.reference, task)
            if result["tests_passed"] != result["tests_total"]:
                failures.append(f"{task.task_id}: {result['tests_passed']}/{result['tests_total']}")
        print(f"hard bank: {len(HARD_TASKS)} tasks, reference failures: {failures or 'none'}")
        return 0 if not failures else 1

    if args.dry_run:
        # Sanity: a KNOWN-GOOD solution must score full marks, and an empty one
        # must score zero. Without both, the verifier proves nothing.
        good = "def sum_even(xs):\n    return sum(x for x in xs if x % 2 == 0)\n"
        t = TASKS[0]
        ok = verify(good, t)
        bad = verify("def sum_even(xs):\n    return 999\n", t)
        print(f"verifier positive control: {ok['tests_passed']}/{ok['tests_total']}")
        print(f"verifier negative control: {bad['tests_passed']}/{bad['tests_total']}")
        good_ok = ok["tests_passed"] == ok["tests_total"]
        bad_ok = bad["tests_passed"] < bad["tests_total"]
        print(f"verifier is discriminating: {good_ok and bad_ok}")
        return 0 if (good_ok and bad_ok) else 1

    episodes: list[dict[str, Any]] = []
    stats = {"attempted": 0, "fully_passed": 0, "partial": 0, "failed": 0}

    with gpu_lease(LEASE_HOLDER, "harvest episodes: coder samples + embeddings", ttl_s=3600, timeout_s=3600):
        for task in selected:
            for sample in range(args.samples):
                temperature = 0.2 if sample == 0 else 0.8
                stats["attempted"] += 1
                t0 = time.time()
                try:
                    raw = call_coder(task.statement, temperature)
                except Exception as exc:
                    print(f"  {task.task_id} s{sample}: model call failed: {exc}")
                    continue
                code = extract_code(raw)
                v = verify(code, task)
                energy = energy_of(v)

                if v["tests_passed"] == v["tests_total"]:
                    stats["fully_passed"] += 1
                elif v["tests_passed"] > 0:
                    stats["partial"] += 1
                else:
                    stats["failed"] += 1

                hidden = embed(f"{task.statement}\n\n{code}")
                episodes.append(
                    {
                        "task": task.task_id,
                        "prompt": task.statement,
                        "code": code,
                        "raw_response": raw[:4000],
                        "energy": energy,
                        "energy_category": "low" if energy < 1.0 else "high",
                        "converged": v["tests_passed"] == v["tests_total"],
                        "iteration": sample,
                        "duration_ms": (time.time() - t0) * 1000.0,
                        "returncode": v["returncode"],
                        "execution_stdout": "",
                        "execution_stderr": v["stderr"],
                        "hidden_state": hidden,
                        "trace_id": str(uuid.uuid4()),
                        "timestamp": time.time(),
                        # The contract anse/jepa/dataset.py actually enforces.
                        "metadata": {
                            "tests_total": v["tests_total"],
                            "tests_passed": v["tests_passed"],
                            "difficulty_tier": "trivial" if energy == 0 else "fixable",
                            "verifier": "sandbox+hidden_assertions",
                            "temperature": temperature,
                            "peak_ram_mb": v["peak_ram_mb"],
                        },
                    }
                )
                print(f"  {task.task_id} s{sample} T={temperature}: "
                      f"{v['tests_passed']}/{v['tests_total']} energy={energy:.2f}")

    with args.out.open("w", encoding="utf-8") as fh:
        for e in episodes:
            fh.write(json.dumps(e) + "\n")

    dims = {len(e["hidden_state"]) for e in episodes}
    tasks_seen = {e["task"] for e in episodes}
    verified = sum(1 for e in episodes if e["metadata"]["tests_total"] > 0)

    print(f"\nwrote {len(episodes)} episodes -> {args.out.resolve()}")
    print(f"  distinct tasks     : {len(tasks_seen)}  (>=2 required for a task-level split)")
    print(f"  hidden_state dims  : {dims}  (must be a single value)")
    print(f"  rows with verdict  : {verified}/{len(episodes)}")
    print(f"  outcomes           : {json.dumps(stats)}")

    contract_ok = len(tasks_seen) >= 2 and len(dims) == 1 and verified == len(episodes)
    print(f"  JEPA contract met  : {contract_ok}")
    return 0 if contract_ok else 1


if __name__ == "__main__":
    sys.exit(main())
