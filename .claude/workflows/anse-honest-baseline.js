export const meta = {
  name: 'anse-honest-baseline',
  description: 'Restructure the 200-case bank into real (statement, hidden test) problems and measure the first honest local pass rate',
  whenToUse: 'Milestone 1. Run before any training or ladder work — every later metric is measured against this baseline.',
  phases: [
    { title: 'Restructure', detail: 'split each domain bank into statement + hidden reference + tolerance' },
    { title: 'Harness', detail: 'build the local-model attempt runner and the per-domain verifier' },
    { title: 'Measure', detail: 'run the bank on the local T4 model and record verified outcomes' },
    { title: 'Report', detail: 'honest baseline table, and an explicit list of what could not be measured' },
  ],
}

// WHY THIS WORKFLOW EXISTS
// The 2026-09-26 audit established that all 200 cases in anse/benchmark/ embed
// their own solution: RUST_KERNELS[id]["source"] IS the finished program, and the
// math/physics/python cases compute a value then compare it to the same constant.
// The "200/200 passing" badge therefore measures "does this machine run the
// reference implementation", with no model generation anywhere in the loop.
// Nothing downstream can be trusted until that is fixed, so this runs first.
//
// COST DISCIPLINE: the agents here BUILD and VERIFY the harness. They do not
// solve problems themselves. All candidate generation is local T4 inference
// invoked by the scripts they write. Paid tokens buy engineering, not answers.

const DOMAINS = [
  {
    key: 'rust',
    bank: 'anse/benchmark/rust_numeric_cases.py',
    count: 50,
    verifier: 'rustc -O compile + run + parse telemetry (compile_and_run_rust, ~:1798)',
    note: 'Strongest verifier available — the Rust compiler rejects whole classes of error a Python test would pass. Reuse compile_and_run_rust but feed it MODEL OUTPUT instead of kernel["source"].',
  },
  {
    key: 'python',
    bank: 'anse/benchmark/complex_python_cases.py',
    count: 50,
    verifier: 'anse/symbolic/sandbox.py Tier-1 subprocess with resource limits',
    note: 'Only domain already wired to the agent loop; sandbox is real and reusable as-is.',
  },
  {
    key: 'math',
    bank: 'anse/benchmark/pure_math_cases.py',
    count: 50,
    verifier: 'NONE TODAY — cases self-assert via SymPy against their own constant',
    note: 'Needs an independent oracle. Either a CAS re-derivation from the statement alone, or a Lean statement checked by anse/formal/proof_gate.py. Report honestly if neither is ready rather than scoring it.',
  },
  {
    key: 'physics',
    bank: 'anse/benchmark/pure_physics_cases.py',
    count: 50,
    verifier: 'NONE TODAY — same self-assertion defect as math',
    note: 'invariant_registry.yaml gives per-case invariant_type/tolerance/units — that IS a usable independent check (dimensional + conservation), unlike the in-function assert. Build the verifier from the registry.',
  },
]

const RESTRUCTURE_SCHEMA = {
  type: 'object',
  properties: {
    domain: { type: 'string' },
    problems_written: { type: 'integer' },
    output_path: { type: 'string' },
    statement_leaks_solution: { type: 'integer', description: 'count of problems whose statement still contains the answer' },
    verifier_ready: { type: 'boolean' },
    verifier_path: { type: 'string' },
    blockers: { type: 'array', items: { type: 'string' } },
  },
  required: ['domain', 'problems_written', 'output_path', 'statement_leaks_solution', 'verifier_ready', 'blockers'],
}

const MEASURE_SCHEMA = {
  type: 'object',
  properties: {
    domain: { type: 'string' },
    attempted: { type: 'integer' },
    verified_pass: { type: 'integer' },
    verified_fail: { type: 'integer' },
    harness_error: { type: 'integer', description: 'attempts that could not be scored at all — never count these as pass or fail' },
    pass_rate: { type: 'number' },
    model: { type: 'string' },
    tokens_per_sec: { type: 'number' },
    wall_clock_s: { type: 'number' },
    results_path: { type: 'string' },
    evidence: { type: 'string', description: 'verbatim tail of the real command output proving these numbers' },
  },
  required: ['domain', 'attempted', 'verified_pass', 'verified_fail', 'harness_error', 'pass_rate', 'results_path', 'evidence'],
}

const RULES = `
NON-NEGOTIABLE RULES (this repo has a documented history of fabricated metrics —
see docs/remediation/AUDIT_2026-09-26.md):
  * Report only real command output. Never write a number you did not observe.
  * If something cannot be measured, report it as unmeasured. A gap is a result.
  * Never let a problem statement contain its own answer. Verify this and count leaks.
  * An attempt that errors in the harness is NOT a failure of the model — count it
    separately as harness_error and never fold it into pass or fail.
  * Do not edit the verifier to make results look better.
  * Use .venv/bin/python (system python3 breaks on numpy/zarr). Set PYTHONPATH=repo root
    and ANSE_LEAN_TESTS=0.
`

phase('Restructure')
log(`Restructuring ${DOMAINS.length} domain banks into real problems (statement + hidden reference)`)

// Pipeline, not parallel: each domain flows Restructure -> Harness -> Measure
// independently. Rust can be measuring while math is still being restructured.
const results = await pipeline(
  DOMAINS,

  // Stage 1: split the bank into problems whose statements do NOT leak the answer.
  (d) => agent(
    `${RULES}

Restructure the problem bank at \`${d.bank}\` (${d.count} cases) into real agent problems.

Today each case embeds its own solution, so the bank is a self-test rather than a
benchmark. Convert it into a JSON file of problems with this shape:

  {"problem_id": "...", "domain": "${d.key}", "statement": "<what to solve, NO solution text>",
   "hidden_reference": "<reference answer/implementation, kept OUT of the statement>",
   "tolerance": <number or null>, "invariant": "<from invariant_registry.yaml if applicable>"}

Write to \`.scratchpad/baseline/problems_${d.key}.json\`.

Verifier situation for this domain: ${d.verifier}
Guidance: ${d.note}

Also reuse \`anse/benchmark/invariant_registry.yaml\` (993 lines of per-case
invariant_type / tolerance / units) — it is the most reusable asset in the bank.

Then CHECK YOUR OWN WORK: for every problem, confirm the statement does not contain
the reference answer (substring and near-duplicate check). Report the leak count
honestly — a nonzero count is expected on the first pass and must be visible.`,
    { label: `restructure:${d.key}`, phase: 'Restructure', schema: RESTRUCTURE_SCHEMA }
  ),

  // Stage 2: build the attempt runner + verifier for this domain.
  (prev, d) => {
    if (!prev || prev.problems_written === 0) {
      log(`SKIP ${d.key}: restructure produced no problems`)
      return null
    }
    return agent(
      `${RULES}

Build the attempt-and-verify harness for domain "${d.key}".

Restructured problems are at: ${prev.output_path} (${prev.problems_written} problems).
Reported solution leaks in statements: ${prev.statement_leaks_solution}
Verifier readiness from stage 1: ${prev.verifier_ready}
Known blockers: ${JSON.stringify(prev.blockers)}

Write \`scripts/baseline/attempt_${d.key}.py\` that:
  1. Loads the problems JSON.
  2. For each problem, sends ONLY the statement to the LOCAL model via
     anse.core.api_extractor.APIExtractor(..., ollama_native=True). Do NOT call any
     paid API. Do NOT include hidden_reference in the prompt.
  3. Runs the real verifier on the model's output: ${d.verifier}
  4. Journals every attempt to .scratchpad/baseline/attempts_${d.key}.jsonl with the
     prompt, raw output, verifier exit code, verifier stdout/stderr, and wall time.
  5. Prints a summary: attempted / verified_pass / verified_fail / harness_error.

IMPORTANT on the local model: a prior measurement found Ollama had been serving on
CPU at 2.3 tok/s because it started before the GPU driver existed. It has since been
restarted with OLLAMA_MAX_LOADED_MODELS=1. Measure and report actual tok/s — if it is
still single-digit, say so loudly, because it changes what sample size is feasible.

If this domain has no sound verifier (math/physics today), DO NOT invent one and DO
NOT fall back to the case's own self-assert. Either build a genuinely independent
check from invariant_registry.yaml, or report verifier_ready=false and stop. An
honest "cannot score this domain yet" is the correct deliverable.`,
      { label: `harness:${d.key}`, phase: 'Harness', schema: RESTRUCTURE_SCHEMA }
    )
  },

  // Stage 3: actually run it and record what happened.
  (prev, d) => {
    if (!prev || !prev.verifier_ready) {
      log(`SKIP measure:${d.key} — no sound verifier (this is a finding, not a failure)`)
      return null
    }
    return agent(
      `${RULES}

Run the baseline measurement for domain "${d.key}" and report the REAL numbers.

Execute \`scripts/baseline/attempt_${d.key}.py\`. Start with a sample of at most 15
problems so a slow local model does not stall the run; if throughput allows, extend
toward the full set and report exactly how many you attempted.

Report:
  - attempted / verified_pass / verified_fail / harness_error (these must sum correctly)
  - pass_rate computed ONLY over (verified_pass + verified_fail), excluding harness_error
  - measured tokens_per_sec of the local model
  - the path to the attempts JSONL
  - 'evidence': paste the verbatim tail of the script's actual stdout

This number becomes the project's first honest baseline. It will probably be low.
A low true number is the deliverable; a high false one is the thing being eliminated.`,
      { label: `measure:${d.key}`, phase: 'Measure', schema: MEASURE_SCHEMA }
    )
  }
)

phase('Report')
const measured = results.filter(Boolean).filter((r) => typeof r.pass_rate === 'number')
const unmeasured = DOMAINS.filter((d) => !measured.find((m) => m.domain === d.key)).map((d) => d.key)

log(`Measured ${measured.length}/${DOMAINS.length} domains; unmeasured: ${unmeasured.join(', ') || 'none'}`)

const report = await agent(
  `${RULES}

Write the honest baseline report to \`docs/remediation/BASELINE_HONEST.md\`.

Measured domains (real data from this run):
${JSON.stringify(measured, null, 2)}

Domains that could NOT be measured: ${JSON.stringify(unmeasured)}

The report must contain:
  1. A table: domain | attempted | verified pass | verified fail | harness error | true pass rate
  2. An explicit section "What this replaces" contrasting these numbers with the
     README's "200/200 Passing" badge and the -90.3% energy claim, both of which the
     audit found to be arithmetic over hand-typed literals in scripts/orchestrate_*.py.
  3. A section "Not measured, and why" for every unmeasured domain — no estimates.
  4. The exact commands to reproduce, and the measured local model throughput.
  5. A frozen-set declaration: which problem ids are reserved as the EVAL set that
     must never be trained on, with a sha256 of that id list. Everything else is the
     TRAIN pool. This matters because escalation-rate improvement is only meaningful
     against a held-out set, and this repo has already had two leakage incidents
     (49/120 duplicate rows; dataset.py:389 silently falling back to an item-level split).

Do not editorialize beyond the evidence. If the baseline is poor, say so plainly.`,
  { label: 'baseline-report', phase: 'Report' }
)

return { measured, unmeasured, report_path: 'docs/remediation/BASELINE_HONEST.md', report }
