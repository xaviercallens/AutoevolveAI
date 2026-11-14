export const meta = {
  name: 'openai-math-night-lab-v2',
  description: 'Overnight openai_math lab, per-lane pipeline: preregister -> commit own prereg -> run -> adversarial verify; then synthesize and commit',
  whenToUse: 'Nightly openai_math hypothesis lab. args = {date: "YYYY-MM-DD", deadline: "HH:MM UTC" (optional), lanes: [{key, cpu, task}]}',
  phases: [
    { title: 'Preregister', detail: 'each lane designs its run and writes a preregistration (cap 60 min)' },
    { title: 'Commit prereg', detail: 'each lane commits its own preregistration before running' },
    { title: 'Run', detail: 'lane runs its preregistered experiment with controls' },
    { title: 'Verify', detail: 'adversarial check of the lane report against its artifacts' },
    { title: 'Synthesize', detail: 'docs, results.tsv, ledger, tests; commit and push' },
  ],
}

// v2 (2026-10-08): night one used a barrier after preregistration, and one lane (H4) spent
// ~7 h preregistering while the other three waited. Each lane now flows on its own.

const WT = '/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery'
const CLONE = '/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math'
const NIGHT = `${WT}/results/openai_math/hypotheses/night_${args.date}`
const ATTR = 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01H1rranmjAFwTfcqjKqVQq5'

const COMMON = `
You are one lane of an overnight research workflow in the AutoevolveAI repo, worktree ${WT} (branch worktree-openai-math-discovery). Read ${WT}/docs/OPENAI_MATH_HYPOTHESES.md and ${WT}/scripts/openai_math/hypotheses/program.md first.
Hard rules:
- Shell: plain commands with literal absolute paths; no shell variables, no shell for-loops, no git -C; loops go inside python3 scripts. Use /usr/bin/python3 (numpy, scipy, cypari2, mpmath, python-flint).
- Never run git commit/push/stash/checkout unless your stage says so. Never touch data/chroma. Write only inside your lane directory and the new files your lane owns.
- A single Bash call must finish within 9 minutes: run long work as resumable chunks across calls. Respect your CPU allotment; the T4 GPU belongs to the LTM ingest and the 05:05 retrain.
- Every reported number comes from a file you wrote with real tool output. If something cannot run, report BLOCKED with the reason; never fabricate, simulate or estimate.
- Positive and negative controls must pass before a number counts.
- Upstream openai/math claims are claims by another model. Clone (read-only): ${CLONE}.
`

const PREREG = {
  type: 'object',
  properties: {
    lane: { type: 'string' }, preregistration_path: { type: 'string' },
    files_to_commit: { type: 'array', items: { type: 'string' } },
    plan: { type: 'string' }, blocked: { type: 'boolean' }, reason: { type: 'string' },
  },
  required: ['lane', 'preregistration_path', 'files_to_commit', 'plan', 'blocked', 'reason'],
}
const REPORT = {
  type: 'object',
  properties: {
    lane: { type: 'string' }, status: { type: 'string', enum: ['DONE', 'PARTIAL', 'BLOCKED'] },
    preregistration_path: { type: 'string' },
    result_paths: { type: 'array', items: { type: 'string' } },
    new_code_paths: { type: 'array', items: { type: 'string' } },
    headline: { type: 'string' }, numbers: { type: 'string' }, controls_pass: { type: 'boolean' },
    claims: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['lane', 'status', 'preregistration_path', 'result_paths', 'new_code_paths', 'headline', 'numbers', 'controls_pass', 'claims', 'notes'],
}
const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['CONFIRMED', 'CORRECTIONS_NEEDED', 'REJECTED'] },
    corrections: { type: 'array', items: { type: 'string' } }, evidence: { type: 'string' },
  },
  required: ['verdict', 'corrections', 'evidence'],
}

const lanes = (args.lanes || []).map(l => ({ ...l, dir: `${NIGHT}/${l.key}` }))
if (!lanes.length) {
  log('no lanes passed in args.lanes; nothing to do')
  return { summary: 'no lanes', lanes: [] }
}

const results = await pipeline(
  lanes,
  l => agent(`${COMMON}
LANE ${l.key}. CPU allotment: ${l.cpu}. Lane directory: ${l.dir} (create it).
${l.task}

THIS STAGE ONLY (hard cap: 60 minutes of work; if your design research is unfinished by then, preregister the reduced run you can justify now and list the open design questions in the preregistration): write ${l.dir}/preregistration.json BEFORE running anything that produces the lane's result. Include the hypothesis id and statement, the statistic or verdict categories, the exact decision rule, the positive and negative controls, the CPU and time budget, the code paths with their sha256 (write new code first and smoke-test it on tiny inputs; disclose any smoke-test numbers seen), and the date ${args.date}. Return the files to commit.`, { label: `prereg:${l.key}`, phase: 'Preregister', schema: PREREG }),
  (pre, l) => pre && (pre.blocked ? { blocked: true, pre } : agent(`In ${WT}, commit lane ${l.key}'s preregistration so it is on record BEFORE the lane runs. Files: ${JSON.stringify(pre.files_to_commit)}.
Run python3 -m pytest on any listed test files; leave a failing test file uncommitted and say so. git add exactly the listed paths (never data/chroma); if git reports .git/index.lock exists, another lane is committing: wait 30 s and retry, up to 10 times. Check git diff --cached --stat shows only your paths, then commit with message "prereg(openai_math): night ${args.date} lane ${l.key}" ending with the two lines
${ATTR}
and git push (if the push is rejected because the remote moved, git pull --rebase then push). Plain commands only. Return the commit sha.`, { label: `commit:${l.key}`, phase: 'Commit prereg' }).then(sha => ({ blocked: false, pre, sha }))),
  (c, l) => c && !c.blocked && agent(`${COMMON}
LANE ${l.key}. CPU allotment: ${l.cpu}. Lane directory: ${l.dir}.
${l.task}

Your preregistration is committed (${c.sha}) at ${l.dir}/preregistration.json: follow it exactly. Write any deviation into ${l.dir}/deviations.md BEFORE the affected run. Controls first, then the preregistered run, in resumable chunks, until done or about ${args.deadline || '06:30 UTC'}. Write ${l.dir}/result.json and ${l.dir}/lane_results.tsv (columns of ${WT}/results/openai_math/hypotheses/results.tsv). Return the lane report.`, { label: `run:${l.key}`, phase: 'Run', schema: REPORT }),
  (rep, l) => rep && agent(`Adversarial verifier: default to finding problems. Lane ${l.key} of the overnight math workflow in ${WT} claims the report below. Check against the files: (1) ${l.dir}/preregistration.json was committed before the results (git log -- that path vs result mtimes); (2) every number in the report appears in a result file produced by the preregistered code (spot-recompute one with a python3 run under 5 minutes); (3) both controls ran and passed; (4) no overstatement (numeric search proves no upper bound; corollaries are not discoveries; upstream claims are not results). Write only ${l.dir}/verification.md.
REPORT: ${JSON.stringify(rep)}`, { label: `verify:${l.key}`, phase: 'Verify', schema: VERDICT }).then(v => ({ lane: l.key, report: rep, verification: v })),
)

const done = results.filter(r => r && r.report)
const skipped = lanes.filter(l => !done.some(d => d.lane === l.key)).map(l => l.key)
if (skipped.length) log(`lanes with no verified report (blocked, failed or dropped): ${skipped.join(', ')}`)

phase('Synthesize')
const summary = await agent(`Synthesis stage of the overnight openai_math lab in ${WT}. Verified lane reports: ${JSON.stringify(done)}. Lanes without a verified report: ${JSON.stringify(skipped)}.
1. Apply every verifier correction; drop claims from REJECTED lanes.
2. Append "## Night run ${args.date}" to ${WT}/docs/OPENAI_MATH_HYPOTHESES.md: one short subsection per lane (what ran, decision-rule outcome, controls, what it does and does not show; name lanes that produced nothing and why). Update per-hypothesis verdicts above only where the night changed them. No invented numbers.
3. Append each lane's lane_results.tsv rows to ${WT}/results/openai_math/hypotheses/results.tsv, renumbering the run column.
4. Extend ${WT}/scripts/openai_math/hypotheses/build_ledger.py with one claim per verified result (exact rational -> B exact_harness; numerics -> X numeric; reading -> X numeric or C argument); rerun it and keep the gate output.
5. Run python3 -m pytest ${WT}/tests/openai_math -q -p no:cacheprovider and python3 ${WT}/test_rigor_guard.py (report findings in new files only).
6. git add only files this workflow created or changed (docs, results/openai_math/hypotheses, scripts/openai_math, tests/openai_math, TODO.md), check git diff --cached --stat, commit "feat(openai_math): night ${args.date} lab results" ending with
${ATTR}
then git push (pull --rebase first if rejected). Plain commands only.
Return a morning summary under 300 words: per lane outcome and decision-rule verdict, what to do next, the commit sha and test results.`, { label: 'synthesize', phase: 'Synthesize' })

return { summary, lanes: done.map(d => ({ lane: d.lane, status: d.report.status, verdict: d.verification && d.verification.verdict, headline: d.report.headline })), skipped }
