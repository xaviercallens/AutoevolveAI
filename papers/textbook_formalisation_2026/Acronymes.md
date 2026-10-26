# Acronymes : les cinq ré-exportations du chapitre 5

Lean file: `formal_cert/Programmes/Famille/Acronymes.lean` (namespace `Acronymes`).
LaTeX listing (verbatim copy, generated): `acronymes_listing.tex` (`lstlisting`, `language=Lean`; it carries the
book's `literate` table extended with `∫` and `ι`, test-compiled with pdflatex against the `main.tex` preamble).

Each theorem is a re-export: its statement is copied from the source theorem and its proof is the source theorem
applied to its arguments. After each one, an `example : @NAME = @source := rfl` checks that the two constants have
exactly the same type (at universe 0 for `ALEXIS` and `AURELIA`, whose checks are pinned `.{0}`; an `Eq` between them only typechecks if the types agree; proof irrelevance closes it).
The family meaning of the names is not stated in the code; it is only hinted at on the dedication page.

## Table

| Nom | Backronyme | Théorème source (fichier : nom) | Énoncé (en français) | `#print axioms` (verbatim) |
|---|---|---|---|---|
| `ALIX` | **A** **L**attice **I**s e**X**tremal | `formal_cert/Triangular/AnyDensity.lean` : `TriangularDensity.triangular_optimal_any_density` | Pour tout potentiel admissible `h` (complètement monotone en `r²`) et toute densité `ρ > 0`, le réseau triangulaire dilaté `ρ^{-1/2} A` est localement fini, de densité `ρ`, et son énergie est inférieure ou égale à celle de toute configuration localement finie de densité `ρ`. **Conditionnel** au théorème amont `universal_energy_minimum` d'openai/math (généré par IA, non relu par des pairs). | `'Acronymes.ALIX' depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `KAL` | **K**olmogorov **A**bsorption **L**imit | `formal_cert/Programmes/PopGen/Absorption.lean` : `ProgPopGen.fixation_limit` | Pour un noyau stochastique sur `{0,…,N}` à bords absorbants, si `h` est harmonique aux états intérieurs, `h 0 = 0`, `h N = 1`, et si la variance à un pas de `h` est strictement positive en chaque état intérieur, alors `Pⁿ(i,N) → h(i)` et `Pⁿ(i,0) → 1 − h(i)` (puissances de Chapman–Kolmogorov). | `'Acronymes.KAL' depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `ILENE` | **I**sothermal **L**aw: **E**very **N**ode **E**quivalent | `formal_cert/Programmes/EvoGraph/BirthDeath.lean` : `EvoGraph.isothermal_fixation_single` | Processus naissance–mort à sélection uniforme sur un graphe isotherme (matrice doublement stochastique) fortement connexe : un mutant unique de fitness `r ≠ 1`, placé en **n'importe quel** sommet `v`, se fixe avec probabilité limite `(1 − r⁻¹)/(1 − r⁻ⁿ)`, la même pour tous les sommets (valeur de Moran). | `'Acronymes.ILENE' depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `ALEXIS` | **A**veraged **L**aplace **EX**ponentials **I**nherit **S**igns | `formal_cert/Autoresearch/KeldyshCM.lean` : `AutoresearchKeldysh.laplace_admissible` | Un mélange positif d'exponentielles décroissantes `t ↦ ∫ e^{−t k(x)} m(x) dμ(x)` (avec `k, m ≥ 0` et tous les moments `∫ kⁿ e^{−ck} m dμ` finis pour `c > 0`) est un potentiel admissible : `C^∞` sur `]0, +∞[`, positif, avec `(−1)^r g^{(r)} ≥ 0`. | `'Acronymes.ALEXIS' depends on axioms: [propext, Classical.choice, Quot.sound]` |
| `AURELIA` | **A**verage **U**nder **R**eplication: **E**volution **L**ifts **I**t, **A**lways | `formal_cert/Programmes/PopGen/Price.lean` : `ProgPopGen.Price.fisher_haploid_nondecreasing` | Sélection haploïde à fitness de types constantes, sans biais de transmission, abondances positives ou nulles, abondance totale et fitness moyenne strictement positives : la fitness moyenne ne décroît pas, `w̄ ≤ w̄'`. C'est un cas particulier du théorème fondamental de Fisher, déduit de l'équation de Price. | `'Acronymes.AURELIA' depends on axioms: [propext, Classical.choice, Quot.sound]` |

## Gate (actual tool output)

- **Compile** (Lean 4.34.1 + Mathlib d13f23b7, `scripts/certified_numerics/lean_pinned.py compile ... --olean
  Programmes.Famille.Acronymes`, cores 6–7): rc 0, 99.8 s. Record:
  `results/textbook_formalisation_2026/acronymes_compile_final.json` (an earlier compile of the same code, before
  docstring-only edits for the LaTeX listing, also rc 0 with the same five axiom lines:
  `acronymes_compile.json`). The five `rfl` identity checks elaborate (no error in the output).
- **Axioms**: all five within `{propext, Classical.choice, Quot.sound}` (lines above, copied from the JSON).
- **Forbidden-token grep** (`skipKernelTC|addDecl|native_decide|implemented_by|sorry|admit`) over
  `Acronymes.lean` and the in-repo sources it depends on (`Triangular/{AnyDensity,Riesz,RieszFinite}.lean`,
  `Programmes/PopGen/{Absorption,MoranModel,Price}.lean`, `Programmes/EvoGraph/{Transport,BirthDeath}.lean`,
  `Autoresearch/{Yukawa,KeldyshCM}.lean`): one hit only, a comment in `MoranModel.lean` line 237
  ("planted sorry/axiom controls live in `PopGenProgControls.lean`"); no code hit. Upstream OAI and Mathlib
  modules were not grepped here.
- **Kernel replay** (`leanchecker` from the 4.34.1 toolchain):
  - `Programmes.Famille.Acronymes`: rc 0, 108.5 s (`results/textbook_formalisation_2026/acronymes_leanchecker.json`).
  - Source modules: see `results/textbook_formalisation_2026/acronymes_leanchecker_sources.json`
    ; all rc 0: `Triangular.Riesz` (105.7 s), `Triangular.RieszFinite` (115.2 s), `Triangular.AnyDensity`
    (910.7 s), `Programmes.PopGen.Absorption` (71.0 s), `Programmes.PopGen.MoranModel` (63.0 s),
    `Programmes.PopGen.Price` (60.8 s), `Programmes.EvoGraph.Transport` (58.7 s), `Programmes.EvoGraph.BirthDeath`
    (56.9 s), `Autoresearch.Yukawa` (66.8 s), `Autoresearch.KeldyshCM` (66.3 s). Each run replays that module's own
    declarations; upstream OAI and Mathlib modules were not replayed here..
- **Controls** (`.scratchpad/FamilleControls.lean`, importing the module): compile rc 1 as intended
  (`results/textbook_formalisation_2026/acronymes_controls.json`). Negative 1: a planted `sorry` theorem prints
  `'planted_ALIX_sorry' depends on axioms: [sorryAx]`. Negative 2: `example : @Acronymes.KAL =
  @ProgPopGen.harmonic_unique_of_var := rfl` fails with `Type mismatch`, so the `rfl` identity check does reject a
  different statement. Positive: `example : @Acronymes.ILENE = @EvoGraph.isothermal_fixation_single := rfl` in the
  same file elaborates with no error.

## Paragraphe pour le chapitre 5

> **Cinq noms courts.** Le fichier `Programmes/Famille/Acronymes.lean` ne démontre rien de nouveau : il
> ré-exporte, sous des noms brefs, cinq théorèmes déjà vérifiés par le noyau ailleurs dans `formal_cert/`.
> Chaque nom est un acronyme dont la docstring donne le développement : `ALIX` (*A Lattice Is eXtremal*,
> optimalité du réseau triangulaire à toute densité, conditionnelle au résultat amont d'openai/math),
> `KAL` (*Kolmogorov Absorption Limit*, probabilité de fixation comme limite d'absorption), `ILENE`
> (*Isothermal Law: Every Node Equivalent*, théorème isotherme), `ALEXIS` (*Averaged Laplace EXponentials
> Inherit Signs*, admissibilité des mélanges de Laplace) et `AURELIA` (*Average Under Replication: Evolution
> Lifts It, Always*, croissance de la fitness moyenne). La preuve de chacun est l'application du théorème
> source à ses hypothèses ; une ligne `example : @ALIX = @triangular_optimal_any_density := rfl` (et de même
> pour les quatre autres) certifie que l'énoncé est littéralement celui de la source, ni plus faible ni plus
> fort (à l'univers 0 pour `ALEXIS` et `AURELIA`). Les axiomes affichés par `#print axioms` sont, pour les cinq, `propext`, `Classical.choice` et
> `Quot.sound`, et le module est rejoué par `leanchecker`. Le lecteur attentif reconnaîtra peut-être d'autres
> lectures de ces cinq noms.
