# OpenAI's 26 October 2026 claims (ETH false; local smoothing → Kakeya/restriction): what is claimed, how faithful the Lean is, and what follows for us

**Author:** Xavier Callens (SocrateAI Lab). Drafted by an AI agent (Claude). No person has reviewed it.
**Status:** read-only analysis study. Nothing was committed, pushed or published. The only file written in the
repository is this one; scratch work is in `/tmp/oaiclaim/` (not tracked).
**Owner's request (verbatim):** "Analyze the last claim and see what follow-up it could bring to us with the current
work and progress."

**Rules kept.**
- A source is **read** only if opened in this session; section 9 is the reading log with one quoted sentence per
  source. Search snippets and relayed coverage are marked **secondary** or **not read**.
- No sentence here says that any claim is true or false, or that we "verified" anything of OpenAI's.
- All priors, values and feasibilities are our estimates, not measurements. Numerical scratch work is Tier X.
- The repository is public: only short quotations of third-party texts appear below; no full texts are copied.

---

## 0. Which claim is "the last claim"

- **The Reddit thread was never read** (Reddit blocks automated access; see `NEWS_STUDY_2026-10-27.md` §1).
- The News Study guessed, at **about 0.55**, that the thread was about OpenAI's **26 October 2026 release** in
  `github.com/openai/math` (merge commit `7ef5c0c`, PR #3): (1) the manuscript *The Exponential Time Hypothesis is
  False* with a Lean formalisation and Comparator challenge `SubexponentialSAT`, and (2) *Local smoothing for the
  Euclidean wave equation*, with Kakeya, Bochner–Riesz, Stein square-function and spherical-restriction consequences
  and Comparator challenge `LocalSmoothing`.
- **New evidence since that guess:** the owner shared an OpenAI page, *Building scientific understanding with academic
  communities* (`openai.com/fr-FR/index/building-scientific-understanding-with-academic-communities/`). Its text was
  **not read** (HTTP 403, section 1). The owner's own pointer outweighs our 0.55 guess: "the last claim" is very
  probably that page's announcement, which (per secondary coverage, section 1) is the same 26 October package plus a
  third, unreleased physics result and a publication policy. We do not put a new number on it.
- **Other candidate claims** (not analysed here):
  - the **unreleased QFT / Yang–Mills-type claim** in the press (section 6);
  - the **6–7 October release** of the manuscript corpus (722 manuscripts at the time; the README now says "721
    manuscripts organized into 373 families", `README.md:16`), on which our LL §16–18, D0/D1 and A2 work already
    rests.

---

## 1. The shared OpenAI page: fetch failed; a partial text was pasted by the owner

- **Fetch failed.** Both the fr-FR and the English URL returned HTTP 403 to automated fetches (this session's
  coordinator and the News Study).
- **Partial primary text.** The owner later pasted three paragraphs of the French page (section 1b). The paste stops
  mid-sentence ("Nos") in the physics paragraph. Everything after that point is **not read**, and that probably includes
  anything on publication, credit and peer review.
- **What that limits.** We still cannot say what OpenAI commits to on peer review, credit, replication or access to
  artifacts, or whether independent auditors are invited. Statements below about those topics are secondary.
- **Secondary coverage, relayed to this study by another agent (none of it read by us; partly search-summary
  only).** Gizmodo (M. Pearl, 26 Oct), DEV Community (A. Farhat, 27 Oct), MLQ.ai (27 Oct). Reported, not checked:
  - the page's current title may be *Working with academic communities to build scientific understanding* (same slug);
  - **three** results: ETH disproved; Kakeya in all dimensions via local smoothing; rigorous existence of certain 4D
    interacting quantum field theories, whose AI artifacts are **withheld** while the physics group writes up;
  - model texts are to be treated as "raw research data", with outside **"shepherd"** experts (ETH: Impagliazzo,
    Paturi, Williams; physics: Gross, Jaffe, Klebanov, Nekrasov) turning outputs into human knowledge;
  - four stated principles: transparency, no academic credit sought by OpenAI, recognition of contributors,
    independence of external researchers;
  - timeline: ETH found 16 Oct and formalised in Lean 17 Oct; local smoothing proof 18 Oct, Lean 19 Oct;
  - MLQ: the Lean files check the **encoded statements**, not the correctness of the papers;
  - an independent tracker ("State of Proof") lists the ETH manuscript as unverified with review not started;
  - Gizmodo: critics found the **Navier–Stokes** Lean statement weaker than the published claim (section 7.1 below);
  - a Yang–Mills Lean formalisation of 16 Oct reportedly does not address the mass gap. **We found no Yang–Mills or
    QFT challenge in `openai/math` at `7ef5c0c`** (`ls lean/ComparatorChallenges | grep -iE "yang|mills|gauge|qft"`
    returns nothing; the only "quantum" hit is the unrelated `ExactQuantumFactoring`), so that formalisation, if it
    exists, is elsewhere.
- **Text in the repository that bears on an academic-communities programme (read, primary):**
  - `README.md:12`: "In our view, these manuscripts are best understood as a form of raw research data, rather than
    polished academic papers. We defer to the math community completely on matters of credit, precedence, and
    concurrent work."
  - `README.md:10`: "We are also exploring community-hosted repositories for these materials."
  - `history.md:12`: "An independent working group of computer scientists led by Russell Impagliazzo, Ramamohan
    Paturi, and Ryan Williams will examine and explain the proof. At the group’s request, we are making the materials
    public immediately so others can examine them as well."
  - `lean/formalization.yaml:1827-1828`: `review:` / `status: unchecked` (the catalogue's own review field).
  - **Pull-request conversations are locked by design:** PR #2 is titled "Lock pull request conversations when
    opened", and PR #3 has `locked: true` with 0 comments (GitHub API). In-repo public feedback is therefore closed;
    any audit we make would have to be reported elsewhere.
- **"Transparency" and "independence of external researchers"** (secondary) suggest that independent artifact audits
  may be welcome. **That must be confirmed from the page text**, which the owner may paste.

**Questions to answer from the page text (for a follow-up once the owner pastes it).**
1. Peer review: does OpenAI commit to journal submission or refereeing by people? Who decides when a result counts as
   accepted, the shepherds or OpenAI?
2. Credit: what exactly does "no academic credit" mean (authorship, citations, prizes)? How are "contributors"
   recognised, and does that include outside auditors?
3. Shepherds: are their reports public, on what timeline, and can they be negative? Are they paid or bound by an
   agreement, and with what conflict-of-interest terms?
4. Independent replication: does the page invite independent audits of the Lean artifacts or the manuscripts? Through
   which channel, given that PR conversations are locked?
5. Artifacts and data: what is released and when (model outputs, reasoning traces, Lean, Comparator logs)? Under
   which licence (the repository is Apache-2.0)? Why is the QFT material withheld, and until when?
6. Withdrawals and corrections: is the `history.md` withdrawal practice (October 7) a formal policy?
7. Does the page say anything about the Lean statements being **statement-checked only**, not proof-of-paper checks?
8. Does it say whether OpenAI itself ran Comparator on these challenges, with which kernel(s), and where the verdict
   logs are?

---

## 1b. The page's own wording (partial, pasted by the owner)

**Source status.** This is the owner's paste of the French page. It is primary text, but partial: it is cut off at "Nos"
in the physics paragraph. We cannot confirm that it is verbatim or complete up to that point. The English translations
are ours. The secondary coverage in section 1 is kept separate and is not merged into this section.

**(a) Local smoothing and Kakeya.**
> « Le lissage local et la conjecture de Kakeya. Le résultat en mathématiques concerne l'analyse harmonique. En 1991,
> Sogge a proposé la conjecture du lissage local, qui porte sur le comportement des ondes lorsqu'elles se focalisent.
> En particulier, la conjecture affirme que la focalisation la plus extrême ne peut être que de courte durée. Le degré
> de focalisation à un instant typique choisi au hasard est toujours bien inférieur à ce qui peut se produire à
> l'instant le plus défavorable. C'est un schéma courant en mathématiques : ce qui peut se produire dans le pire des cas
> est plus extrême que ce que l'on observe en moyenne. En raison du caractère fondamental du phénomène conjecturé, ses
> implications s'étendent à de nombreux domaines de l'analyse mathématique. Il implique par exemple la conjecture de
> Kakeya et la conjecture de restriction de Stein. »

*Translation:* "Local smoothing and the Kakeya conjecture. The mathematics result concerns harmonic analysis. In 1991,
Sogge proposed the local smoothing conjecture, which concerns the behaviour of waves as they focus. In particular, the
conjecture asserts that the most extreme focusing can only be short-lived. The degree of focusing at a typical,
randomly chosen time is always much smaller than what can happen at the worst time. This is a common pattern in
mathematics: what can happen in the worst case is more extreme than what is observed on average. Because the
conjectured phenomenon is so fundamental, its implications reach many areas of mathematical analysis. It implies, for
example, the Kakeya conjecture and Stein's restriction conjecture."

**(b) ETH.**
> « L'hypothèse du temps exponentiel est fausse. La collaboration en informatique s'attachera à comprendre et à
> expliquer un résultat concernant l'hypothèse du temps exponentiel (ETH), une conjecture de longue date sur la
> complexité du problème de satisfaisabilité des formules booléennes, étroitement lié au problème P contre NP. L'ETH a
> été largement considérée comme vraie et utilisée dans des centaines d'articles pour établir des résultats
> conditionnels de difficulté de calcul dans des domaines très variés, dont la théorie des graphes, la biologie
> computationnelle, les bases de données et la géométrie algorithmique. De manière surprenante, notre système a
> récemment démontré que l'ETH est fausse, un résultat qui a ensuite été vérifié en Lean. La réfutation de l'ETH relance
> la question de l'accélération possible de ces tâches et pourrait guider la recherche de meilleurs algorithmes. Trouver
> de tels algorithmes et transformer les avancées théoriques en améliorations pratiques nécessitera d'importantes
> recherches supplémentaires. Ces travaux seront vérifiés et encadrés par un groupe dirigé par Russell Impagliazzo (UC
> San Diego), Ramamohan Paturi (UC San Diego) et Ryan Williams (MIT). Tous trois sont experts en conception
> d'algorithmes et en théorie de la complexité. »

*Translation:* "The Exponential Time Hypothesis is false. The computer-science collaboration will work to understand
and explain a result about the Exponential Time Hypothesis (ETH), a long-standing conjecture about the complexity of
the Boolean satisfiability problem, closely related to the P versus NP problem. ETH has been widely regarded as true
and used in hundreds of papers to establish conditional hardness results in very varied fields, including graph theory,
computational biology, databases and computational geometry. Surprisingly, our system recently proved that ETH is
false, a result that was then verified in Lean. The refutation of ETH reopens the question of whether these tasks can be
sped up and could guide the search for better algorithms. Finding such algorithms and turning theoretical advances into
practical improvements will require substantial further research. This work will be verified and supervised by a group
led by Russell Impagliazzo (UC San Diego), Ramamohan Paturi (UC San Diego) and Ryan Williams (MIT). All three are experts
in algorithm design and complexity theory."

**(c) QCD (truncated).**
> « Existence de la chromodynamique quantique et complétions du modèle standard. La collaboration en physique
> s'attachera à comprendre et à expliquer un résultat qui fournit une preuve d'existence mathématiquement rigoureuse de
> certaines théories quantiques des champs en interaction contenant des champs de jauge et des fermions en quatre
> dimensions, dont la chromodynamique quantique (QCD) et une complétion unifiée du modèle standard de la physique des
> particules. Nos [coupé] »

*Translation:* "Existence of quantum chromodynamics and completions of the Standard Model. The physics collaboration
will work to understand and explain a result that provides a mathematically rigorous existence proof of certain
interacting quantum field theories containing gauge fields and fermions in four dimensions, including quantum
chromodynamics (QCD) and a unified completion of the Standard Model of particle physics. Our [cut off]"

**(d) Physics, continuation (pasted separately by the owner).** The paste starts mid-sentence, so the text between
« Nos » and the passage below is **missing**.
> « [...] communication avec l'un ou plusieurs de ses membres concernant ces travaux soit adressée à l'adresse e-mail
> suivante : YANGMILLS4D@gmail.com. Nos modèles ont produit une preuve en langage naturel de l'existence de la théorie
> de Yang-Mills le 9 septembre 2026, puis une preuve pour la QCD le 18 septembre 2026. Compte tenu de la longueur et de
> la complexité des travaux, nous avons reporté leur publication jusqu'à l'achèvement de la formalisation en Lean. Nous
> avons achevé la formalisation de l'existence de la théorie de Yang-Mills le 16 octobre 2026, ce qui nous a conduits à
> mettre en place la collaboration décrite ici. Nous espérons que ces résultats marquent le début d'une transition qui
> fera de la théorie quantique des champs, le cadre le plus important de la physique théorique moderne, un domaine
> mathématiquement rigoureux. Nous sommes enthousiastes à l'idée de fournir des ressources pour que la communauté
> scientifique progresse vers cet objectif. »

*Translation:* "[...] communication with one or more of its members about this work be addressed to the following
e-mail address: YANGMILLS4D@gmail.com. Our models produced a natural-language proof of the existence of Yang–Mills
theory on 9 September 2026, then a proof for QCD on 18 September 2026. Given the length and complexity of the work, we
postponed its publication until the Lean formalisation was complete. We completed the formalisation of the existence
of Yang–Mills theory on 16 October 2026, which led us to set up the collaboration described here. We hope these
results mark the start of a transition that will make quantum field theory, the most important framework of modern
theoretical physics, a mathematically rigorous field. We are excited to provide resources so that the scientific
community can progress towards this goal."

**Recorded from (d), and nothing more:**
- **Contact.** The page publishes `YANGMILLS4D@gmail.com` as the address for communication with one or more members of
  the physics group about this work. We record it and have sent nothing. Writing to it is not part of any follow-up
  below. It is an option only for the owner to decide, for example after artifacts are released. The address is a
  free-mail account, not an institutional domain; we note that without drawing any conclusion from it.
- **Timeline, as the page states it:**
  - 9 Sept 2026: a natural-language proof of Yang–Mills existence;
  - 18 Sept 2026: a natural-language proof for QCD;
  - publication deferred until the Lean formalisation was complete;
  - 16 Oct 2026: the Lean formalisation of **Yang–Mills existence** was completed, which led to the collaboration.
  - **In the available text no Lean completion is stated for QCD or for the Standard-Model completion.** Paragraph (c)
    claims an existence proof that covers both. Paragraph (d) says only the Yang–Mills formalisation is finished.
- **"Existence of Yang–Mills theory" versus the Clay problem.** The Clay Yang–Mills problem asks for existence of a
  quantum Yang–Mills theory on ℝ⁴ for every compact simple gauge group **and** a mass gap Δ > 0. **The available
  primary text does not mention a mass gap.** MLQ (secondary, relayed, not read by us, unconfirmed from the page) says
  the Yang–Mills claim does not address the mass gap. Once artifacts exist, a reader must check:
  - which axioms define "existence" (Wightman, Osterwalder–Schrader, or a lattice-continuum construction);
  - which gauge groups are covered;
  - whether the theory is non-trivial, meaning not Gaussian or free;
  - for the Lean, how "a QFT" is encoded: this is where a definition-level weakening would hide (section 6);
  - whether any mass-gap statement is made.
  Until then, any wording such as "Millennium problem solved" would be an over-claim. Nothing in the page as we have
  it supports it.
- **Stated aim and community resources.** The page hopes to make QFT "a mathematically rigorous field" and to "provide
  resources" to the community. The available text does not say what resources these are (artifacts, compute, funding,
  access), on what terms, or when. If they include the Lean formalisation, the fidelity checks of section 4 and
  GATE-1 (F3) are what an independent lab could usefully contribute. That too waits for release.
- **Still unknown after (d):**
  - the start of the sentence before the contact address (presumably the group's members, whom secondary coverage
    names as Gross, Jaffe, Klebanov and Nekrasov);
  - credit;
  - data and artifact release, including whether and when the Yang–Mills Lean formalisation will be published (we
    found none in `openai/math`);
  - the publication process;
  - peer-review commitments.

### What the page says, and what the available text leaves unsaid

| Page wording | What it says | What it does not say (in the available text) |
|---|---|---|
| ETH: « notre système a récemment démontré que l'ETH est fausse » | OpenAI asserts, in its own voice, that its system **proved** ETH false. | Nothing qualifies it: no "claimed", no "pending review". |
| « un résultat qui a ensuite été vérifié en Lean » | A Lean verification took place, after the proof. | **What** was verified: the repository's Lean statement is the weaker ρ(n) bound, not the manuscript's main bound (section 2.2), though it suffices for ETH. **By whom:** not stated; presumably OpenAI itself. **With which checker:** not stated (Lean kernel? Comparator? nanoda?). **Where the logs are:** not stated, and we found none in the repo (section 4.4). Lean verification covers the **statement as encoded** (section 4), not the press wording. |
| « Ces travaux seront vérifiés et encadrés par un groupe dirigé par … » | Human verification is **future tense**: it is pending, not done. This agrees with `history.md:12` ("will examine and explain"). | When, how, whether the group's findings will be public, and whether they can be negative. |
| « La collaboration … s'attachera à comprendre et à expliquer » (both collaborations) | Each collaboration's stated role is to **understand and explain**, which reads as exposition rather than adjudication. | Whether "verified" by the group and "understand and explain" are the same mandate. The ETH paragraph uses both phrasings. |
| « étroitement lié au problème P contre NP » | ETH is related to P vs NP. | That refuting ETH does **not** settle P vs NP. The manuscript says so itself (`main_full_version.tex:149`); the page, as far as we have it, does not. |
| « Trouver de tels algorithmes et transformer les avancées théoriques en améliorations pratiques nécessitera d'importantes recherches supplémentaires » | OpenAI says itself that there is no practical improvement yet. | How large the gap is. Our Tier-X scratch work (section 4.3) puts the crossover with brute force at n > 10^2390 for A = 1. |
| Local smoothing: « Il implique par exemple la conjecture de Kakeya et la conjecture de restriction de Stein » | The conjecture implies Kakeya and restriction. | That **a proof** was obtained. The available paragraph describes the conjecture and its implications, not a result. It does not mention Lean, and it does not say "throughout the interior of the range". The repo's Lean covers only the interior (section 3.2, L5), not the endpoint restriction conjecture. |
| QCD: « une preuve d'existence mathématiquement rigoureuse … dont la chromodynamique quantique (QCD) et une complétion unifiée du modèle standard » | An existence proof for interacting 4D gauge + fermion QFTs, including QCD. | In which axiomatic framework (Wightman, Osterwalder–Schrader, or other). Whether a mass gap is claimed: our reading is that existence alone would not be the full Clay Yang–Mills problem, which also asks for a mass gap. Part (d) adds only that Lean was completed for **Yang–Mills existence**, on 16 Oct. No Lean is stated for QCD or the Standard-Model completion, and none is public in `openai/math`. Nothing is said on release dates. |

### Effect on the analysis

- **Fidelity (section 4):** unchanged in substance. The page's « vérifié en Lean » is the strongest wording we have
  seen. It makes section 4.4 more important: the repository does not yet show *who ran which check*, so the accurate
  phrasing stays "OpenAI states it was verified in Lean; we have not seen a verdict log and have not run one."
- **Plausibility (section 5):** the page adds no evidence. It adds a stronger **assertion**: "proved" in OpenAI's own
  voice, with human verification explicitly in the future. Our assessment is unchanged and we take no position on
  truth.
- **Follow-ups (section 7):**
  - F2 (the explainer) gains value. The page's unqualified « démontré » next to « seront vérifiés » is exactly the
    distinction the explainer is about: claim, Lean statement, kernel check, human review. We raise F2's V from 2 to
    2.5. Its new score, 0.45 × 2.5 × 0.85 = 0.956, is level with F1 (0.950) within calibration error.
  - F5 (the SAT replay) gains no value. The page names the group that "will verify", so an outside replay is even
    more clearly their territory. Its over-claim risk stays very high and it stays deferred.
  - Nothing changes for the QCD claim: there is still no artifact.

### Questions still open because the text is cut off (for the owner to paste the rest)

1. **Publication process:** will the results go to journals or arXiv, under whose names, and on what schedule?
2. **Credit:** does the page repeat the README's "we defer to the math community completely on matters of credit"? Who
   is credited: the shepherds, earlier authors, auditors?
3. **Data and artifact release:** which artifacts (manuscripts, Lean, Comparator logs, reasoning traces) are released
   for each result? When will the QCD material be released, and under which licence?
4. **Peer-review commitments:** is any refereeing by people promised? Will the shepherd groups' reports be public,
   including negative ones? What does « vérifiés » mean for the group, compared with « comprendre et expliquer »?
5. **The Lean verification:** who ran it, with which tools, and where is the log? Does the page say what the Lean
   statement covers?
6. **Independence:** does the rest of the page invite independent audits, through which channel (given that PR
   conversations are locked), and with what terms?
7. **The gap between « Nos » and « communication avec … ses membres »:** the shepherds' names (secondary coverage:
   Gross, Jaffe, Klebanov, Nekrasov), the framework of the existence proof, and any mass-gap statement. Part (d)
   supplies the timeline and the contact address, but not these.
8. **Everything after the last pasted sentence:** any credit, publication, peer-review or release commitments.

---

## 2. What is claimed: ETH

### 2.1 In plain words

- **The Exponential Time Hypothesis (ETH)** (Impagliazzo–Paturi): there is a δ > 0 such that 3-SAT on n variables
  cannot be decided in time 2^{δn}·poly(input) — equivalently, no 2^{o(n)}-time algorithm. The manuscript's abstract
  phrases it as "deciding $3$-SAT on $n$ variables requires $2^{\Omega(n)}$ time in the worst case"
  (`build/main_full_version.tex:36-38`).
- **The claim** (abstract and Theorem 1.1, `main_full_version.tex:30-39, 73-87`): for every fixed k ≥ 2, a
  **deterministic** algorithm **counts** the satisfying assignments of a k-CNF with n variables and m clauses in time
  (n+m)^{O_k(1)}·2^{O_k(n log log n/√log n)} and (n+m)^{O_k(1)} bits of space; for m ≤ Dn, 2^{O(n/√log n)}.
- **Consequences claimed by the manuscript** (not checked by us): refutation of ETH, SETH, Gap-ETH, NSETH and #ETH
  (`:252-324`); subexponential counting of independent sets, q-colourings and perfect matchings (Corollary,
  `:156-176`); a circuit lower bound C_L(n) > c·n√log n for infinitely many n for some L ∈ E^NP (`:178-191`); a
  Max-k-SAT approximation corollary that cites another OpenAI manuscript claiming the **Unique Games Theorem**
  (`:103-108`, family 102 in `CONTENTS.md`) — that corollary therefore rests on a second unrefereed claim; the main
  theorem does not.
- **What it would not imply**, in the manuscript's own words: "runtime bounds of the form $2^{o(n)}$ do not transfer
  under general polynomial-time reductions ... so our result does not imply that general NP problems admit
  subexponential time algorithms" (`:149`). It is not P = NP.
- **The sparsification lemma** (Impagliazzo–Paturi–Zane) is a **tool** in the proof (`:459-465`, `:3543`), not
  something refuted. Fine-grained complexity: many lower bounds are stated "assuming ETH" (for example 2^{o(n)} lower
  bounds for 3-Colouring or Vertex Cover through linear-size reductions, and ETH-tight parameterised bounds). If the
  claim holds, those bounds lose their stated hypothesis; our reading (not a check) is that bounds with weaker
  hypotheses of the form "no 2^{n/polylog n} algorithm" would be the natural replacement. Experts, not us, should say
  which conditional results survive.

### 2.2 What the Lean theorem states (`lean/ComparatorChallenges/SubexponentialSAT.lean`, read in full)

`theorem exact_count_and_sat (k : ℕ) (hk : 2 ≤ k)` (lines 194-218) states: for each k ≥ 2 there exist **one** machine
(a `PrimitiveMachine`), two of its tapes (count, answer), reals C, A, S > 0 and naturals d, e > 0 such that **for every
n and every CNF F over `Fin n` with all clauses of size ≤ k**, the machine started on `encodeCNF F`:
- reaches, after exactly `time` steps, a halted configuration whose state is `Sum.inl (decide (0 < count F))`, whose
  count tape is exactly the binary word of the number of satisfying assignments, and whose answer tape is the SAT bit;
- with `time ≤ C·(L+1)^d·2^{A·ρ(n)}`, where L = bit length of the encoding and
  **ρ(n) = n·(ln ln(n+16))²/√ln(n+16)** (lines 132-139);
- and at **every prefix** of the run, the total number of visited cells over all tapes is ≤ S·(L+1)^e (lines 212-217).

The proof file in the challenge is `sorry` (line 218): the challenge is the statement; OpenAI's solution is
`OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean:74`, which instantiates the machine as an explicit compiled
program (`GuardedCompiler.primitive program` with 1220 tapes, `Final.lean:110-113`), so the machine is a concrete
object, not a bare existence claim.

**Definitions versus proof.** Everything in the challenge file is a definition (SAT syntax and semantics at lines
17-47, encoding at 55-79, the machine model at 87-124, the runtime scale at 132-139, the space monitor at 147-189)
except the one theorem. Comparator's config (`SubexponentialSAT.json`) lists `"definition_names": []`, so **no
definition is a hole**: the solution must reproduce every one of these definitions identically. This is the opposite of
the 9 hole challenges flagged in D1 (memory note: "Comparator skips definition-hole bodies"); that gap does **not**
apply here. The same holds for `LocalSmoothing.json`, which has no `definition_names` key at all.

**What the Lean proves is weaker than the manuscript's main bound.** The Lean exponent is the "weaker exponent"
ρ(n) of `main_full_version.tex:89-96`, not the theorem's n log log n/√log n; `lean/docs/378.md` says so: "the October
25 manuscript gives the sharper time bound". For ETH this difference does not matter: ρ(n) = o(n) already.

---

## 3. What is claimed: local smoothing, Kakeya, restriction

### 3.1 In plain words

- **Sogge's local smoothing conjecture**: averaging the half-wave e^{it√−Δ}f over t ∈ [1,2] gains regularity over the
  fixed-time estimate: ‖e^{it√−Δ}f‖_{L^p(ℝⁿ×[1,2])} ≲ ‖f‖_{W^{s,p}} for every s > max(0, (n−1)/2 − n/p), 2 ≤ p < ∞.
- **Claim** (abstract, `build/paper.tex:56-64`): "We prove Sogge's local smoothing conjecture for the Euclidean wave
  equation in every spatial dimension at least two", hence Bochner–Riesz, Stein's square function, restriction for the
  sphere, paraboloid and cone "throughout the interior of the conjectured range", and the Kakeya and Nikodym maximal
  conjectures, so "every Euclidean Kakeya set has full Hausdorff dimension".
- **Prior state of the art, as the manuscript itself reports it** (not from memory): Guth–Wang–Zhang reached p = 4 in
  the plane; in ℝ³, Gan–He–Li–Wu gave the full gain up to ε-loss for p ≥ 10/3 (`sections/history.tex:25-44`); Kakeya
  full dimension was known for n = 2 (Davies) and n = 3 (Wang–Zahl) (`sections/kakeya.tex:38-41`). So the new content
  is n ≥ 3 for local smoothing in the full range, and n ≥ 4 for Kakeya dimension.
- **If right:** Kakeya, Bochner–Riesz and Stein's restriction conjecture (interior) are among the central open problems
  of harmonic analysis; a proof in all dimensions would be a major result. The endpoint restriction conjecture is
  **not** claimed (section 3.2).

### 3.2 What the Lean statements say (`lean/ComparatorChallenges/LocalSmoothing.lean`, read in full)

Six theorems, all ending in `sorry` in the challenge, all with permitted axioms {propext, Quot.sound,
Classical.choice}, no definition holes ("Standalone Comparator reference: six independent targets, no definition
holes", line 6):

| Theorem (line) | Statement in plain words | Range |
|---|---|---|
| `euclidean_local_smoothing` (84-96) | For n ≥ 2, 2 ≤ p, and ε > 0 (or p = 2, ε = 0), ∃C: for every **Schwartz** f, the half-wave on ℝⁿ×[1,2] is in L^p with norm ≤ C·‖J^{s}f‖_p, s = max(0,(n−1)/2 − n/p) + ε | all finite p ≥ 2, ε-loss |
| `bochner_riesz` (99-106) | uniform-in-R L^p bounds for the Bochner–Riesz means of order δ > max(n·|1/p − 1/2| − 1/2, 0), 1 ≤ p ≤ ∞ | strict |
| `spherical_restriction` (109-117) | extension operator L^a(sphere) → L^b(ℝⁿ) for b > 2n/(n−1) and b > (n+1)/(n−1)·a′ | **strict, interior only** |
| `kakeya_maximal` (120-126) | ‖f*_δ‖_{L^n(sphere)} ≤ C_ε δ^{−ε}‖f‖_{L^n}, 0 < δ ≤ 1 | every ε > 0 |
| `kakeya` (129-131) | every set containing a unit segment in every direction has `dimH = n`; no measurability assumed | full |
| `stein_square` (134-141) | Stein's square function bounded on L^p for α > max(1/2, n(1/2 − 1/p)), p ≥ 2 | strict |

The manuscript's Theorem 1 (`sections/introduction.tex:16-23`) matches the first row. The Lean statements cover what
`history.md:11` announces ("throughout the interior of the conjectured range") and nothing at the endpoints. The
Nikodym, paraboloid, cone and Schrödinger consequences claimed in the abstract have **no** Comparator target. The
sharper critical annular estimate (Theorem 1.2, `introduction.tex:97-104`) is a proof step, not a Comparator target.

---

## 4. Fidelity analysis (our speciality)

All readings below are by an AI agent: **Tier C judgements, not certifications.** Each row says what a reader or expert
must still check.

### 4.1 SubexponentialSAT

| # | Where | Possible gap | Our reading | What an expert must check |
|---|---|---|---|---|
| S1 | `SubexponentialSAT.lean:92-99, 107-119` | Non-standard machine model | `PrimitiveMachine`: finitely many tapes over {blank, 0, 1} (`Option Bool`), finite control, each state scans **one** tape and performs one move or one write. This is a *restricted* multitape Turing machine. A restriction makes an **upper** bound harder, not easier; any RAM simulates it with constant overhead, so a time bound here transfers to standard models. The transition is a finite table, so no oracle power can hide in it. | That Mathlib's `Turing.Tape` / `Turing.TM0.Stmt` at Mathlib `d13f23b7` have the expected semantics (move left/right, write, `Tape.mk₁` = head at first cell). |
| S2 | `:194-199` | Uniformity / quantifier order | ∀k ∃machine ∃constants ∀n ∀F: **one machine per k**, constants independent of n and F. Not a non-uniform family. | Nothing further; this is what ETH needs (k = 3). |
| S3 | `:55, :64-77` | SAT encoding | n and every literal code are written in **unary** (`encodeNat n = replicate n true ++ [false]`), so L = O(n + m·k·n). This is polynomial in (n, m), so the (L+1)^d factor is still poly(n, m); it is not a trivialisation. Clauses and formulas are `Finset`s (no duplicates) and the encoding is canonical (sorted, `:67-71`). | That restricting to canonical inputs is harmless (canonicalisation is polynomial), and that the unary blow-up is accepted as "reasonable encoding". |
| S4 | `:199, :210-211` | What n counts | n is the **declared** number of variables (`Fin n`), the ETH parameter; L is separate. | Nothing further. |
| S5 | `:132-139` | "Subexponential" meaning, junk values | ρ(n) = n(ln ln(n+16))²/√ln(n+16) = o(n). ln(n+16) ≥ 2 (proved in the solution, `SqrtLog/StatementScale.lean:24`), so no log/sqrt/division junk values. | That ρ is o(n) (elementary). See 4.3: the bound is asymptotic only. |
| S6 | `:203-209` | Output correctness | Count tape equals exactly the binary count; answer tape and halting state equal the SAT bit. Conjuncts at `:208-209` (`toNat (countWord …) = count`, length ≤ n+1) are true facts about `countWord` and add no content. | Nothing further; the content is in `:201-207`. |
| S7 | `:212-217, :155-159, :188-189` | Space | Visited cells summed over all tapes, at **every prefix**, including the input tape; poly(L). | That `LocatedCfg.monitor` (`:166-182`) tracks head positions correctly (it is part of the statement, so a wrong monitor would change the meaning). |
| S8 | `SubexponentialSAT.json` | Definition holes | `"definition_names": []`: none. The D1 hole-body gap does not apply. | — |
| S9 | `SubexponentialSAT.json` | Axioms | `permitted_axioms` = {propext, Quot.sound, Classical.choice}: exactly our whitelist. | That a Comparator verdict exists (section 4.4). |
| S10 | `SubexponentialSAT.json` | Second kernel | `"enable_nanoda": false`. Only 2 of the 418 configs in the repo set it to true. One kernel (Lean's) is trusted. | Whether anyone has replayed it in a second kernel. |
| S11 | solution closure | Dependencies | Import closure of `OAI.Algorithms.SubexponentialSAT.Main`: **3,091 OAI files (~547k lines), external roots only `Lean` and `Mathlib`**. None of the 23 patched third-party packages (`lean/patches/`) is in scope. | — |
| S12 | solution closure | Escape hatches (pre-screen only) | Our token grep (comment-stripped) over the closure: 0 `sorry`, `admit`, `axiom` declarations, `native_decide`, `implemented_by`, `@[extern]`, `unsafe`, `debug.skipKernelTC`, `addDecl`, `#exit`, `@[csimp]`, `ofReduceBool`. Positive control: the same grep finds the 6 `sorry` of `LocalSmoothing.lean`. **3 `opaque` declarations** (`SqrtLog/LeafProgramPreparedRecoveryQuery.lean:59`, `…Witness.lean:178, :198`), each with a body (checked for `:59`); opaque values are kernel-checked, so they are not an escape. Not grepped: `partial`, `run_cmd`, `initialize`, `elab_rules`. **A grep is not soundness evidence** (A2 showed a forged declaration passes `#print axioms`); only a kernel replay is. | A full build plus kernel replay (follow-up F5). |

**Our verdict on the SAT statement (Tier C, AI reading):** on its face it is a faithful formalisation of "for every
fixed k, #k-SAT is computable on a multitape Turing machine in poly(L)·2^{O_k(ρ(n))} time and poly(L) space", which
for k = 3 contradicts ETH as usually stated. We found **no** weakening of the kinds we look for (definition holes,
non-uniformity, oracle power, unreasonable encoding, junk values, vacuous hypotheses). This is the unusual case where,
if the statement is faithful, **the weight of the claim rests on the kernel check, not on the informal proof**: that is
why S9–S12 and section 4.4 matter more than reading the 67-page manuscript.

### 4.2 LocalSmoothing

| # | Where | Possible gap | Our reading | Must check |
|---|---|---|---|---|
| L1 | `LocalSmoothing.lean:76` | **Junk `deriv`** | `literalSteinSquareFunction` uses `deriv (fun s => bochnerRiesz α s f x) r`. In Mathlib, `deriv` of a non-differentiable function is **0**, which would make `stein_square` trivially true where differentiability fails. For Schwartz f and α > 1/2 we expect differentiability in r, but it is not stated. | Confirm differentiability for α > 1/2, or exhibit an f with nonzero square function (a GATE-1 vacuity item). |
| L2 | `:39-40` | **Vacuity through a zero measure** | `sphereMeasure n = (volume).toSphere.map Subtype.val`. If this measure were 0, `kakeya_maximal` (LHS norm 0) and `spherical_restriction` (input norm 0, extension 0) would be trivially true. We expect it to be the (scaled) surface measure and nonzero for n ≥ 2. | That `sphereMeasure n ≠ 0` for n ≥ 2 (one Mathlib lemma away; vacuity check). |
| L3 | `:19-31` | Bochner-integral junk zeros | `∫` of a non-integrable function is 0 in Lean. On Schwartz data all integrands (Fourier transform, half-wave, Bessel potential) are integrable, so no junk zero. `kakeyaMaximal` uses `∫⁻` (lintegral, no junk); the extension integral is over a finite measure with a > 1, so L^a ⊂ L¹. | Nothing beyond L2. |
| L4 | `:84-96` | Data class | Schwartz f only, as in the manuscript ("We state the wave estimates for complex Schwartz data; density gives the indicated extensions", `introduction.tex:31-33`). Standard. | — |
| L5 | `:101, :111-112, :136, :85` | Endpoints | All ranges strict (ε > 0, δ > …, b > …, α > …). The Lean claims the interior only; **the endpoint restriction conjecture is not stated.** | Any public statement must say "interior". |
| L6 | `:65-66, :129-130` | Kakeya set definition | "contains a unit segment in every unit direction", no measurability, no compactness: the full set version (slightly stronger than the usual compact version, not weaker). `dimH F = n` uses Mathlib's Hausdorff dimension. | — |
| L7 | `:45-46, :113` | Conjugate exponent | `conjugateExponent a = a/(a−1)` for finite a, 1 for a = ∞; a > 1 is assumed, so no division junk. | — |
| L8 | `:33-34` | Time window | t ∈ [1,2] (`observationMeasure`), Sogge's setting. | — |
| L9 | closure | Dependencies and escapes | Closure of `OAI.Analysis.Fourier.LocalSmoothing.Comparator`: **2,261 OAI files (~190k lines)**, external root only `Mathlib`; 0 hits for every token in S12 (no `opaque` either). Same caveat: a grep is a pre-screen. | Kernel replay (follow-up F6). |
| L10 | `LocalSmoothing.json` | nanoda | No `enable_nanoda` key (default). | — |

**Our verdict (Tier C, AI reading):** the six statements look like faithful encodings of the interior-range
conjectures, with two **must-check vacuity items** (L1 junk `deriv`, L2 nonzero sphere measure). Neither is evidence of
a defect; both are the cheap checks that would exclude a trivially-true reading.

### 4.3 How far from practice is the SAT bound? (Tier X scratch, `/tmp/oaiclaim/scripts/crossover.py`, mpmath)

With A = 1 (A is existential and its true value is not stated, so real thresholds are later):
- the Lean exponent ρ(n) drops below n only once ln n > 5,504, i.e. **n > 10^2390**;
- it beats the 2^{0.386n} of the best published 3-SAT bounds (≈1.307^n) only for **n > 10^55,825**;
- the manuscript's sharper exponent n ln ln n/√ln n beats 2^{0.386n} once n > 10^79 (A = 1 again).
Control: the script's ratio at L = e⁴ equals 16/e² = 2.165, checked against the closed form.

**In plain words:** the claim is purely asymptotic. At any size of formula that could exist physically it has no effect
on SAT solving, on cryptography, or on our exhaustive searches, and no experiment could tell it apart from brute force.
Its importance, if correct, is theoretical: a hypothesis that underpins a large body of conditional lower bounds would
be false.

### 4.4 Has anyone run Comparator on these two challenges?

- **We found no recorded verdict** in the repository: no Comparator log, no "kernel accepts" text, and the catalogue's
  review field is `status: unchecked` (`formalization.yaml:1828`). `lean/ComparatorChallenges/README.md` gives only run
  instructions ("lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json").
- **So the accurate wording is:** OpenAI ships a Comparator config and a solution; **we have not seen a verdict, and we
  have not run one.** "Checked by Comparator" is the framing under test, not a fact we hold. Secondary coverage
  (MLQ) says that the Lean checks the encoded statements, not the papers, which agrees with our reading.

### 4.5 What we ran in this study

- `git clone --depth 1` of `openai/math` into `/tmp/oaiclaim/math` (HEAD `7ef5c0cc5ca4…`). The existing disk-2 clone was
  **not** reused because it is at `adc7f124` (7 October), before PR #3.
- The pinned stack on disk 2 (`openai_math_pinned/lean`) has the **same Mathlib pin** as the new commit (`d13f23b723`,
  batteries `f2effa3d80`, Lean 4.34.1), so a later replay can reuse its Mathlib oleans.
- Import-closure and escape-token scan (`/tmp/oaiclaim/scripts/closure_grep.py`), with the positive control above.
- One elaboration of the copied SAT challenge file under the pinned stack on core 7, with `#print axioms` appended
  (`/tmp/oaiclaim/scripts/compile_challenge.py`). Result: **rc 0 in 884.8 s** (cold disk-2 cache). The only
  diagnostic was `declaration uses 'sorry'` at line 194, and `#print axioms` gave `[propext, sorryAx, Classical.choice,
  Quot.sound]`. Lake also warned that some unrelated packages in the pinned project have local changes; none of those
  packages is in this file's imports. This shows two things only: the challenge statement elaborates under our pin,
  and the placeholder `sorry` is visible as `sorryAx`, which is the expected positive control for a sorried challenge.
  It says **nothing** about OpenAI's proof. LocalSmoothing.lean was not compiled.

---

## 5. Plausibility (honest assessment, no verdict)

- **Extraordinary-claim prior.** ETH has stood since 2001 and decades of algorithm design have stopped at c^n bounds
  with c > 1. The prior that a 2026 AI-generated manuscript refutes it is low. Likewise, Kakeya in all dimensions has
  resisted the field's strongest tools; Wang–Zahl's n = 3 result was 2025.
- **What raises it, conditionally.** Unlike most of the corpus, both claims come with Lean statements that, on our
  reading, are faithful and have no definition holes, and with solution closures that pull in nothing but Lean and
  Mathlib and contain no escape tokens. If a kernel replay accepts the solution with whitelisted axioms, then the
  remaining doubt is statement fidelity (section 4) and the soundness of Lean, Mathlib and the toolchain. That is a
  much smaller doubt than "is a 67-page proof correct".
- **What we do not know.** No verdict log exists in the repo; no one we can cite has replayed it; the release is one
  day old. For our gate the claims stand at: SAT statement Tier C (our reading), proof unknown to us.
- **Track record of the same source:** three manuscripts were withdrawn on 7 October for a sign error
  (`history.md:26-36`), and 14 were revised (`history.md:38`). That was unformalised work; it shows the informal manuscripts can be
  wrong, not that the Lean ones are.
- **Community (secondary only).** Al Jazeera quotes Ryan Williams: "We are working to verify and examine their proof
  and determine if it holds up" (summariser quote, from the News Study). The "State of Proof" tracker reportedly lists
  ETH as unverified with review not started (relayed). We found no public statement by Impagliazzo or Paturi; none was
  read.
- **Our position:** we do not assess the proof. Our contribution, if any, is to the instrument (statement fidelity,
  kernel replay), never to the mathematics.

---

## 6. The QFT claim

- **Reported (secondary only):** rigorous existence for certain 4D interacting QFTs; physics shepherds Gross, Jaffe,
  Klebanov, Nekrasov; AI artifacts withheld while the group writes the work up.
- **Primary, partial (owner's paste, §1b (c)–(d)):**
  - the claim covers existence of interacting 4D gauge-plus-fermion QFTs, including QCD and "a unified completion of
    the Standard Model";
  - natural-language proofs dated 9 Sept (Yang–Mills) and 18 Sept 2026 (QCD);
  - a Lean formalisation of Yang–Mills existence completed 16 Oct 2026, with **none stated for QCD**;
  - no mass gap is mentioned;
  - the contact address is `YANGMILLS4D@gmail.com`.
- **Not found:** no QFT or Yang–Mills challenge exists in `openai/math` at `7ef5c0c`, so the stated Lean formalisation
  is not public there.
- **What a lab like ours could do now: nothing useful.** No statement, no Lean and no manuscript are released. If Lean
  artifacts appear, the same fidelity checklist (section 4) would apply, with special attention to how "interacting"
  and "existence" (Wightman / Osterwalder–Schrader axioms) are encoded: that is exactly where definition-level
  weakening hides. We would not race the physics group.

---

## 7. Follow-ups for us

### 7.1 Re-check of our own A2 wording (prompted by the Gizmodo remark, secondary)

- **The prompt.** Gizmodo (relayed, not read) says critics found the Navier–Stokes Lean statement weaker than the
  published claim. The critic and the argument are both unread.
- **What our paper says** (`papers/p2_navier_stokes_audit/main.tex`, doi:10.5281/zenodo.23661381):
  - abstract, lines 70-74: "finds the Lean (C) faithful to Fefferman's (C)", tagged Tier C; it adds "Conditionally on
    fidelity ... the formal object proves Fefferman's alternative~(C); that is not a Clay determination";
  - line 301: the (C) witness has "zero initial data and a nonzero (rescaled) force"; "Criticism that the result is
    'forced, not unforced' is therefore not a fidelity defect against (C) as Clay states it (it would bear on
    (A)/(B))";
  - line 316: "We read neither of the corpus authors' papers, so nothing here compares the natural-language argument
    with the Lean development."
- **Is our wording adequate?** For what it claims, yes: our fidelity yardstick is **Clay's text**, and the paper says
  so. But "weaker than the published claim" is a comparison with the **authors' or OpenAI's own claim**, which our
  paper explicitly did not make. A reader of the abstract alone could read "faithful to Fefferman's (C)" as "faithful
  to what was announced". So there is a **gap of emphasis, not a found error**.
- **Proposal: a clarification note, not an erratum** (owner's decision; it touches a published record). A REVISION entry
  and, at the next version, one abstract sentence carrying four points already in §fid / §not:
  1. "faithful" means faithful to the text of Clay's alternative (C) (and (D) as corrected by the errata), nothing more;
  2. the witness uses a nonzero force, so it is not an unforced blow-up and says nothing about (A)/(B);
  3. the Lean was **not** compared with the authors' informal claims or with any press or company announcement;
  4. if a critique targets the (C) solution class itself, we owe a re-reading.
- **An erratum is warranted only** after the critique is read and shown to apply to the Lean-vs-Clay comparison.
- Cost: under an hour of writing; the new version would need the usual producer ≠ verifier audit.

### 7.2 Ranked follow-ups

Scales: **p** = prior of a useful, surviving output in the time box (0.1–0.5); **V** = value 1–5 on Proposal 4's
rubric; **F** = feasibility (0–1). **Score = p × V × F.**

**Why V differs from the News Study.** The News Study scored X1 (a statement review of the ETH machine model) at V = 1
because its lens was our four mission areas (energy, cancer models, materials, carbon), where this is off-mission. Here
the owner asks about the **mathematics programme**, whose rubric gives V = 3 to "an independent check of a recent
outside claim". We use V = 3 only for the full replays (F5, F6), which are such checks. Statement readings stay at
V = 2: this study already did most of that reading.

| Rank | Id | What | p | V | F | p × V × F | Tier reachable | Over-claim risk |
|---|---|---|---|---|---|---|---|---|
| 1 | F2 | Public explainer "How to read an AI-generated proof" built on this case (V raised to 2.5 after the page text, §1b) | 0.45 | 2.5 | 0.85 | 0.45 × 2.5 × 0.85 = **0.956** | none (outreach) | medium |
| 1 | F1 | A2 clarification note (7.1) | 0.50 | 2 | 0.95 | 0.50 × 2 × 0.95 = **0.950** | — (wording of our record) | low |
| 3 | F3 | GATE-1 fixtures from these two artifacts | 0.45 | 2 | 0.80 | 0.45 × 2 × 0.80 = **0.720** | process audit | low |
| 3 | F4 | Blind second fidelity reading (producer ≠ verifier) of both challenge files, plus the L1/L2 vacuity checks in Lean | 0.40 | 2 | 0.90 | 0.40 × 2 × 0.90 = **0.720** | C (reading); A for the two small vacuity lemmas | medium |
| 5 | F6 | A2-style rebuild + kernel replay + statement identity of `LocalSmoothing` (2,261 modules) | 0.30 | 3 | 0.45 | 0.30 × 3 × 0.45 = **0.405** | A for "our replay accepts these 6 statements with whitelisted axioms" | high |
| 6 | F5 | Same for `SubexponentialSAT` (3,091 modules), plus Comparator with `nanoda` enabled | 0.30 | 3 | 0.30 | 0.30 × 3 × 0.30 = **0.270** | A (same scope) | **very high** |
| – | F7 | Downstream use of ETH or Kakeya/restriction in our programme | — | — | — | **0** (no dependence) | — | — |

Ties: the two items ranked 1 (F2 and F1, 0.956 and 0.950) are tied, and so are the two ranked 3. The gaps between
ranks 1 and 4 are smaller than our calibration error. F1 still goes first in practice: it is cheaper, it concerns our
own published record, and the explainer should cite the corrected wording.

**F1. A2 clarification note.** Section 7.1. Fits because the published A2 record is ours and the criticism touches it.
1–2 weeks: a REVISION entry now, the abstract sentence at the next version, the usual audit. Cost: hours. Code of
conduct: yes; it narrows our own claim.

**F2. Explainer for the SocrateAI-Contribution audience (non-scientists).** What it is: a short public page explaining
the three layers of an AI-generated proof claim, using this case:
1. the informal manuscript (can be wrong: three were withdrawn on 7 October);
2. the Lean statement (it can say something different from the headline; the A2 forced/unforced example; junk
   `deriv`; a zero measure making a bound trivial; "interior of the range" versus the full conjecture);
3. the kernel check (strong, but only for the statement as written, and only once someone has actually run it; a grep
   or `#print axioms` alone can be fooled).
Plus the practical-size point of 4.3 (10^2390), so no one reads "ETH is false" as "SAT is now easy" or "cryptography
is broken". 1–2 weeks: draft, a reader check by a non-scientist, publish as a page. Cost: a day of drafting. Over-claim
risk: medium. It must say "claimed", never "proved", name the authors and the shepherds, and wait for the owner's
approval. Code of conduct: yes, if it takes no side on correctness.

**F3. GATE-1 fixtures from these artifacts** (Addendum A1, `PROPOSAL_4_ADDENDUM_2026-10-27.md:11`). What it is: planted
mutants that the vacuity and numeric checks must catch, built from real, high-stakes statements:
- a **junk-`deriv` mutant**: replace the square function by one whose `deriv` is of a non-differentiable function; the
  check must flag "trivially zero";
- a **zero-measure mutant**: `sphereMeasure := 0`; the check must flag `kakeya_maximal` as vacuous;
- a **weakened-runtime mutant**: replace ρ(n) by n (or 2^{A·n}); the numeric o(n) check must flag "not
  subexponential";
- the **hole mutant** `MainStatement := True`, already planned.
These compile against the challenge files only (no solution build), so each is a small file on core 7. Tier: process
audit; upgrades nothing. Fits because GATE-1 is already approved in the addendum and lacks realistic fixtures.

**F4. Blind second fidelity reading.** A different agent instance, blind to this study, rereads both challenge files
against the manuscripts (as A2 did against H9), and proves in Lean, under the pinned stack, the two vacuity facts L1
(differentiability, or a nonzero square function for one explicit f) and L2 (`sphereMeasure n ≠ 0`). 1–2 weeks: two
days of reading, small Lean files on core 7. Tier: C for the reading; A for the two small lemmas (about our reading,
not about OpenAI's proof). Over-claim risk: medium (never "the statements are faithful", only "two readings found no
mismatch; these vacuity checks pass").

**F5/F6. Full replay** (the A2 recipe: build from source under the pinned stack, kernel replay of every closure
declaration, elaborated-statement identity with mutants, Comparator with landrun/lean4export and **nanoda enabled**,
`#print axioms` in our own audit file).
- **What we would run:** copy the two closures into a separate Lake project that reuses the disk-2 Mathlib oleans (same
  pin); `lake build` the solution modules; `A2Replay`-style replay; Comparator on both JSONs; nanoda if it builds.
- **How long (not measured, extrapolated):** A2's 609 + 1,829 modules took 55 + 85 min to build and 11.5 + 15.7 min
  to replay (8–10 GB RSS each), and Comparator on `TriangularEnergy` (229 files) ran over 2 hours. SAT is 3,091 modules
  and ~547k lines; we would guess a build of 3–12 h on two cores and a Comparator replay of many hours to over a day.
  LocalSmoothing (2,261 modules, ~190k lines) is likely half that. The machine has a load average of 14 on 8 cores and
  29 GB RAM.
- **What it could show:** "our rebuild and kernel replay accept the six (or one) statements with axioms {propext,
  Classical.choice, Quot.sound}; the proved statement is the challenge statement; mutants are rejected." That is the
  same Tier-A scope as A2.
- **What it cannot show:** that the statement means what the press says (that is section 4, Tier C); that Lean, Mathlib
  or the kernel are sound; that the manuscript's proof is correct; anything about the sharper manuscript bounds or the
  corollaries.
- **Why F is low:** two closures this large, a busy machine, cores reserved for wave 1, C1b and the A1 scheduler, and
  building third-party code needs the owner's own `!` command (memory note matrix-lt-lab).
- **Over-claim risk: very high for SAT.** The temptation is "we verified that ETH is false". The only allowed sentence
  is conditional, as in A2: "if the statement is faithful and Lean/Mathlib are sound, then the kernel-checked theorem
  contradicts ETH as stated". Expert groups own the assessment.
- **Code of conduct:** acceptable only as an instrument check reported with full credit to OpenAI and the shepherd
  group, published **after** or **alongside** (not before) any working-group report, or sent to the group privately
  first (owner's decision). Racing them is declined.

**F7. Downstream use for our programme: none found.** A grep of `papers/ docs/ results/ formal/ formal_cert/ anse/
scripts/` for Kakeya, Exponential Time Hypothesis, Bochner–Riesz, local smoothing, Stein restriction and SETH finds
only Proposal 5's decline row (`NEXT_STEPS_PROPOSAL_5_MATHEMATICS_2026-10-27.md:490`), the News Study, and "Sethi"
false positives in the K3 papers and H13. Nothing in our lattice sums, theta functions, energy minimisation, universal
optimality, or certified-numerics stack depends on ETH or on restriction/Kakeya. C1b's exhaustive census is a finite
enumeration; 4.3 shows the claimed algorithm would not change its cost at any feasible size.

**Also considered.**
- **The MUB-6 auxiliary checker** released in the same PR (restored C++ and a Python checker) could be re-run as Tier C;
  off-topic here, unranked (News Study §3(e)).
- **Rational Hodge for CM abelian varieties** got a Lean formalisation in the same PR; out of scope for this study.

### 7.3 Decline

| Decline | Why |
|---|---|
| Any wording "we verified ETH is false / Kakeya is proved / OpenAI's result" | Over-claim; LL §16/§18: a re-run is an instrument check |
| Racing the Impagliazzo–Paturi–Williams group or the physics shepherds | Code of conduct |
| Running, extracting or benchmarking the SAT algorithm | No value at feasible sizes (4.3); invites "SAT is easy" readings |
| Any QFT work | Nothing released |
| Reading or reasoning about the informal proofs as referees | Not our competence; expert groups own it |
| Using the Unique Games corollary or other corpus results as inputs to our own proofs | Unrefereed dependencies |

### 7.4 Recommendation

1. **Now:** F1 (A2 clarification note, owner approval) and F3 (GATE-1 fixtures; small files, core 7).
2. **This week, after F1:** F2 (explainer), with the owner's approval before anything is public.
3. **If capacity allows:** F4 (blind second reading plus two vacuity lemmas).
4. **Defer** F6 then F5 until wave 1 and C1b have finished, and only with the owner's `!` approval for the build. If one
   is done, do LocalSmoothing first: it is smaller, it has no `opaque`, and it does not carry the ETH over-claim risk.
5. Ask the owner to **paste the OpenAI page text**, to answer the questions of section 1, in particular whether
   independent audits are invited and through which channel.

---

## 8. What this means for the mathematics programme

- **The lesson of A2 is confirmed and sharpened.** A2 found that a faithful-looking statement can be narrower than its
  headline (forced, not unforced, blow-up), and that `#print axioms` alone can be fooled. These two releases are the
  case where Comparator's known gap (hole bodies) does **not** apply; what remains is junk values, vacuity, endpoints
  and the run itself. That is exactly GATE-1's scope, so the right use of this news is to strengthen our gate (F3), not
  to chase the claims.
- **C1b** (exhaustive death-Birth amplifier census at N = 11, preregistered in Addendum 2) is untouched: it relies on
  nothing from ETH, and the claimed algorithm is irrelevant at its sizes (4.3).
- **K1 and M3 papers**: no dependence. M3 (independent partial check of the Luo–Wei Yukawa threshold) is the
  producer ≠ verifier pattern done right; F4/F5/F6 would be the same pattern at much higher cost and lower value to us.
- **Proposal 5** already declines "anything framed as solving a famous conjecture (… Kakeya, Navier–Stokes, ETH …)"
  (`NEXT_STEPS_PROPOSAL_5_MATHEMATICS_2026-10-27.md:490`). This study supports that row and adds no new Proposal-5 item.
- **Sandier–Serfaty Lean port (A1):** the LocalSmoothing development (2,261 files of Fourier, PDE and measure theory on
  Mathlib only) is a potential source of reusable lemmas, for example Schwartz-class Fourier facts and surface measure
  on spheres. That is reuse with credit under Apache-2.0, if a specific lemma is needed; it is not a programme item.
- **Resource note:** wave 1, C1b and the A1 scheduler keep every core busy, so the replays (F5, F6) are the first thing
  to drop.

---

## 9. Reading log

| # | Source | How opened | One quoted sentence |
|---|---|---|---|
| 1 | `openai/math` `history.md` at `7ef5c0c` | full, local clone | "The case of 3-SAT refutes the Exponential Time Hypothesis." |
| 2 | `openai/math` PR #3 (title, body, lock status) | GitHub API | "Add the manuscripts *Local smoothing for the Euclidean wave equation* and *The Exponential Time Hypothesis is False*, with accompanying Lean formalizations." |
| 3 | `openai/math` `README.md` | full | "We defer to the math community completely on matters of credit, precedence, and concurrent work." |
| 4 | `lean/ComparatorChallenges/SubexponentialSAT.lean` and `.json` | full | "One fixed primitive machine exactly counts every bounded-width formula, decides satisfiability, meets the square-root-logarithmic time bound, and uses only polynomially many visited tape cells at every execution prefix." (docstring, line 191-193) |
| 5 | `lean/ComparatorChallenges/LocalSmoothing.lean` and `.json` | full | "Standalone Comparator reference: six independent targets, no definition holes." |
| 6 | `lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean` (lines 1-120), `Main.lean`, parts of `Encoding.lean`, `Computation.lean`, `SqrtLog/StatementScale.lean`, two `opaque` sites | partial | "Exact counting and SAT on one fixed primitive run, with the unchanged ETH square-root-log time scale and polynomial all-prefix visited space." |
| 7 | `lean/docs/378.md`, `lean/docs/079.md` | full | "For $m$ clauses, the October 25 manuscript gives the sharper time bound" (378) |
| 8 | `lean/formalization.yaml` (header, SAT/LocalSmoothing entries, review field), `lean/ComparatorChallenges/README.md`, `lean/patches/` listing, `lake-manifest.json` | partial | `status: unchecked` (review field) |
| 9 | ETH manuscript source `build/main_full_version.tex` (lines 28-250, 1495-1520, plus greps) | partial | "our result does not imply that general NP problems admit subexponential time algorithms." |
| 10 | Local smoothing manuscript source `build/paper.tex` (abstract), `sections/introduction.tex` (Theorems 1.1, 1.2), `sections/history.tex` (lines 1-60), `sections/kakeya.tex` (grep) | partial | "We prove Sogge's local smoothing conjecture for the Euclidean wave equation in every spatial dimension at least two." |
| 11 | Our `papers/p2_navier_stokes_audit/main.tex` (abstract, §claims, §fid, §not) | partial | "We read neither of the corpus authors' papers, so nothing here compares the natural-language argument with the Lean development." |
| 12 | Our `docs/studies/NEWS_STUDY_2026-10-27.md`, `docs/proposals/PROPOSAL_4_ADDENDUM_2026-10-27.md`, header of `NEXT_STEPS_PROPOSAL_5_MATHEMATICS_2026-10-27.md`, `results/proposal2/2026-10-26/A2/{REBUILD,SOUNDNESS_SCAN}.md` (timings) | full / partial | "Rule: if a check flags a vacuous or trivially true statement, that statement may not be labelled Tier A." (Addendum A1) |

| 13 | OpenAI page *Building scientific understanding with academic communities* (fr-FR), **partial**: three paragraphs plus a continuation, pasted by the owner (we did not fetch it) | owner's paste, relayed | « De manière surprenante, notre système a récemment démontré que l'ETH est fausse, un résultat qui a ensuite été vérifié en Lean. » |

**Not read.**
- The rest of the OpenAI page: the fetch returned HTTP 403 (fr-FR and English). Two parts are missing: the text
  between « Nos » and « communication avec l'un ou plusieurs de ses membres », and everything after the last pasted
  sentence.
- `openai.com/index/sharing-ai-progress-in-mathematics/`: HTTP 403 (News Study).
- The Reddit thread.
- The PDFs `paper.pdf` of both manuscripts (we read their LaTeX sources in part instead; 67 and 59 pages).
- Gizmodo, DEV Community, MLQ.ai, the State of Proof tracker: relayed by another agent, **secondary**, not opened here.
- Al Jazeera: summariser quote only, via the News Study.
- Any statement by Impagliazzo, Paturi, or the physics shepherds.
