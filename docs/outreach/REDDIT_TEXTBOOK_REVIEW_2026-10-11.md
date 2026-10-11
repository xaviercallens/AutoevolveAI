# Reddit call for red-team and citizen-science review: textbook v1

Drafts for the author to post. Nothing here has been posted. Record: doi:10.5281/zenodo.23295142 (public, CC-BY-4.0,
105-page PDF + source bundle). Before posting, check each subreddit's current rules. Several large ones (r/math,
r/Physics, r/AskPhysics) remove AI-generated content or "personal theories". The posts below disclose the AI
authorship in the first lines. Don't remove that to get past a filter; post where it is welcome instead.

Suggested order:
1. r/FluidMechanics (main post A). This is the community the author already reviews with.
2. r/CitizenScience (post B).
3. r/leanprover (post C), and in parallel the Lean Zulip #Is there code for X? / #new members stream, where Lean
   reviewers actually are.
4. Only after the first wave of corrections, consider r/math's "Quick Questions" thread or a moderator message, not a
   top-level post.

Where reviewers report: GitHub issues on
https://github.com/xaviercallens/SocrateAI-Scientific-MechanicaFluidorum/issues, with the label `textbook-review` (create
it before posting). The template is at the end of this file.

---

## Post A: r/FluidMechanics

**Title:** Red-team request: a student textbook linking 2D point vortices to a machine-checked lattice-energy theorem
(AI-assisted, unreviewed, please try to break it)

**Body:**

> Disclosure up front: this book was written by AI agents (Claude) under my direction. I'm a citizen scientist, not a
> mathematician, and no human expert has reviewed it yet. That's why I'm posting. I'm asking you to find what's wrong,
> not to endorse it.
>
> **What it is.** A free 105-page textbook (CC-BY), *The Triangular Lattice and Universal Optimality*:
> https://doi.org/10.5281/zenodo.23295142
>
> It follows one theorem from the openai/math Lean 4 release: among all planar point configurations of a given
> density, the triangular lattice has the least energy for every completely monotone repulsion. Each result appears
> three ways: as a human proof step by step, as the Lean statement that was machine-checked, and as numerics in Python
> and in Rust (SUNDIALS CVODE). Every claim is labelled with how far to trust it: A = machine-checked, L = literature,
> C = argument only, X = numerical exploration that supports nothing.
>
> **Why this sub.** Chapter 4 starts from 2D Euler point vortices: the logarithmic interaction, Kirchhoff's equations,
> vortex crystals (Fine et al. 1995), and BEC vortex lattices (Abo-Shaeer et al. 2001). It explains where the theorem
> applies and where it does not. The log interaction is *not* in the theorem's class; the book says so and explains
> why.
>
> **What I'd most like attacked** (Chapter 4 is the most exposed):
> 1. The point-vortex Hamiltonian, the rotating-frame argument (n_b = 2Ω/Γ), and the invariants P, Q, I. Are the signs
>    and factors right?
> 2. Physics statements tagged [Tier C] "general knowledge, not cited": wakes in dusty plasmas, mode-coupling
>    instability, ion crystals. Which are wrong or need a real citation?
> 3. Do the "what CVODE/IDA can and cannot do here" claims hold for real vortex-crystal simulations?
> 4. Run the exercises. Are any ill-posed, too hard without saying so, or wrong?
> 5. Known weak spot, already disclosed: the companion paper's Yukawa numerics truncate the potential at r_c = 8. At
>    κ = 1 that shifts the energies by about 1.8e-2, more than the triangular–square gap. Is our argument that the gap
>    comparison still stands convincing?
>
> **How to report.** Open an issue on
> https://github.com/xaviercallens/SocrateAI-Scientific-MechanicaFluidorum/issues (label `textbook-review`) with the
> page, the claim, and why it's wrong. Every accepted correction will be credited by name (or handle) in v2, and an
> error you find is worth more to me than praise.
>
> Code is in the record's source bundle and in https://github.com/xaviercallens/rusty-SUNDIALS. The Python scripts run
> on a laptop in under a minute.

---

## Post B: r/CitizenScience

**Title:** Help test a free AI-written maths/physics textbook: run the scripts, check the numbers, report what breaks

**Body:**

> I'm a citizen scientist. With AI agents (Claude) I produced a free 105-page textbook about why the triangular
> (honeycomb-like) arrangement is the lowest-energy way to pack repelling particles in a plane, a theorem that was
> machine-checked in Lean 4. No expert has reviewed it yet, and I'd like ordinary careful readers to try to break it
> first: https://doi.org/10.5281/zenodo.23295142
>
> You don't need to follow the proofs to help. Useful tasks, from easiest to hardest:
> - **Reproduce.** Download the bundle, run `code/ch3_yukawa_small.py`, `code/ch4_point_vortices.py` and
>   `code/ch5_checks.py` (Python + numpy/scipy), and check that the printed numbers match the book. Report your OS and
>   Python version even if everything matches. That counts too.
> - **Read for clarity.** Mark any sentence a curious student could not follow.
> - **Check a citation.** Every [Tier L] claim cites a paper. Does the paper say that?
> - **Hunt for overclaims.** Does any sentence suggest more is proved than the tier label says?
>
> Report in a GitHub issue (no coding needed, just text):
> https://github.com/xaviercallens/SocrateAI-Scientific-MechanicaFluidorum/issues. Contributors are credited in v2.

---

## Post C: r/leanprover (and Lean Zulip)

**Title:** Review request: small Lean 4 additions on top of openai/math's triangular-lattice universal optimality
(open vs closed disks, Riesz, every density): looking for statement-fidelity problems

**Body:**

> AI-assisted work (Claude agents under my direction); I'm asking for scrutiny, not endorsement.
>
> On top of openai/math's `universal_energy_minimum` (pinned at adc7f124; Lean 4.34.1, Mathlib d13f23b7) we
> kernel-checked a few consequences, with every axiom footprint within {propext, Classical.choice, Quot.sound}:
> - D1/D1b: Riesz optimality and finiteness for s > 2;
> - D2: universal optimality at every density;
> - D3: non-uniqueness, the lattice with one vacancy;
> - D4: `energy_eq_openEnergy` / `densityOne_iff_open`. Upstream's liminf energy and density-one condition are
>   unchanged with `Metric.ball` in place of `Metric.closedBall`, so `universal_energy_minimum_open` holds. The
>   `_any` versions need no local finiteness, and `ctl_open`/`ctl_closed` show the identity is not definitional.
>
> Files: `formal_cert/Triangular/*.lean` in https://github.com/xaviercallens/AutoevolveAI (branch
> `worktree-openai-math-discovery`), also in the Zenodo bundle https://doi.org/10.5281/zenodo.23295142. The textbook
> sets each Lean statement beside its human proof.
>
> What we can't check ourselves: **do the definitions say what the prose says?** For example: is upstream's
> `ENNReal.ofReal`-truncated lower energy the right notion; is D2's rescaling faithful to CKMRV Definition 1.3; does the
> book misdescribe any Lean statement? Issues welcome on the repo above or on MechanicaFluidorum.

---

## Red-team checklist (link it from the issue template)

These are the places most likely to be wrong, ranked by our own audits:
1. **Definition fidelity:** upstream's `energy` is a liminf in `[0, ∞]` of `ENNReal.ofReal` sums. Every Tier A claim
   is conditional on this matching the intended physics.
2. **Chapter 3, pair counting:** the book's energies count each pair once, which is ½ of Chapter 1's E_g. Check every
   cross-chapter comparison.
3. **The truncation erratum** (editor's note): shifted-force Yukawa at r_c = 8 is not completely monotone.
4. **Chapter 4, Tier C physics** with no citation (dusty-plasma wakes, ion crystals, Hales).
5. **Chapter 5:** the fcc/bcc statement is conditional on a Tier X inequality (Project U2), and so is the discussion of
   the per-potential conjecture.
6. **D4 at densities other than one** is Tier C, not formalised.

## Issue template (for `.github/ISSUE_TEMPLATE/textbook-review.md` in MechanicaFluidorum, via a PR)

```
---
name: Textbook review
about: Report an error or unclear passage in the Universal Optimality textbook (doi:10.5281/zenodo.23295142)
labels: textbook-review
---
**Page / section:**
**Claim as written (quote):**
**Tier shown in the book (A/L/C/X):**
**What is wrong or unclear:**
**Evidence (derivation, citation, script output with OS/Python version):**
**Suggested correction:**
**How you'd like to be credited (name, handle, or anonymous):**
```
