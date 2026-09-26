export const meta = {
  name: 'anse-ladder-cascade',
  description: 'Run the local-first verified cascade over a problem level, escalating only on verified failure, and harvest episodes',
  whenToUse: 'After anse-honest-baseline establishes a baseline. Pass args {level:"L0"|"L1"|"L2", limit:N} to pick the rung.',
  phases: [
    { title: 'Preflight', detail: 'confirm frozen EVAL/TRAIN split, GPU residency, budget supervisor' },
    { title: 'Cascade', detail: 'local T4 attempt -> best-of-N -> escalate through paid tiers only on verified failure' },
    { title: 'Harvest', detail: 'write verified episodes in VerifiedLoopTrace form' },
    { title: 'Account', detail: 'escalation rate and cost per solved problem — the headline KPIs' },
  ],
}

// THE CENTRAL DESIGN
// Every problem is attempted on the LOCAL T4 first (measured 35 tok/s warm for
// qwen2.5-coder:7b-instruct after the Ollama GPU fix; marginal cost ~= electricity).
// A paid tier is reached ONLY after the local tier has verifiably failed. So:
//
//   escalation_rate = fraction of problems the local model could not solve
//   cost_per_solve  = dollars / verified solutions
//
// Both are counts of verifier exit codes and real dollars, not formulas. That is
// deliberate: the 2026-09-26 audit found 14 fabricated-metric defects, including a
// README energy chart that is arithmetic over hand-typed literals. You cannot fabricate
// an API bill, and you cannot fabricate `cargo test` exiting 0.
//
// If the local model improves, escalation rate falls and cost falls with it. The cost
// curve IS the learning curve.

const LEVELS = {
  L0: {
    name: 'L0 — simple Rust + Python solver problems',
    domains: ['rust', 'python'],
    goal: 'Establish a real local solve rate on problems with a hard verifier. High volume, fast feedback.',
    why: 'Rust first: rustc is the strictest verifier available and rejects error classes a Python test passes.',
  },
  L1: {
    name: 'L1 — Master level',
    domains: ['rust', 'python', 'math'],
    goal: 'Harder algorithmic + mathematical problems with independent verification.',
    why: 'Only attempt after L0 local solve rate is established and non-trivial.',
  },
  L2: {
    name: 'L2 — PhD level',
    domains: ['math', 'lean'],
    goal: 'Lean theorem proving against the axiom-checked gate; problems with no memorized answer.',
    why: 'Requires anse-lean-proof-gate to have run and its negative controls to pass.',
  },
}

const LEVEL_KEY = (args && args.level) || 'L0'
const LIMIT = (args && args.limit) || 20
const LEVEL = LEVELS[LEVEL_KEY]
if (!LEVEL) throw new Error(`unknown level ${LEVEL_KEY}; expected one of ${Object.keys(LEVELS).join(', ')}`)

const PREFLIGHT_SCHEMA = {
  type: 'object',
  properties: {
    eval_set_frozen: { type: 'boolean' },
    eval_train_overlap: { type: 'integer', description: 'MUST be 0 — any overlap invalidates the KPI' },
    eval_id_sha256: { type: 'string' },
    gpu_resident: { type: 'boolean' },
    local_tokens_per_sec: { type: 'number' },
    budget_supervisor_ready: { type: 'boolean' },
    tos_decision_recorded: { type: 'boolean' },
    blockers: { type: 'array', items: { type: 'string' } },
  },
  required: ['eval_set_frozen', 'eval_train_overlap', 'gpu_resident', 'budget_supervisor_ready', 'tos_decision_recorded', 'blockers'],
}

const CASCADE_SCHEMA = {
  type: 'object',
  properties: {
    domain: { type: 'string' },
    attempted: { type: 'integer' },
    solved_local: { type: 'integer' },
    solved_after_escalation: { type: 'integer' },
    unsolved: { type: 'integer' },
    harness_error: { type: 'integer' },
    escalation_rate: { type: 'number' },
    escalations_by_tier: { type: 'object', additionalProperties: true },
    usd_spent: { type: 'number' },
    cost_per_solve: { type: 'number' },
    episodes_written: { type: 'integer' },
    journal_path: { type: 'string' },
    evidence: { type: 'string' },
  },
  required: ['domain', 'attempted', 'solved_local', 'solved_after_escalation', 'unsolved', 'harness_error', 'escalation_rate', 'usd_spent', 'journal_path', 'evidence'],
}

const RULES = `
NON-NEGOTIABLE RULES:
  * Report only real command output and real spend. No estimated metrics.
  * NEVER escalate a problem the local model has not first attempted and verifiably
    failed. Bypassing the free tier defeats the entire cost model.
  * Escalate in ascending cost order (local -> haiku -> sonnet -> opus). Most
    escalations should resolve at the cheapest paid tier; if they do not, say so.
  * An attempt that errors in the harness is harness_error, never a model failure.
  * NEVER attempt a problem from the frozen EVAL set. EVAL is measured, never trained
    on and never used to drive escalation policy.
  * Use .venv/bin/python, PYTHONPATH=repo root, ANSE_LEAN_TESTS=0.
`

phase('Preflight')
log(`Cascade level ${LEVEL_KEY}: ${LEVEL.name} (limit ${LIMIT} per domain)`)

const pre = await agent(
  `${RULES}

Preflight the cascade for ${LEVEL.name}.

Verify and report, with evidence for each:

1. FROZEN EVAL SET. docs/remediation/BASELINE_HONEST.md should declare which problem
   ids are the frozen EVAL set (with a sha256 of that id list) and which are the TRAIN
   pool. Confirm the two sets have ZERO intersection and report the overlap count. A
   nonzero overlap is a hard stop: this repo has already had two leakage incidents —
   49/120 duplicate rows in the Phase-2 r=0.40 headline, and anse/jepa/dataset.py:389
   silently falling back to an item-level split when distinct tasks are too few.
   If BASELINE_HONEST.md does not exist yet, stop and report that as a blocker.

2. GPU RESIDENCY. Confirm the local model is on the GPU, not CPU. Check
   \`ollama ps\` shows "100% GPU" and \`nvidia-smi\` shows a llama-server compute process.
   Measure WARM tok/s (discard the first cold call — cold load measured ~297s, warm
   measured ~35 tok/s for qwen2.5-coder:7b-instruct). Report the warm number.
   Context: Ollama previously served CPU-only at 2.3 tok/s for days because it started
   before the GPU driver existed. Verify, do not assume.

3. BUDGET SUPERVISOR. There must be an EXTERNAL enforcer that kills the run at a spend
   ceiling — not a flag the child process can ignore. The existing
   scripts/night_phase_runner.py takes --budget-ceiling but a prior runaway still spent
   $9.76 across runs. Confirm a supervisor exists that polls actual spend and
   terminates. If it does not exist, build it at scripts/budget_supervisor.py.

4. ToS DECISION. Read docs/remediation/IMPROVEMENT_PLAN_2026-09-26.md for the recorded
   decision on whether paid-tier outputs may be used as TRAINING TARGETS. This is a
   policy question, not a code question. If the decision is "router only" (the safe
   default), episodes harvested from escalations are labelled trainable=false and only
   the local model's own verified samples train. Report which mode is in effect.
   Do NOT make this decision yourself — report it as a blocker if unrecorded.`,
  { label: 'preflight', phase: 'Preflight', schema: PREFLIGHT_SCHEMA }
)

if (pre.blockers.length || pre.eval_train_overlap !== 0 || !pre.tos_decision_recorded) {
  log(`HALT: preflight failed — ${pre.blockers.join('; ') || 'eval/train overlap or missing ToS decision'}`)
  return { level: LEVEL_KEY, preflight: pre, halted: true, cascade: [], accounting: null }
}

phase('Cascade')
const perDomain = await pipeline(
  LEVEL.domains,

  (domain) => agent(
    `${RULES}

Run the local-first verified cascade for domain "${domain}" at ${LEVEL.name}.
Goal: ${LEVEL.goal}
Rationale: ${LEVEL.why}

Sample at most ${LIMIT} problems from the TRAIN pool only (never EVAL).
Warm local throughput measured at preflight: ${pre.local_tokens_per_sec} tok/s.
ToS mode in effect: ${pre.tos_decision_recorded ? 'recorded — read the plan for which' : 'UNRECORDED'}

For each problem, in this exact order:
  1. LOCAL single-shot via anse.core.api_extractor.APIExtractor(ollama_native=True).
     Verify with the domain's real verifier.
  2. If failed: LOCAL best-of-N (N=4, varied temperature). Verify each.
  3. If still failed: escalate to the cheapest paid tier, then the next, stopping at
     the first verified success. Record which tier solved it and the actual USD.
  4. If all tiers fail: record unsolved. This is a legitimate outcome, not an error.

Journal EVERY attempt to .scratchpad/cascade/${LEVEL_KEY}_${domain}.jsonl with: problem_id,
tier, prompt, raw output, verifier exit code, verifier output, wall seconds, usd.

Report escalation_rate = (attempted - solved_local) / (attempted - harness_error), and
cost_per_solve = usd_spent / (solved_local + solved_after_escalation). Paste verbatim
output as evidence.`,
    { label: `cascade:${domain}`, phase: 'Cascade', schema: CASCADE_SCHEMA }
  ),

  (prev, domain) => {
    if (!prev || prev.attempted === 0) return null
    return agent(
      `${RULES}

Harvest verified episodes from the ${domain} cascade journal at ${prev.journal_path}.

Convert each VERIFIED attempt into the trace form the JEPA/QLoRA readers actually
consume. Critical schema detail from the audit: anse/memory/harvester.py:60 defaults
LoopTrace.metadata to {}, but anse/jepa/dataset.py:222-226 treats metadata["tests_total"]
as required and SILENTLY DROPS any row lacking it (counted as skipped["unverified"],
never raised). Only anse/core/agent_loop.py:484 sets it. So an episode written without
tests_total/tests_passed is invisible to training while appearing to be stored.

Therefore every harvested episode MUST carry: tests_total, tests_passed, the verifier's
exit code, difficulty_tier (anse/symbolic/evaluator.py:75-90 computes this from energy
and it is already persisted to trace.metadata), and a trainable flag set per the ToS
mode in effect.

Write episodes to data/episodes/${LEVEL_KEY}_${domain}.jsonl. Then PROVE they are
consumable: load them through the actual JEPA dataset reader and report how many rows
survive versus how many are dropped and why. A high drop count here is the single most
important thing to surface — it is the defect P4-2 exists to fix.`,
      { label: `harvest:${domain}`, phase: 'Harvest', schema: CASCADE_SCHEMA }
    )
  }
)

phase('Account')
const rows = perDomain.filter(Boolean)
const totalSpend = rows.reduce((s, r) => s + (r.usd_spent || 0), 0)
const totalSolved = rows.reduce((s, r) => s + (r.solved_local || 0) + (r.solved_after_escalation || 0), 0)
log(`Cascade complete: ${rows.length} domains, $${totalSpend.toFixed(2)} spent, ${totalSolved} verified solves`)

const accounting = await agent(
  `${RULES}

Write the cascade accounting to docs/remediation/CASCADE_${LEVEL_KEY}.md.

Real per-domain data from this run:
${JSON.stringify(rows, null, 2)}

Totals: $${totalSpend.toFixed(4)} spent, ${totalSolved} verified solves.

Include:
  1. Table: domain | attempted | solved local | solved after escalation | unsolved |
     harness error | escalation rate | $ | $/solve
  2. Escalation distribution by tier. If most escalations needed the most expensive
     tier, the cascade is not saving money and that must be stated.
  3. Episode yield: verified episodes written, and how many survive the JEPA dataset
     reader. Name the drop reasons.
  4. A promotion recommendation for the next rung, with an explicit threshold. Do NOT
     recommend advancing to a harder level if the local solve rate at this level is
     near zero — that ordering failure is how this project previously ended up with
     PhD-level claims and no working baseline.
  5. "What would make this number wrong" — the honest caveats (sample size, problem
     selection bias, whether any EVAL problem leaked in).`,
  { label: 'accounting', phase: 'Account' }
)

return { level: LEVEL_KEY, preflight: pre, cascade: rows, total_usd: totalSpend, total_solved: totalSolved, accounting }
