export const meta = {
  name: 'anse-phd-paper',
  description: 'Take one PhD-level physics problem from statement to a provenance-complete paper: derive, formalise in Lean, verify numerically in two languages, then review adversarially',
  whenToUse: 'To produce a publishable-rigor artifact. Pass args {problem:"...", domain:"physics"} or omit for the reference problem.',
  phases: [
    { title: 'Derive', detail: 'symbolic derivation — no algebra recalled from memory' },
    { title: 'Formalise', detail: 'Lean 4 proof, accepted only on an axiom audit' },
    { title: 'Measure', detail: 'two independent implementations that must agree' },
    { title: 'Write', detail: 'paper with every number injected from the ledger' },
    { title: 'Review', detail: 'adversarial referees, falsified on a negative control first' },
  ],
}

// THE GOAL, STATED AS A GATE
// A paper is CANDIDATE-COMPLETE when all six hold. Each is machine-checkable;
// none is a matter of opinion:
//
//   G1  Every quantitative claim resolves to a ledger key and re-derives.
//   G2  No claim cites a file that does not exist.
//   G3  Every cited theorem compiles with NO sorryAx and no unexpected axiom,
//       and no theorem is vacuous (nothing of the form `True`).
//   G4  Results reproduce from a clean checkout at a pinned commit.
//   G5  No adversarial lens finds an unsupported claim — and the reviewer was
//       proven able to reject a knowingly-broken paper first.
//   G6  Novelty: a real literature search finds no prior work stating the result.
//
// WHAT THIS WORKFLOW DELIBERATELY DOES NOT CLAIM. It does not certify that the
// work is PhD-worthy. A system cannot certify its own significance — that is
// structurally the same defect as the repo's `review_paper_gemini_pro.py`, which
// hardcodes ACCEPT WITHOUT RESERVATION and never calls a model. G1-G6 are
// automatable; "this is a contribution" is a judgement for a human or a venue.
// The honest finish line is: candidate-complete, then a human signs off.
//
// REFERENCE RUN (already executed; see scripts/phd_demo/ and papers/phd_demo_verlet/)
// Störmer-Verlet on the harmonic oscillator. SymPy derived det M = 1 and the
// shadow Hamiltonian; Lean proved 7 theorems with zero sorryAx; Python and Rust
// agreed to 5.5e-10; the measured ratio amplitude/h^2 matched the proved
// omega^2/4 to nine significant figures. Use it as the template.

const PROBLEM = (args && args.problem) ||
  'Störmer–Verlet integrator for the harmonic oscillator: exact symplecticity, ' +
  'the exactly-conserved modified Hamiltonian, and the resulting bounded energy error'
const DOMAIN = (args && args.domain) || 'computational physics / geometric integration'
const LOOPS = (args && args.reviewLoops) || 3

const RULES = `
NON-NEGOTIABLE RULES. This repository has a documented history of fabricated
results (docs/remediation/AUDIT_2026-09-26.md lists 14 components that reported
success without doing the work). Violating these is worse than failing the task.

  * NEVER state a mathematical result from memory. Derive it symbolically with
    SymPy and keep the derivation as an artifact. If you cannot derive it, say so.
  * NEVER write a number you did not compute. Every figure in the paper must be
    injected from the artifact ledger by a key lookup that RAISES when absent.
  * NEVER accept a Lean proof on its exit code. \`sorry\` compiles and exits 0.
    Acceptance requires \`#print axioms\` showing no sorryAx.
  * NEVER state a theorem you weakened to make it provable. A vacuous
    \`∀ t, True\` presented as a result is the worst outcome available — and
    anse/v5/autonomous_curriculum.py:61-64 already contains one.
  * NEVER synthesise a figure. scripts/generate_phd_paper_figures.py:199-202 plots
    initial_loss*(1-0.201*(1-exp(-e/5))) + noise as a measured loss curve. Plot
    real computed arrays or plot nothing.
  * A gap is a result. "This could not be verified" is a publishable sentence;
    a plausible invented number is not.

Environment: .venv/bin/python, PYTHONPATH=repo root, ANSE_LEAN_TESTS=0.
Lean 4.34.0-rc2 via \`cd formal && lake env lean <file>\` (Mathlib.Tactic.Ring is
in the built cache; do NOT run a full Mathlib build). Rust 1.96 via ~/.cargo/bin.
Local model qwen3:8b on the T4 at ~35 tok/s warm — free; prefer it over paid calls.
`

const DERIVE_SCHEMA = {
  type: 'object',
  properties: {
    script_path: { type: 'string' },
    statements_derived: { type: 'array', items: { type: 'string' } },
    key_identities: { type: 'object', additionalProperties: true },
    anything_asserted_from_memory: { type: 'boolean' },
    evidence: { type: 'string' },
  },
  required: ['script_path', 'statements_derived', 'anything_asserted_from_memory', 'evidence'],
}

const LEAN_SCHEMA = {
  type: 'object',
  properties: {
    lean_path: { type: 'string' },
    theorems: { type: 'array', items: { type: 'string' } },
    exit_code: { type: 'integer' },
    sorry_ax_present: { type: 'boolean' },
    vacuous_statements: { type: 'array', items: { type: 'string' } },
    accepted: { type: 'boolean' },
    axiom_lines: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'string' },
  },
  required: ['lean_path', 'theorems', 'exit_code', 'sorry_ax_present', 'accepted', 'evidence'],
}

const MEASURE_SCHEMA = {
  type: 'object',
  properties: {
    ledger_path: { type: 'string' },
    implementations: { type: 'array', items: { type: 'string' } },
    cross_language_worst_rel_diff: { type: 'number' },
    cross_language_agree: { type: 'boolean' },
    theory_matches_measurement: { type: 'boolean' },
    figures: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'string' },
  },
  required: ['ledger_path', 'implementations', 'cross_language_agree', 'theory_matches_measurement', 'evidence'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    negative_control_passed: { type: 'boolean' },
    loops_run: { type: 'integer' },
    final_accepted: { type: 'boolean' },
    unsupported_claims_remaining: { type: 'array', items: { type: 'string' } },
    fixes_applied: { type: 'array', items: { type: 'string' } },
    evidence: { type: 'string' },
  },
  required: ['negative_control_passed', 'loops_run', 'final_accepted', 'evidence'],
}

phase('Derive')
log(`Problem: ${PROBLEM}`)

const derivation = await agent(
  `${RULES}

Derive the mathematics for this problem symbolically.

PROBLEM: ${PROBLEM}
DOMAIN: ${DOMAIN}

Write a SymPy script under scripts/phd_demo/ that DERIVES every identity the paper
will rely on — the governing equations, the discrete map if there is one, any
Jacobian/determinant/trace, and any conserved quantity (solve for it; do not posit
it). Print each result.

Then translate the physics into precise mathematical statements suitable for
formalisation: each must be a closed identity or inequality with explicit
quantifiers, and none may be vacuous.

Set anything_asserted_from_memory=true if you could not derive something and had
to state it. That is an honest answer and I need to know.`,
  { label: 'sympy-derive', phase: 'Derive', schema: DERIVE_SCHEMA }
)

if (derivation && derivation.anything_asserted_from_memory) {
  log('WARNING: some statements were asserted rather than derived — flagged in the record')
}

phase('Formalise')
const lean = await agent(
  `${RULES}

Formalise the derived statements in Lean 4 and pass the axiom audit.

Derived statements: ${JSON.stringify(derivation.statements_derived)}
Key identities: ${JSON.stringify(derivation.key_identities || {}).slice(0, 2500)}

Write formal/ANSE/<Name>.lean. Guidance from the reference run:
  * \`import Mathlib.Tactic.Ring\` is available from the built cache and is enough
    for polynomial identities. Do not import all of Mathlib.
  * State theorems over a CONCRETE field (ℚ or ℝ), not a general \`Field K\`.
    \`ring\` cannot prove 2⁻¹·2 = 1 over an arbitrary field because characteristic
    2 is a real counterexample — this exact mistake produced four sorryAx
    theorems on the first attempt of the reference run.
  * End the file with \`#print axioms\` for EVERY theorem.

Compile with \`cd formal && lake env lean <path>\`. Acceptance requires: exit 0,
at least one theorem, and sorryAx appearing NOWHERE. Set accepted accordingly and
paste the axiom lines verbatim as evidence.

Also list any theorem whose statement is vacuous (provable by \`trivial\` regardless
of the mathematics). Those must be rewritten, not shipped.`,
  { label: 'lean-formalise', phase: 'Formalise', schema: LEAN_SCHEMA }
)

if (!lean || !lean.accepted) {
  log(`HALT: Lean gate rejected (sorryAx=${lean && lean.sorry_ax_present}). ` +
      `Not writing a paper around unproved theorems.`)
  return { problem: PROBLEM, derivation, lean, halted: 'lean_rejected' }
}

phase('Measure')
const measurement = await agent(
  `${RULES}

Implement and measure, in TWO independent languages, and write the artifact ledger.

Proved theorems available to test against: ${JSON.stringify(lean.theorems)}

Requirements:
  1. A Python implementation and a Rust implementation, written independently.
  2. They must agree within a DECLARED tolerance; the script must FAIL on
     disagreement rather than reporting it as a note.
  3. A contrast case that should behave badly (e.g. a non-symplectic scheme) so
     the result is discriminating rather than merely consistent.
  4. A parameter sweep confirming the predicted scaling law, compared against the
     constant the Lean theorems establish.
  5. Figures plotted from the REAL computed arrays.
  6. A ledger at results/phd_demo/artifacts.json holding every number plus a
     sha256 for each figure, and a \`gates\` block recording which checks passed.

Follow the reference implementation in scripts/phd_demo/run_experiment.py, which
already does exactly this and can be extended.

Report the worst cross-language relative difference and whether measurement
matches the proved theory.`,
  { label: 'measure', phase: 'Measure', schema: MEASURE_SCHEMA }
)

if (!measurement || !measurement.cross_language_agree || !measurement.theory_matches_measurement) {
  log('HALT: measurement failed cross-language agreement or disagreed with the proved theory.')
  return { problem: PROBLEM, derivation, lean, measurement, halted: 'measurement_failed' }
}

phase('Write')
const paper = await agent(
  `${RULES}

Write the paper. Every number comes from the ledger; none is typed.

Ledger: ${measurement.ledger_path}
Figures: ${JSON.stringify(measurement.figures)}
Lean theorems: ${JSON.stringify(lean.theorems)}

Extend scripts/phd_demo/build_paper.py. Its central property must be preserved:
the generator contains NO quantitative literal about the results, and its ledger
accessor RAISES on a missing key so the build fails rather than emitting a
plausible value.

Structure: abstract, introduction, mathematical setting with numbered theorems,
a machine-checked-verification section quoting the real axiom lines, the numerical
experiment with ledger-built tables, cross-language agreement, and a section on
context management and fabrication avoidance that states the countermeasures and
the SCOPE OF THE CLAIM — what the result does not establish.

Compile to PDF with pdflatex (siunitx is NOT installed; define \\num locally or
avoid it, and escape underscores inside \\texttt). Report the PDF path and size.`,
  { label: 'write-paper', phase: 'Write' }
)

phase('Review')
const review = await agent(
  `${RULES}

Review the paper adversarially, and prove the reviewer can reject BEFORE trusting it.

Use scripts/phd_demo/peer_review.py, which already implements this:
  * A real model call (local qwen3:8b on the T4; raises if unreachable and never
    defaults to accept).
  * A NEGATIVE CONTROL: a corrupted paper with a claim the ledger contradicts.
    The reviewer MUST reject it. If it does not, the reviewer is broken — fix it
    and re-run before any acceptance counts.
  * Three perspective-diverse lenses: provenance, formal, statistics.

Run ${LOOPS} improvement loops. After each loop, for every unsupported claim the
referees identify: either correct it in the paper (and rebuild so the ledger and
text stay consistent), or WITHDRAW the claim. Do not argue with a referee by
restating the claim.

Report negative_control_passed, loops_run, final_accepted, any unsupported claims
still standing, and the fixes you applied. If the referees still reject after
${LOOPS} loops, report that honestly — a rejected paper is a real outcome and far
more useful than a fabricated acceptance.`,
  { label: 'peer-review', phase: 'Review', schema: REVIEW_SCHEMA }
)

// Final gate evaluation. G4 and G6 are reported, not asserted, since a clean-checkout
// reproduction and a literature search need resources this workflow may not have.
const gates = {
  G1_claims_trace_to_ledger: Boolean(measurement.theory_matches_measurement),
  G3_lean_axiom_clean: Boolean(lean.accepted && !lean.sorry_ax_present),
  G3_no_vacuous_theorems: (lean.vacuous_statements || []).length === 0,
  G5_reviewer_falsified: Boolean(review && review.negative_control_passed),
  G5_no_unsupported_claims: Boolean(review && review.final_accepted),
  cross_language_agree: Boolean(measurement.cross_language_agree),
}
const candidateComplete = Object.values(gates).every(Boolean)

log(`Gates: ${JSON.stringify(gates)}`)
log(candidateComplete
  ? 'CANDIDATE-COMPLETE — all machine-checkable gates pass. Human sign-off is the remaining step.'
  : 'NOT candidate-complete — see the failing gates above.')

return {
  problem: PROBLEM,
  derivation,
  lean,
  measurement,
  paper,
  review,
  gates,
  candidate_complete: candidateComplete,
  note: 'G2/G4/G6 (dead links, clean-checkout reproduction, novelty search) are ' +
        'checked by anse-claims-provenance. PhD-worthiness is not self-certifiable.',
}
