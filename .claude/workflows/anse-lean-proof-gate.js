export const meta = {
  name: 'anse-lean-proof-gate',
  description: 'Build one sound Lean proof gate (axiom-checked, not exit-code) and run local best-of-N proving against it',
  whenToUse: 'Before any Lean/theorem work is scored. Every existing Lean gate in the repo accepts `sorry`.',
  phases: [
    { title: 'Gate', detail: 'single verifier: compile then #print axioms, reject sorryAx' },
    { title: 'Negative control', detail: 'prove the gate can REJECT before trusting it to accept' },
    { title: 'Prover', detail: 'local prover client with per-model prompt formats + best-of-N' },
    { title: 'Run', detail: 'attempt real goals on the T4, journal every attempt with its axiom list' },
  ],
}

// WHY THIS WORKFLOW EXISTS
// Measured empirically during the 2026-09-26 audit:
//
//   theorem trivially_unproved (n : Nat) : n + 0 = n := by sorry
//   -> warning: declaration uses `sorry`     EXIT CODE 0
//   -> #print axioms  =>  depends on axioms: [sorryAx]
//
// `sorry` EXITS ZERO. Therefore every gate in this repo keyed on returncode accepts
// unproved theorems. There are ~10 independent `lake env lean` invocations and only
// ONE is sound: anse/formal/lean_runner.py:60, which emits `#print axioms` and checks
// for sorryAx. anse/symbolic/repl_pain_loop.py:145 tests returncode and then at
// :162-164 sets stderr="" on success, DISCARDING the sorry warning entirely.
//
// Consolidating to one axiom-checked gate is the whole point. Note also that
// anse/core/mcts_lean_solver.py has zero inbound imports — card P1-9 was spent
// hardening a proof gate nothing calls.

const GATE_SCHEMA = {
  type: 'object',
  properties: {
    gate_path: { type: 'string' },
    checks_axioms: { type: 'boolean' },
    rejects_sorry: { type: 'boolean' },
    rejects_unexpected_axiom: { type: 'boolean' },
    call_sites_migrated: { type: 'array', items: { type: 'string' } },
    call_sites_remaining: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'string' },
  },
  required: ['gate_path', 'checks_axioms', 'rejects_sorry', 'evidence'],
}

const CONTROL_SCHEMA = {
  type: 'object',
  properties: {
    negative_controls_run: { type: 'integer' },
    negative_controls_correctly_rejected: { type: 'integer' },
    positive_controls_run: { type: 'integer' },
    positive_controls_correctly_accepted: { type: 'integer' },
    gate_is_falsified: { type: 'boolean', description: 'true if the gate ever accepted something it should have rejected' },
    evidence: { type: 'string' },
  },
  required: ['negative_controls_run', 'negative_controls_correctly_rejected', 'positive_controls_run', 'positive_controls_correctly_accepted', 'gate_is_falsified', 'evidence'],
}

const RUN_SCHEMA = {
  type: 'object',
  properties: {
    goals_attempted: { type: 'integer' },
    proved_and_axiom_clean: { type: 'integer' },
    compiled_but_used_sorry: { type: 'integer' },
    failed_to_compile: { type: 'integer' },
    samples_per_goal: { type: 'integer' },
    model: { type: 'string' },
    tokens_per_sec: { type: 'number' },
    mean_verify_seconds: { type: 'number' },
    journal_path: { type: 'string' },
    evidence: { type: 'string' },
  },
  required: ['goals_attempted', 'proved_and_axiom_clean', 'compiled_but_used_sorry', 'failed_to_compile', 'journal_path', 'evidence'],
}

const RULES = `
NON-NEGOTIABLE RULES:
  * Report only real command output. This repo has a documented fabrication history.
  * A proof is accepted ONLY if the kernel compiles it AND \`#print axioms\` shows no
    sorryAx and no unexpected axiom. Exit code 0 alone is NOT proof — verified.
  * Never edit a goal statement to make it provable. Never weaken a theorem to True.
    (anse/v5/autonomous_curriculum.py:61-64 already contains
    \`theorem kdv_momentum_conservation ... : forall (t : R), True := by intro t; trivial\`
    — a vacuous statement presented as a PhD-level verified result. Do not add more.)
  * Lean toolchain is real: lean 4.34.0-rc2 / Lake 5.0.0 at ~/.elan/bin, matching
    formal/lean-toolchain. formal/.lake is a symlink to disk 2 with ~1,862 .olean
    (~17.6% of Mathlib).
  * Do NOT run a full Mathlib build. Start on goals with no Mathlib import — verified
    working: \`theorem t (n : Nat) : n + 0 = n := Nat.add_zero n\` compiles clean today.
`

phase('Gate')
const gate = await agent(
  `${RULES}

Create ONE sound Lean proof gate at \`anse/formal/proof_gate.py\`.

Lift the correct logic from \`anse/formal/lean_runner.py:47-90\` — it is the only sound
verifier in the repo. The gate must:
  1. Write the candidate to a temp .lean file.
  2. Compile with \`lake env lean\` from the \`formal/\` directory.
  3. Append \`#print axioms <declaration_name>\` and parse the output.
  4. ACCEPT only if compilation succeeds AND the axiom list contains no \`sorryAx\`
     and nothing outside an explicit allowlist (propext, Classical.choice, Quot.sound
     are the standard three and are acceptable).
  5. Return a structured result: accepted (bool), axioms (list), compile_stdout,
     compile_stderr, and a reason string when rejected.
  6. Raise rather than return a default when the toolchain itself is missing — never
     fail open.

Then inventory every other \`lake env lean\` call site (there are ~10; known ones include
anse/symbolic/repl_pain_loop.py:133, anse/symbolic/lean_rag_dojo.py:172,195,
anse/core/mcts_lean_solver.py:54, anse/core/hard_gate_compiler.py:44,
scripts/run_v10_swarm.py:48) and report which you migrated to this gate and which remain.

Do not delete anse/symbolic/repl_pain_loop.py's stderr-feedback repair loop — that
mechanism is useful for ITERATION. Only its ACCEPTANCE test is wrong. Route acceptance
through the new gate and keep the feedback loop.`,
  { label: 'build-gate', phase: 'Gate', schema: GATE_SCHEMA }
)

phase('Negative control')
// A gate that has never rejected anything is an unfalsified gate. This is the
// single most important stage: it is what the repo's existing "peer review"
// scripts never did (they hardcode ACCEPT with no model call at all).
const control = await agent(
  `${RULES}

Falsify the gate at ${gate.gate_path} before anyone trusts it.

Build a control corpus and run it through the gate:

NEGATIVE controls — the gate MUST reject every one:
  * \`theorem a (n : Nat) : n + 0 = n := by sorry\`            (sorryAx)
  * a proof left with an unsolved goal
  * \`theorem c : False := by sorry\`                           (proves False via sorry)
  * a vacuous restatement: \`theorem d : forall (t : Nat), True := by intro t; trivial\`
    presented as if it proved something substantive — the gate should accept this as
    *compiling* but your harness must flag it as vacuous, because this exact pattern
    is already in the repo at anse/v5/autonomous_curriculum.py:61-64.
  * a proof that introduces a custom \`axiom\` and uses it

POSITIVE controls — the gate MUST accept:
  * \`theorem e (n : Nat) : n + 0 = n := Nat.add_zero n\`
  * at least two more genuinely proved non-Mathlib goals

Report counts and set gate_is_falsified=true if the gate EVER accepted a negative
control. If it did, fix the gate and re-run until it does not.

Write the control corpus to \`tests/formal/test_proof_gate_controls.py\` as real pytest
tests so this can never silently regress. Each test needs genuine assertions — the
repo's test_rigor_guard.py rejects tests with zero assertions or tautological asserts,
and it currently flags 6 such tests.`,
  { label: 'negative-control', phase: 'Negative control', schema: CONTROL_SCHEMA }
)

if (control.gate_is_falsified) {
  log('STOP: the gate accepted a negative control. Not proceeding to proving — fix the gate first.')
  return { gate, control, proving: null, halted: 'gate_falsified' }
}

phase('Prover')
const prover = await agent(
  `${RULES}

Build the local prover client at \`anse/formal/prover_client.py\`.

Reuse \`anse/core/api_extractor.py:26-102\` — \`APIExtractor(ollama_native=True)\` already
posts to Ollama's /api/chat and honors seed/temperature (the docstring's "0.1.44 ignores
seed" caveat is stale; this box runs 0.34.1). Do not write a new HTTP client.

Add what is genuinely missing — the repo has ZERO prover-format knowledge
(scripts/lean_interactive_agent.py:52 is literally a mock returning "sorry"):
  1. Per-model prompt templates. DeepSeek-Prover-V2 and Goedel-Prover-V2 expect
     different formats; completion-style prompting was verified to work:
     "Complete the following Lean 4 proof:\\n\\n\`\`\`lean4\\n<theorem> := by\\n"
  2. A best-of-N sampler: N samples at varied temperature, each verified independently
     through ${gate.gate_path}, first axiom-clean success wins.
  3. Honest accounting: return all N attempts and their verdicts, not just the winner,
     so the per-goal success rate is measurable.

Available locally: hf.co/unsloth/DeepSeek-Prover-V2-7B-GGUF:Q8_0 and
hf.co/mradermacher/Goedel-Prover-V2-8B-GGUF:Q6_K.

VRAM note: Q8_0 needs ~9.5 GB of 14,912 MiB — it fits but leaves ~5 GB, so strictly one
prover at a time. OLLAMA_MAX_LOADED_MODELS=1 has been set. If throughput is poor,
recommend re-pulling at Q4_K_M (~4.5 GB) but measure before recommending.

Do NOT build MCTS. anse/symbolic/lean_mcts_prover.py exists with real UCB1 but its
tactic generator is a hardcoded 12-item list, and MCTS over a ~20s/verify compiler is
expensive with unproven value here. Establish the single-shot and best-of-N rates first.`,
  { label: 'build-prover', phase: 'Prover', schema: GATE_SCHEMA }
)

phase('Run')
const run = await agent(
  `${RULES}

Run real proof attempts on the T4 and report honest numbers.

Use ${prover.gate_path || 'anse/formal/prover_client.py'} with the gate at ${gate.gate_path}.

Goal set — start where no Mathlib build is needed:
  * A set of elementary Nat/List goals you write yourself (at least 10).
  * The 4 real open \`sorry\`s in this repo, which are genuine proof obligations, not
    placeholders: formal/ANSE/Theorems.lean:61, formal/ANSE/Basic.lean:160,
    formal/ANSE/System2.lean:170 and :185. formal/ANSE/Blueprint.lean:155-183 maintains
    a machine-readable registry of these — read it for what each obligation states.
    Attempt them, and expect to fail on most. Failure here is a real result.

Write \`scripts/prove_batch.py\` to drive this, journaling EVERY attempt (goal, sample
index, temperature, raw completion, gate verdict, axiom list, verify seconds) to
\`.scratchpad/proving/attempts.jsonl\`.

Report: goals_attempted, proved_and_axiom_clean, compiled_but_used_sorry (this count
existing per-goal is exactly what every other gate in the repo would have scored as a
WIN — call it out), failed_to_compile, measured tok/s, and mean verify seconds.

Paste verbatim output as evidence. If the local model proves nothing, that is the
honest baseline and it is what we need.`,
  { label: 'prove-batch', phase: 'Run', schema: RUN_SCHEMA }
)

return { gate, control, prover, run }
