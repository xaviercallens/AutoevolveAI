export const meta = {
  name: 'anse-claims-provenance',
  description: 'Trace every quantitative claim to an artifact, then adversarially review — the terminal gate for a publishable result',
  whenToUse: 'To reconcile README/paper claims with reality, and as the acceptance gate for the PhD-paper goal.',
  phases: [
    { title: 'Extract', detail: 'enumerate every quantitative claim in README and papers' },
    { title: 'Trace', detail: 'resolve each claim to a file, a key and a hash — or mark it unsupported' },
    { title: 'Review', detail: 'adversarial reviewers instructed to reject, plus a negative control' },
    { title: 'Verdict', detail: 'publishable / not, with the unsupported-claim list' },
  ],
}

// WHY THIS IS THE TERMINAL GATE
// The stated goal is "stop when a PhD-level paper passes peer review autonomously".
// Today that condition would fire immediately and falsely, because the peer review is
// a constant function:
//
//   scripts/review_paper_gemini_pro.py  -- reads the paper ONLY to assert len > 1000,
//     never analyses content, then hardcodes five ReviewDimension(score=10,
//     verdict="EXEMPLARY"), prints "TOTAL SCORE: 50 / 50", sets
//     overall_recommendation="ACCEPT WITHOUT RESERVATION", embeds a literal
//     proof_token, and writes the result to Redis attributed to "gemini-3.1-pro".
//     Grep for genai/openai/anthropic/httpx/requests in that file: ZERO hits.
//     The model was never invoked. Same pattern in review_phd_120_paper.py:147-205
//     and review_3_phd_cases_gemini_pro.py.
//
// So the first job is a reviewer that CAN reject, proven by a negative control. An
// unfalsified gate is not a gate.
//
// A NOTE ON AUTONOMY, stated plainly: a system cannot certify its own PhD-worthiness.
// That is structurally the same defect as everything above. This workflow makes a paper
// CANDIDATE-COMPLETE — every claim traced, every proof axiom-checked, adversarial review
// survived. Final acceptance is a human or a venue. Checks 1-6 are automatable; step 7
// is not, and pretending otherwise would reproduce the exact failure being fixed.

const CLAIM_SCHEMA = {
  type: 'object',
  properties: {
    source: { type: 'string' },
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim_id: { type: 'string' },
          text: { type: 'string' },
          number: { type: 'string' },
          cited_artifact: { type: 'string' },
        },
        required: ['claim_id', 'text'],
      },
    },
    total: { type: 'integer' },
  },
  required: ['source', 'claims', 'total'],
}

const TRACE_SCHEMA = {
  type: 'object',
  properties: {
    source: { type: 'string' },
    supported: { type: 'array', items: { type: 'object', additionalProperties: true } },
    unsupported: { type: 'array', items: { type: 'object', additionalProperties: true } },
    contradicted: { type: 'array', items: { type: 'object', additionalProperties: true } },
    artifact_missing: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'string' },
  },
  required: ['source', 'supported', 'unsupported', 'contradicted', 'evidence'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    model_actually_invoked: { type: 'boolean', description: 'must be true — the existing scripts fake this' },
    rejects: { type: 'boolean' },
    unsupported_claims_found: { type: 'array', items: { type: 'string' } },
    severity: { type: 'string', enum: ['fatal', 'major', 'minor', 'none'] },
    reasoning: { type: 'string' },
  },
  required: ['lens', 'model_actually_invoked', 'rejects', 'unsupported_claims_found', 'severity', 'reasoning'],
}

const TARGETS = (args && args.targets) || ['README.md', 'papers']

const RULES = `
NON-NEGOTIABLE RULES:
  * A claim is SUPPORTED only if you can name the file, the key/line, and re-derive the
    number from it. "A file with a plausible name exists" is not support.
  * A claim is CONTRADICTED if the cited artifact's own data disagrees with it.
  * Never repair a claim by editing the artifact. Fix the claim or mark it unsupported.
  * Any reviewer you build MUST make a real model call and MUST be able to reject. Prove
    it on a negative control before its ACCEPT means anything.
`

phase('Extract')
log(`Extracting quantitative claims from: ${TARGETS.join(', ')}`)

const traced = await pipeline(
  TARGETS,

  (target) => agent(
    `${RULES}

Enumerate every quantitative or verifiable claim in \`${target}\`.

For README.md that means each badge and each KPI table row. For the papers tree, each
numeric assertion in the .tex/.md sources (papers/ holds 26 PDFs, 23 .tex, and the
benchmark case sources).

Known examples to make sure you catch, from the 2026-09-26 audit:
  * "2,967 Lean 4 proofs" — actual: 218 theorem/lemma/example declarations across 34
    files. 2967 is a Lake BUILD-JOB count (mostly Mathlib dependencies), restated as
    authored proofs — a ~13.6x category error.
  * "200/200 Passing" — the cited results/200_unified_eval_report.json self-reports
    197/200 (verified {True:197, False:3}).
  * "-90.3% Energy Reduction" — every value in that chart (125.0, 38.2, 15.4, 12.1,
    11.2) is a hand-typed literal in scripts/orchestrate_*.py.
  * "License: MIT" — LICENSE does not exist in the repo.
  * "Closed-Loop Hardness 10/10" — badge says 10, the cited script's name says 5, and
    anti_stub_passed/closed_loop_passed are hardcoded True at :163-164 and :297-298.

Assign each claim a stable claim_id. Be exhaustive; do not stop at the known ones.`,
    { label: `extract:${target}`, phase: 'Extract', schema: CLAIM_SCHEMA }
  ),

  (prev, target) => {
    if (!prev || prev.total === 0) return null
    return agent(
      `${RULES}

Trace each of the ${prev.total} claims from \`${target}\` to an artifact.

Claims: ${JSON.stringify(prev.claims).slice(0, 6000)}

For each, resolve to {file, key_or_line, sha256, rederived_value} and classify:
  SUPPORTED   — artifact exists and its data reproduces the claim
  UNSUPPORTED — no artifact substantiates it (or the artifact does not exist)
  CONTRADICTED— the artifact's own data disagrees

Be even-handed. The audit found genuinely SUPPORTED claims too: the -97.8% human edit
distance IS computed (compute_edit_distance_ratio, orchestrate_2000_cases_eda.py:117,144,
though truncated to the first 300 chars), results/200_unified_eval_report.json is a real
run with genuine per-case variance, and the physics engines compute energy from a measured
invariant error rather than assigning it. Credit those.

Also note where the code is MORE honest than the prose: formal/ANSE/Theorems.lean:11
states "Every sorry below is a named proof obligation" and Blueprint.lean:155-183 keeps
a machine-readable status registry of the open obligations. The Lean sources disclose
their gaps; the README erases them. That asymmetry belongs in the report.

Write the mapping to docs/remediation/CLAIMS_TRACE_${target.replace(/[^a-z0-9]/gi, '_')}.json`,
      { label: `trace:${target}`, phase: 'Trace', schema: TRACE_SCHEMA }
    )
  }
)

const rows = traced.filter(Boolean)
const unsupportedTotal = rows.reduce((s, r) => s + r.unsupported.length + r.contradicted.length, 0)
log(`Traced: ${unsupportedTotal} unsupported or contradicted claims across ${rows.length} sources`)

phase('Review')
// Build a reviewer that can actually reject, then run diverse lenses over the paper.
// Negative control FIRST: if the reviewer cannot reject a knowingly-broken paper, its
// acceptance is worthless.
const control = await agent(
  `${RULES}

Build an honest reviewer and PROVE it can reject, before it reviews anything real.

Create \`scripts/review_paper.py\` that:
  1. Makes a REAL model call. Local first (qwen3:8b via
     anse.core.api_extractor.APIExtractor(ollama_native=True), measured ~35 tok/s warm
     on the T4 after the Ollama GPU fix); escalate to a paid tier only if the local
     model cannot follow the rubric.
  2. Takes a rubric with numeric thresholds and returns a structured verdict with
     per-criterion scores AND the specific claims it could not verify.
  3. Records which model actually answered, and fails loudly if no model was reached —
     never defaults to ACCEPT. Compare with anse/core/red_team.py:32-35, which on any
     Ollama failure falls through to a "simulated PRM" that returns PASS by default.

Then run the NEGATIVE CONTROL: feed it a deliberately broken paper — take a real paper
and inject a claim contradicted by its own cited artifact (e.g. assert 200/200 while
citing the report that says 197/200), plus a figure whose curve is synthesised.

The reviewer MUST reject it. If it accepts, the reviewer is broken: fix and re-run.
Report model_actually_invoked and whether rejection occurred.

Also delete or clearly quarantine the three fabricating review scripts
(review_paper_gemini_pro.py, review_phd_120_paper.py, review_3_phd_cases_gemini_pro.py)
and the two on-disk artifacts falsely attributed to gemini-3.1-pro
(papers/peer_review_gemini_3_1_pro.json, papers/peer_review_120_phd_cases.json), plus
the Redis key antigravity:paper:peer_review:gemini_3_1_pro. Attributing a review to a
model that was never called is the most serious integrity defect found in this repo.`,
  { label: 'reviewer-negative-control', phase: 'Review', schema: REVIEW_SCHEMA }
)

if (!control.model_actually_invoked || !control.rejects) {
  log('HALT: the reviewer could not be falsified — it failed to reject a knowingly-broken paper.')
  return { traced: rows, unsupported_total: unsupportedTotal, control, reviews: [], verdict: 'REVIEWER_UNFALSIFIED' }
}

// Perspective-diverse review: a paper can fail in several distinct ways, so give each
// reviewer a different lens rather than N identical skeptics.
const LENSES = [
  { key: 'provenance', prompt: 'Every number must trace to an artifact. Reject if any headline claim cannot be re-derived from a named file.' },
  { key: 'formal', prompt: 'Every cited theorem must compile with no sorryAx and no unexpected axiom. `sorry` exits 0 in Lean, so exit-code-based claims are void. Reject vacuous statements such as `: forall t, True := by trivial` presented as substantive results.' },
  { key: 'statistics', prompt: 'Reject any improvement claimed from a first-vs-last point comparison, any mean taken over sentinel placeholder values, and any effect within the noise floor. Check whether an effect size exceeds the series stdev.' },
  { key: 'reproducibility', prompt: 'Reject if results cannot be reproduced from a clean checkout at a pinned commit, or if artifacts embed paths from another machine (several results/ files embed /home/xavkal/ paths).' },
]

const reviews = await parallel(
  LENSES.map((lens) => () =>
    agent(
      `${RULES}

Review this project's strongest paper candidate through the ${lens.key.toUpperCase()} lens.

Your instruction for this lens: ${lens.prompt}

Default to REJECT when uncertain. You are the adversary; a paper that survives you is
worth something, and one you wave through is worth nothing.

Traced claim status from earlier phases (real data):
${JSON.stringify(rows.map((r) => ({ source: r.source, supported: r.supported.length, unsupported: r.unsupported.length, contradicted: r.contradicted.length })), null, 2)}

Use the honest reviewer built at scripts/review_paper.py — make a real model call and
report which model answered. List every specific claim you could not verify.`,
      { label: `review:${lens.key}`, phase: 'Review', schema: REVIEW_SCHEMA }
    )
  )
)

phase('Verdict')
const valid = reviews.filter(Boolean)
const rejecting = valid.filter((r) => r.rejects)
log(`${rejecting.length}/${valid.length} lenses reject; ${unsupportedTotal} claims unsupported or contradicted`)

const verdict = await agent(
  `${RULES}

Write the acceptance verdict to docs/remediation/PUBLICATION_GATE.md.

Claim tracing (real):
${JSON.stringify(rows.map((r) => ({ source: r.source, supported: r.supported.length, unsupported: r.unsupported.length, contradicted: r.contradicted.length, missing: r.artifact_missing })), null, 2)}

Reviewer negative control: invoked=${control.model_actually_invoked}, rejected_broken_paper=${control.rejects}
Adversarial lenses: ${rejecting.length} of ${valid.length} reject
${JSON.stringify(valid.map((r) => ({ lens: r.lens, rejects: r.rejects, severity: r.severity, found: r.unsupported_claims_found })), null, 2)}

State the candidate-complete criteria and mark each PASS/FAIL against the evidence:
  1. Every quantitative claim traces to an artifact and re-derives
  2. No claim cites a nonexistent file
  3. Every cited theorem compiles, axiom-clean
  4. Results reproduce from a clean checkout at a pinned commit
  5. No adversarial lens finds an unsupported claim
  6. Novelty: no prior work states the same result (use the alphaXiv tools available via
     ToolSearch to search the literature — make this a real search, not an assertion)

Then state plainly, as the report's conclusion: criteria 1-6 are machine-checkable and
this gate checks them; final acceptance as PhD-level work is a human or venue judgement
and is NOT self-certifiable. Recommend the concrete next action — which specific
unsupported claims to fix or retract first, ordered by severity.`,
  { label: 'publication-verdict', phase: 'Verdict' }
)

return {
  traced: rows,
  unsupported_total: unsupportedTotal,
  control,
  reviews: valid,
  lenses_rejecting: rejecting.length,
  candidate_complete: rejecting.length === 0 && unsupportedTotal === 0,
  verdict,
}
