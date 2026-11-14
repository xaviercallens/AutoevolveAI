import json, collections
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
OUT = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/discovery_journal_2026/"
R = {x["name"]: x for x in json.load(open(B + "all_repos.json"))}
E = json.load(open(B + "enriched.json"))
H = json.load(open(B + "honest.json"))

M, PH, CO, FU, GE, AI, NU, ED, IN, OT = ("mathematics", "physics", "cosmology", "fusion/plasma", "genetics/biology",
    "AI agents/methodology/verification", "numerics/software", "education", "infrastructure/devops", "personal/other")
SCI = {M, PH, CO, FU, GE, AI, NU}

C = {
"AutoevolveAI": (AI, "Verification-first harness (ANSE) for LLM-agent science: gates must be able to fail, claims must trace to artifacts; hosts the local-LLM/Lean/GPU tooling used by the other projects. README says an internal audit found 14 components reporting success without doing the work; not peer reviewed."),
"DarkMatterK3-Home.github.io": (CO, "Proposed distributed-computing project to test whether cosmic-web topology matches K3 moduli-space (Picard-Fuchs) structure; repo also holds the self-audits that gate-failed the laboratory-scale re-scope."),
"GWAYA-GwenLayaOpenModel": (AI, "Fail-closed verification gate for LLM-generated code (real compilers + sandboxed tests, AST stub auditing) with a paper and per-claim audits of its own numbers."),
"HiveMind": (AI, "Decentralised sparse-MoE training/inference over volunteer GPUs (Steam/BOINC/DiLoCo style). README states the legacy scientific-swarm paths are synthetic simulations and the only real-token evidence is a tiny CPU smoke test."),
"HiveMind-home.github.ui": (IN, "Near-empty placeholder repo for the HiveMind@home front end (1 commit)."),
"HiveMindatHome.github.io": (IN, "Static project site for HiveMind@home / La Ruche (compute-reciprocity charter, no money involved)."),
"xaviercallens.github.io": (IN, "Static site mirror of the HiveMind@home page."),
"Mirror-Map-Sieve": (M, "Exploratory preprint and pipeline studying one weight-5 Apery-like binomial sum S20(n) and its possible Calabi-Yau-operator interpretation; README says explicitly 'We do not claim a discovery'."),
"OpenAI-NSE-Epistemic-Audit": (PH, "Audit of the OpenAI Navier-Stokes/Euler Lean 4 blow-up proof read physically (Knudsen-number / continuum-assumption analysis) plus follow-up improvement plan; a later note withdraws earlier 'physical vacuity/censorship' wording."),
"OpenAI4F": (OT, "Stub repo (OpenSource AI for Finance), 2 commits."),
"OpenSourceAI4Finance-ControlCenter": (OT, "Empty placeholder repo."),
"OpenCycloInitiative": (GE, "Design documents for an open-source algae photobioreactor unit (cyclo-vortex hydrodynamics); documentation-level, 25 commits over two days."),
"OptimalEnergyAI": (M, "Applies the triangular-lattice universal-optimality result as a design idea for latent geometry in ML: Lean 4 spec, three CPU proof-of-concept experiments (hexagonal vs square grid, E8 vs Z^8 quantiser), plus business/IP planning docs. Private; no real-data PoC yet per README."),
"PersonaShield": (OT, "Private empty repo."),
"ReadyPlayerTogether": (OT, "Godot 4 VR/desktop metaverse game project; not scientific."),
"SocrateAI-CohnKumar-8D-Numeric": (M, "Empty repo (created 2026-10-11) reserved for 8D Cohn-Kumar numerics; no content."),
"SocrateAI-Dual-Scale-Agora-Lab": (CO, "Near-empty README-level repo describing the Dual-Scale Agora lab aim; no code."),
"SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal": (CO, "Stream 1 of the Dual-Scale Topological Universe Model: Lean 4 formalisation of arithmetic/lattice claims (Tier A kernel-checked, Tier B conjectural); several early headline claims were retracted in July 2026."),
"SocrateAI-Lean-Lib": (M, "Lean 4 library of 14 'domains' / 40+ modules claimed zero-sorry with an axiom-audit report; 'computational zero axioms' checks are theorems about specific numbers."),
"SocrateAI-Lean-Verification": (M, "Private Lean 4 library on tensor rank / asymptotic algebra / 'Kal Alien Mathematics' (high-level only)."),
"SocrateAI-Numeric-DualScale-Solver": (NU, "LeanFlow: pseudo-spectral 2D/3D Navier-Stokes solver with a dyadic shell sub-grid model, Rust crates + Lean 4 certificates, and a codebase audit that fixed tautological negative controls."),
"SocrateAI-Numeric-DualScale-Solver-Enterprise": (NU, "Private near-copy of the LeanFlow NS solver repository (high-level only)."),
"SocrateAI-Scientific-Agora": (AI, "Private multi-agent infrastructure/workspace of the SocrateAI Agora (large Lean+Rust+TeX tree); identical metrics to NewDiscoveries, probably the same repository under a former name."),
"SocrateAI-Scientific-Agora-AlphaEvolve-K3-T2": (CO, "Small prototype linking Python tensor optimisation to a Lean 4 JSON-RPC daemon for K3 x T^2 compactification search."),
"SocrateAI-Scientific-Agora-K3-DarkMatter": (CO, "Dual-scale topological universe model repo: Cooper s7/s10 operator identities proved in Lean, attempted K3/dark-matter links; README discloses that C1/C2 lattice numbers were retracted."),
"SocrateAI-Scientific-Agora-LeanFlow": (NU, "Private planning repository for a general MCP server for stiff solvers, TDA and Lean-checked data certificates; README: 'There is no server code yet'."),
"SocrateAI-Scientific-Agora-LeanMaster": (PH, "Lean 4 + Mathlib formalisation of T-duality, double field theory, K3 x T^2 lattices and Mathieu-moonshine arithmetic; README revised after an audit found over-claims ('first fully certified String Theory' withdrawn)."),
"SocrateAI-Scientific-Agora-Physique-Cinetique": (PH, "Exact-rational kinetic response-function engine with Lean proofs and comparison to published data; carries RETRACTIONS and two audits that found phantom simulation output and stub kernels."),
"SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic": (M, "Automated pipeline on K3xT^2, mock modular forms and hydrodynamic limits; huge Lean tree (4,471 .lean files, likely generated)."),
"SocrateAI-Scientific-AlienMathematics-Foundation": (M, "Retrospective of a June 2026 AI-driven 'alien mathematics' exploration: self-described failures, one claimed publishable result, lessons."),
"SocrateAI-Scientific-AutoEvolve-K3xT2": (CO, "AlphaEvolve-style evolutionary search for K3 x T^2 cosmology models with DESI BAO likelihood and nested sampling; docs say no definitive empirical discovery claimed and record a decisive NANOGrav refutation of one spectrum."),
"SocrateAI-Scientific-Communication": (AI, "Papers plus the reviews that examined them, organised by claim strength, including claims that did not survive."),
"SocrateAI-Scientific-CondensedMatterTheory": (PH, "AdS/CMT literature review (73 arXiv papers, RAG on AutoevolveAI's vector store) plus Lean offsets file with an explicit 'not proved' section."),
"SocrateAI-Scientific-DualScaleSimulator": (PH, "T-duality / string-dynamics simulator on K3 x T^2 with LeanFlow, TDA and Lean certification; no README."),
"SocrateAI-Scientific-Elenchus": (AI, "Private laboratory method + harness for AI-assisted science: cross-examine claims with tiers and refuting gates ('it removes false confidence, and that is all')."),
"SocrateAI-Scientific-FusionEnergy": (FU, "Empty repository (created 2026-10-19) reserved for fusion work; no content in the repo itself."),
"SocrateAI-Scientific-Genetic": (GE, "Lean 4 + Python/Rust hub for reverse transcription, chromatin remodelling and E8 dicodon ideas; AUDIT_2026-10-21 records a model-output (POLE P286R TMB) as not an observation and a refuted stage-removal model class."),
"SocrateAI-Scientific-LLeanM": (OT, "Empty repository."),
"SocrateAI-Scientific-LeanMaster-CoreStringTheoryFormalization": (PH, "Placeholder with one commit ('First string theory formalization')."),
"SocrateAI-Scientific-Mathesis": (AI, "Stream 0 shared notation, verification kernel and epistemic ledger for the other streams; audit pack warns non-vacuous witnessed theorems can still be the wrong statement."),
"SocrateAI-Scientific-MechanicaFluidorum": (M, "Staged verifier-in-the-loop programme on 3D Navier-Stokes regularity around 'Hypothesis U' (enstrophy control of truncated system); audit packet says a 'no' answer or killed track counts as success; Hypothesis U not proved."),
"SocrateAI-Scientific-Mensura": (M, "Tier-B exact-arithmetic and numerical companion to the Navier-Stokes Lean programme."),
"SocrateAI-Scientific-NewDiscoveries": (AI, "Private; same content/metrics as SocrateAI-Scientific-Agora (likely rename/duplicate)."),
"SocrateAI-Scientific-Poly-Algebraic-Calculus": (M, "Single-commit placeholder with only an abstract of a proposed 'Poly-Algebraic Calculus'."),
"SocrateAI-Scientific-QuantumComputing": (PH, "Quantum-hardware verification stream; README: 'prepared, not implemented', not peer reviewed."),
"SocrateAI-Scientific-QuantumFluids": (PH, "Machine-checked Lean 4 library of quantum-fluid structure (257 theorems) with a textbook tribute to Godfrin's work; RETRACTIONS.md and pre-registered criteria, one hypothesis refuted as written."),
"SocrateAI-Scientific-SectorCausalityTheory": (PH, "Criterion for when self-duality has physical consequences, with Lean formalisation, notebooks and an MCP server; tested on sixteen candidate systems; README has a 'what this theory does not claim' section."),
"SocrateAI-Scientific-TNN-UniversModel": (AI, "Thermodynamic/topological tensor-NN 'Univers Model' with real-data registry; a certified audit renamed overclaimed items (e.g. 'Live Sonic Horizon Simulator' became a 1D advection-diffusion proxy)."),
"SocrateAI-Wolfram-Hypergraph": (CO, "Computation-augmented-generation proof of concept for Wolfram-hypergraph dark-matter cosmology; brief says it does not claim to have discovered particles."),
"SocrateAI-thesisautoresearch": (AI, "Private autonomous research / DBA thesis copilot with Lean 4, Z3 and RAG tracks (high-level only)."),
"SuperGravity": (AI, "Zero-trust gateway and continuous self-improvement framework for agentic coding, built on AutoevolveAI/ANSE and Lean."),
"TIC4206066-Exoplanet-Verification": (CO, "Independent adversarial re-analysis (refutation gates with positive/negative controls) of a third party's TESS exoplanet candidate TIC 4206066 b, with Lean checks and a Zenodo data package."),
"Universcraft": (NU, "Rust procedural-engine (HoloEngine) for multi-scale world rendering; software project with physics-flavoured claims, not a research result."),
"VibeSpec": (OT, "Mockup-to-formal-spec-to-code pipeline for front-end generation; software tooling."),
"WebWebLightv4": (OT, "AI Studio web app scaffold."),
"amcp": (AI, "Agent Mesh Communication Protocol v1.5 enterprise edition: Java framework for mobile agents with LLM orchestration."),
"amcp-v1.5-opensource": (AI, "Open-source edition of the AMCP Java agent framework; status file reports 14 tests, 0 failures."),
"attentionmatter": (AI, "Private proof of concept for attention-inspired prompt token reduction (README claims 30-56% reduction; not independently checked here)."),
"liaspeaking": (ED, "Local voice-based educational companion app for children aged 8-13."),
"macmagicbrush": (OT, "Private local web UI for the MagicBrush image-editing model."),
"mopga": (OT, "Private manifesto note on planetary CO2 removal; no README."),
"nSymboCoder": (AI, "Private sub-1B neuro-symbolic code-model concept."),
"runux-ai-runtime": (IN, "Private proprietary RISC-V LLM runtime (KV-cache compression, integer attention); Rust + some Lean."),
"rust-linux-mini-kernel": (IN, "RunuX: no_std Rust kernel / Linux-subsystem reimplementation with Lean verification of parts, boots under QEMU and cloud VMs; build-status files record failed container builds."),
"rusty-Fenris-CMRR": (NU, "Small Rust crate relaxing 2D mesh nodes under a Yukawa repulsion using the local rusty-SUNDIALS CVODE; README status says early version."),
"rusty-SUNDIALS": (NU, "AI-assisted pure-Rust translation of SUNDIALS CVODE (ODE/stiff solver, ~500 MB tree) with Lean specification files; used as the numerics backbone for other projects."),
"rusty-leveldb": (NU, "Rust LevelDB port derived from a fork of dermesser/leveldb-rs; not science."),
"scikit-runux-tribute": (ED, "Tribute / teaching-style scikit-learn-like library dedicated to two professors."),
"scribemed": (OT, "Local medical-scribe AI assistant (French); not research."),
"symbioticfactory": (OT, "Open blueprint documents for a carbon-negative water-energy-food-carbon biorefinery; design-level, no experiments."),
"triangular-universal-optimality-lean": (M, "Kernel-checked Lean 4 corollaries of the upstream openai/math triangular-lattice universal-optimality theorem, opened for red-team review; LIMITATIONS.md says it is not a proof of the conjecture and uses a weaker optimality notion."),
"videomorph": (OT, "Private empty repo."),
"wazair": (OT, "Empty repo."),
"webwarcybergame": (OT, "Browser cyber-warfare strategy game."),
"xAuraOS": (AI, "Local-first 'cognitive operating substrate' (AuraOS): governed agent runtime with verifiers and capability leases; huge commit count (2,157), includes its own deep audit."),
"xPersonaShield": (OT, "Private GPU adversarial-perturbation tool to protect portraits from AI manipulation."),
"xaviercallens-SocrateAI-Scientific-Agora-K3-Quatum": (PH, "Architecture notes for quantum simulation of K3 x T^2 models; small, mostly TeX."),
"xaviercallens-SocrateAI-Scientific-FluidMecanism": (PH, "Empty placeholder (1 commit)."),
"xaviercallens-SocrateAI-Scientific-LeanMaster-StringTheoryFormalization": (PH, "Earlier public copy of the string-theory Lean formalisation; claims 'first machine-verified formalisation', a claim the main LeanMaster repo later withdrew."),
"xavuntu-AIRustLinux": (IN, "AI-native Rust Linux distribution concept built on the RunuX kernel; failed-build status files included."),
"xprivateremoteaccess": (OT, "Private SSH remote-access notes."),
"xvideomorph": (OT, "Private empty repo."),
}
missing = set(E) - set(C)
assert not missing, missing

rows = []
for n, e in sorted(E.items()):
    r = R[n]; dom, summ = C[n]
    private = r["visibility"] != "PUBLIC"
    rows.append(dict(
        name=n, visibility="PRIVATE" if private else "PUBLIC", created=r["createdAt"][:10], pushed=r["pushedAt"][:10],
        language=(r["primaryLanguage"] or {}).get("name"), disk_kb=r["diskUsage"], stars=r["stargazerCount"],
        description=None if private else r["description"], domain=dom, science_relevant=dom in SCI, summary=summ,
        lean=dict(lean_files=e.get("lean_files"), lakefile=bool(e.get("lakefile")), lean_toolchain=bool(e.get("lean_toolchain"))),
        rust=dict(cargo_tomls=len(e.get("cargo", [])), rs_files=e.get("rs_files"), sundials_mention=e.get("sundials_hit")),
        notebooks=e.get("notebooks"), data_files=e.get("data_files"), tex_files=e.get("tex_files"), py_files=e.get("py_files"),
        commits_since_2025_10_26=e.get("commits_last_year"), merged_prs=e.get("merged_prs"),
        tree_truncated=e.get("tree_truncated"),
        honesty_files=[] if private else e.get("honest_files", []),
        key_quotes={} if private else {p: h[:4] for p, h in H.get(n, {}).items() if h},
    ))

allr = list(R.values()); SINCE = "2025-10-26"
nonfork = [x for x in allr if not x["isFork"]]
counts = dict(
    total=len(allr), forks=sum(x["isFork"] for x in allr), non_forks=len(nonfork),
    private_total=sum(x["visibility"] != "PUBLIC" for x in allr),
    non_fork_outside_window=len(nonfork) - len(rows),
    kept=len(rows), kept_public=sum(r["visibility"] == "PUBLIC" for r in rows), kept_private=sum(r["visibility"] == "PRIVATE" for r in rows),
    science_relevant=sum(r["science_relevant"] for r in rows),
    by_domain=dict(collections.Counter(r["domain"] for r in rows).most_common()),
    window=f"{SINCE}..2026-10-26", criteria="created OR pushed on/after window start; isFork=false",
    empty_or_placeholder_repos=sum(1 for r in rows if (r["disk_kb"] or 0) <= 5 and (r["commits_since_2025_10_26"] or 0) <= 3),
)
LESSONS = [
("AutoevolveAI", "Every quantitative claim must be traceable to an artifact, and every gate must be able to fail. A gate that has never rejected anything is not a gate."),
("AutoevolveAI", "An internal audit found 14 components reporting success without doing the work (README, 'Measured status')."),
("SocrateAI-Scientific-Agora-LeanMaster", "Earlier README described the project as 'the first fully certified String Theory' ... An audit found that several headline claims held only for a much narrower Lean statement than the one described in prose (e.g. a bound over N presented as holding over R) ... one Lean theorem contained a real bug (a non-unique 'unique minimum' caused by Nat truncation, now fixed)."),
("SocrateAI-Scientific-Agora-K3-DarkMatter", "F6 disclosure (2026-07-24): C1/C2 lattice numbers retracted ... mislabeled them as z-space singular points, with hardcoded exponents ... The resulting ... numbers rho=4, T=18 ... are NOT valid and are retracted."),
("SocrateAI-DualScaleTopologicalUniverseModel-LeanProposal", "Two vacuous S1-03 'integrality' theorems discovered; s10/s18 partner series NOT integral (witnesses 17/2, 45/2 at n=2); s7 integrality 'PASS(7) only, general case = named open goal'."),
("DarkMatterK3-Home.github.io", "WP_A2_CIRCULARITY_AUDIT: 'Gate 0 of the Laboratory-Scale Re-Scope: FAIL ... a clean negative, reported with the same prominence as a positive.'"),
("DarkMatterK3-Home.github.io", "Lesson: every numeric constant must be verified against an external source; no hardcoding of raw values from unverified sources (LESSONS_LEARNED.md)."),
("Mirror-Map-Sieve", "'Status: exploratory preprint seeking expert review. We do not claim a discovery.' A fixed CY positional bias first failed (+10% ppl); a learnable bias passed (+8.1%) but the gain is learnability, not Calabi-Yau structure."),
("SocrateAI-Scientific-AlienMathematics-Foundation", "'An honest account of an AI-driven mathematical exploration, its failures, its one genuine contribution' - 6 independent computational methods failed to find any exact decomposition even at R = 48 where one is known to exist."),
("SocrateAI-Scientific-Agora-Physique-Cinetique", "Secondary audit found a 'fabricated phantom simulation ... not produced by any code in this repository' and a Bakry-Emery routine that built a SymPy Ricci tensor then discarded it and returned 2*d; roton kernel was a parameterised polynomial relabelled 'Algebraic Stubs'; status FAIL (Corrected)."),
("SocrateAI-Scientific-AutoEvolve-K3xT2", "'We do not yet claim definitive empirical discovery'; an unconstrained steep axion spectrum was decisively refuted by NANOGrav 15-yr (lnB = -51.58)."),
("SocrateAI-Scientific-Genetic", "AUDIT_2026-10-21: 'POLE P286R TMB 12500/9 mut/Mb is a model output, not an observation'; 'GAR.H15's mechanism for POLE P286R is refuted ... the whole stage-removal model class fails.'"),
("SocrateAI-Scientific-QuantumFluids", "Pre-registered criterion 'refutes the hypothesis as written'; two hypotheses refuted for one reason; some criteria 'failed through my own design' (README)."),
("SocrateAI-Scientific-Communication", "A claim of being the first Lean 4 formalization of this material 'was false, and it was refuted' (README, 'honest status of the current paper')."),
("SocrateAI-Scientific-TNN-UniversModel", "Certified audit renamed 'Live Sonic Horizon Simulator / analogous to Hawking white hole' to '1D Advection-Diffusion Proxy' and 'Hamiltonian drift' to 'L2-Norm Drift'."),
("OpenAI-NSE-Epistemic-Audit", "'A Physical Reading, Not a Physical Refutation'; later note withdraws 'physical vacuity' and 'censorship' wording; found an axiom declared in a file whose header claimed '0 custom axioms'."),
("triangular-universal-optimality-lean", "Open red-team review, 'Not peer reviewed'; LIMITATIONS: our UniversallyOptimal uses lower energy (liminf), weaker than CKMRV's definition; upstream does not claim the per-potential Cohn-Kumar form and neither do we."),
("SocrateAI-Scientific-MechanicaFluidorum", "'A \"no\" answer is a success, not a failure' - Definition of Done does not include proving Hypothesis U; a negative verdict or a killed track counts."),
("SocrateAI-Numeric-DualScale-Solver", "Tautological local literal negative controls replaced by an authoritative validation engine; LaTeX abstract inequality contradicting the exact bound was corrected."),
("GWAYA-GwenLayaOpenModel", "CLAIM_AUDIT: 'One bib entry is wrong ... One README badge is overstated'; recomputed numbers marked V (verified), VN (caveat) or X (mismatch)."),
("HiveMind", "'The legacy scientific swarm and domain-trainer paths are synthetic Gaussian-regression/game simulations, not language benchmarks. Their MSE is not perplexity ... [the smoke test] does not validate the broader hardware, WAN, frontier-capability or performance claims.'"),
("SocrateAI-Scientific-Agora-LeanFlow", "'Status (2026-09-19): planning repository. There is no server code yet.'"),
("SocrateAI-Scientific-QuantumComputing", "'Status (2026-10-11): prepared, not implemented. Not peer reviewed.'"),
("SocrateAI-Scientific-Mathesis", "A statement can be non-vacuous, carry witnesses in both polarities, and still be the wrong statement (AUDIT_PACK.md)."),
("SocrateAI-Scientific-Elenchus", "'The elenchus ... never establishes a positive truth. It removes false confidence, and that is all it does.'"),
("TIC4206066-Exoplanet-Verification", "Positive control recovered 100%; eclipsing-binary, secondary-occultation and centroid-shift negative controls all REFUTED as intended."),
]
json.dump(dict(counts=counts, repos=rows, lessons=[dict(repo=a, quote=b) for a, b in LESSONS]), open(OUT + "github_inventory.json", "w"), indent=1)

# markdown
L = []
L.append("# GitHub inventory: xaviercallens, window 2025-10-26 to 2026-10-26\n")
L.append("Source: `gh repo list` plus per-repo API calls, collected 2026-10-26. Read-only. Private repos are described at high level only (no code, no README quotes). Summaries are one-sentence readings of the README/description by the collector, not verified claims; see each repo's own caveats.\n")
L.append("## Counts\n")
for k in ["total", "forks", "non_forks", "private_total", "non_fork_outside_window", "kept", "kept_public", "kept_private", "science_relevant", "empty_or_placeholder_repos"]:
    L.append(f"- {k}: {counts[k]}")
L.append(f"- criteria: {counts['criteria']}\n")
L.append("Caveat: `pushedAt`/`createdAt` come from the GitHub API; commit counts are commits reachable from the default branch since 2025-10-26. Several repos were created before the window (e.g. amcp, 2025-09) but pushed within it. Duplicates: SocrateAI-Scientific-Agora and SocrateAI-Scientific-NewDiscoveries report identical metrics and are probably one repo under two names.\n")
L.append("## By domain\n")
doms = collections.OrderedDict()
for r in rows:
    doms.setdefault(r["domain"], []).append(r)
for d in sorted(doms, key=lambda d: -len(doms[d])):
    L.append(f"### {d} ({len(doms[d])})\n")
    L.append("| repo | vis | created | pushed | lang | commits/yr | merged PRs | .lean | .rs | nb | stars |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in doms[d]:
        L.append(f"| {r['name']} | {r['visibility']} | {r['created']} | {r['pushed']} | {r['language']} | {r['commits_since_2025_10_26']} | {r['merged_prs']} | {r['lean']['lean_files']} | {r['rust']['rs_files']} | {r['notebooks']} | {r['stars']} |")
    L.append("")
L.append("## Science-relevant repositories\n")
for r in sorted([r for r in rows if r["science_relevant"]], key=lambda r: (r["domain"], r["name"])):
    L.append(f"### {r['name']} [{r['visibility']}] ({r['domain']})\n")
    L.append(r["summary"] + "\n")
    L.append(f"- Created {r['created']}, last push {r['pushed']}; {r['commits_since_2025_10_26']} commits and {r['merged_prs']} merged PRs in window; disk {r['disk_kb']} KB; language {r['language']}.")
    lean = r["lean"]
    L.append(f"- Lean 4: {lean['lean_files']} .lean files, lakefile={'yes' if lean['lakefile'] else 'no'}, lean-toolchain={'yes' if lean['lean_toolchain'] else 'no'}. Rust: {r['rust']['rs_files']} .rs files, {r['rust']['cargo_tomls']} Cargo.toml (first 5 counted), SUNDIALS mention={'yes' if r['rust']['sundials_mention'] else 'no'}. Notebooks: {r['notebooks']}; data files (csv/json/etc): {r['data_files']}; TeX files: {r['tex_files']}.")
    if r["tree_truncated"]:
        L.append("- Note: GitHub truncated the file tree; file counts are lower bounds.")
    if r["honesty_files"]:
        L.append("- Honesty/audit/status files: " + ", ".join(f"`{p}`" for p in r["honesty_files"][:6]))
    for p, hs in r["key_quotes"].items():
        for h in hs[:3]:
            L.append(f"  - `{p}`: \"{h[:260]}\"")
    L.append("")
L.append("## Lessons learnt across repos (quotes)\n")
for a, b in LESSONS:
    L.append(f"- **{a}**: {b}")
L.append("\n## Non-science kept repositories (one line each)\n")
for r in sorted([r for r in rows if not r["science_relevant"]], key=lambda r: (r["domain"], r["name"])):
    L.append(f"- {r['name']} [{r['visibility']}] ({r['domain']}): {r['summary']}")
open(OUT + "github_inventory.md", "w").write("\n".join(L) + "\n")
print(json.dumps(counts, indent=1))
