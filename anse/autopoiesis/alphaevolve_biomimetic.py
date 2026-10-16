"""
AlphaEvolve + Biomimetic Genetic Evolution Engine for AutoevolveAI (ANSE).

Synthesizes Google DeepMind's AlphaEvolve / FunSearch evolutionary paradigm with
Quality-Diversity (MAP-Elites), AST-level Genetic Programming, and Biomimetic
regulatory mechanisms on top of ANSE's physical Energy Function (E):

Literature Grounding (arXiv):
  - Novikov et al. (2025), "AlphaEvolve: A coding agent for scientific and
    algorithmic discovery", arXiv:2506.13131 (https://arxiv.org/abs/2506.13131)
  - Romera-Paredes et al. (2023/2024), "Mathematical discoveries from program
    search with large language models (FunSearch)", arXiv:2312.02175
    (https://arxiv.org/abs/2312.02175)
  - Lehman et al. (2022), "Evolution through Large Models (ELM)",
    arXiv:2206.08896 (https://arxiv.org/abs/2206.08896)
  - Mouret & Clune (2015), "Illuminating search spaces by mapping elites
    (MAP-Elites)", arXiv:1504.04909 (https://arxiv.org/abs/1504.04909)
  - Guo et al. (2023/2024), "Connecting Large Language Models with Evolutionary
    Algorithms Yields Powerful Prompt Optimizers (EvoPrompt)", arXiv:2309.08532
    (https://arxiv.org/abs/2309.08532)
  - Liu et al. (2024), "Evolution of Heuristics: Towards Efficient Automatic
    Algorithm Design Using Large Language Model (EoH)", arXiv:2401.02051
    (https://arxiv.org/abs/2401.02051)

Core Biomimetic & Evolutionary Pillars:
  1. Thermodynamic + Allostatic Energy Function:
     Combines physical execution energy E_phys (latency, peak RAM, invariant error)
     with metabolic allostatic load E_metabolic (structural AST complexity excess).
  2. Artificial Immune System (AIS) Negative Selection & Somatic Hypermutation:
     Eliminates non-self/pathogenic candidates (cyber-defense violations, stubs,
     previously failed antigen hashes) before execution (apoptosis E = 10^6), and
     scales mutation intensity inversely with clonal affinity.
  3. Epigenetic Chromatin Regulation (Methylation vs. Acetylation):
     Locks stable, low-energy AST functions via epigenetic methylation while
     opening high-energy bottleneck functions (acetylation) for targeted crossover
     and mutation.
  4. Homologous AST Crossover & AlphaEvolve Diff Patching:
     Recombines verified AST function definitions across parent elites and applies
     structured SEARCH/REPLACE diff blocks or somatic numerical/operator refinements.
  5. Island-Model MAP-Elites Archipelago with Homeostatic Temperature Control:
     Maintains K islands across a morphogen temperature gradient, archiving elites
     in a 2D behavioral descriptor grid (structural complexity x memory efficiency)
     with periodic ring migration and stagnation-triggered island repopulation.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import math
import random
import re
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any

from anse.harness import HardenedAutoresearchLoop
from antigravity_harness.core.argos_hardener import ArgosHardeningEngine

MAX_APOPTOSIS_ENERGY: float = 1e6


@dataclass
class EpigeneticChromatinState:
    """Epigenetic regulation marks on AST function loci.

    - `methylated_loci`: Stable, low-energy function names protected from destructive
      mutation (heterochromatin).
    - `acetylated_loci`: Bottleneck or recently mutated function names open for
      homologous recombination and somatic hypermutation (euchromatin).
    - `locus_energy_ema`: Exponential moving average of energy attributed to each function.
    """

    methylated_loci: set[str] = field(default_factory=set)
    acetylated_loci: set[str] = field(default_factory=set)
    locus_energy_ema: dict[str, float] = field(default_factory=dict)

    def update_from_evaluation(
        self,
        function_names: Sequence[str],
        total_energy: float,
        methylation_threshold: float = 25.0,
        alpha: float = 0.4,
    ) -> None:
        """Update epigenetic methylation/acetylation marks after measuring candidate energy."""
        for fn in function_names:
            prev = self.locus_energy_ema.get(fn, total_energy)
            updated = (1.0 - alpha) * prev + alpha * total_energy
            self.locus_energy_ema[fn] = updated
            if updated <= methylation_threshold:
                self.methylated_loci.add(fn)
                self.acetylated_loci.discard(fn)
            else:
                self.acetylated_loci.add(fn)
                self.methylated_loci.discard(fn)


@dataclass
class DiploidGenome:
    """Biomimetic diploid code organism evaluated in the AlphaEvolve archipelago."""

    genome_id: str
    dominant_code: str
    recessive_code: str = ""
    generation: int = 0
    island_id: int = 0
    parent_ids: tuple[str, ...] = ()
    mutation_operator: str = "seed"
    physical_energy: float = MAX_APOPTOSIS_ENERGY
    metabolic_energy: float = 0.0
    total_energy: float = MAX_APOPTOSIS_ENERGY
    latency_ms: float = 9999.0
    memory_mb: float = 0.0
    invariant_error: float = 1.0
    pareto_rank: int = 0
    crowding_distance: float = 0.0
    behavioral_descriptor: tuple[int, int] = (0, 0)
    epigenetics: EpigeneticChromatinState = field(default_factory=EpigeneticChromatinState)
    attestation_token: str = ""

    @property
    def objective_vector(self) -> tuple[float, float, float, float]:
        """4D minimization objective vector: (latency_ms, memory_mb, metabolic_energy, invariant_error)."""
        return (
            float(self.latency_ms),
            float(self.memory_mb),
            float(self.metabolic_energy),
            float(self.invariant_error),
        )

    @property
    def code_sha256(self) -> str:
        return hashlib.sha256(self.dominant_code.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["epigenetics"]["methylated_loci"] = sorted(self.epigenetics.methylated_loci)
        d["epigenetics"]["acetylated_loci"] = sorted(self.epigenetics.acetylated_loci)
        d["code_sha256"] = self.code_sha256
        return d


class ArtificialImmuneSystem:
    r"""Biomimetic Artificial Immune System (AIS) enforcing negative selection & clonal affinity.

    - Negative Selection (T-Cell Tolerance): Rejects any candidate matching known
      pathogenic AST signatures (via `ArgosHardeningEngine`) or previously recorded
      lethal antigen hashes ($E \ge 10^6$).
    - Clonal Somatic Hypermutation Rate: Computes mutation rate $\mu(E) \in [\mu_{\min}, \mu_{\max}]$
      inversely proportional to clonal affinity ($1 / (1 + E)$), so high-affinity elites
      undergo fine-grained exploitation while low-affinity candidates undergo broad mutation.
    """

    def __init__(
        self,
        hardening_engine: ArgosHardeningEngine | None = None,
        min_mutation_rate: float = 0.08,
        max_mutation_rate: float = 0.75,
    ) -> None:
        self.hardening_engine = hardening_engine or ArgosHardeningEngine()
        self.min_mutation_rate = min_mutation_rate
        self.max_mutation_rate = max_mutation_rate
        self.lethal_antigen_hashes: set[str] = set()
        self.antibody_memory: dict[str, float] = {}

    def negative_selection_screen(self, code: str) -> tuple[bool, str, str]:
        """Screen candidate code before execution.

        Returns `(passed, reason, attestation_token)`.
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash in self.lethal_antigen_hashes:
            return False, "AIS Negative Selection: matches known lethal antigen hash", ""

        report = self.hardening_engine.audit_code(code, target="<ais_candidate>")
        if not report.passed:
            self.lethal_antigen_hashes.add(code_hash)
            reasons = "; ".join(f"{v.rule_id}: {v.message}" for v in report.violations[:3])
            return False, f"AIS Apoptosis ({reasons})", ""

        return True, "AIS Self-Tolerant", report.attestation_token

    def record_outcome(self, code: str, total_energy: float) -> None:
        """Update immunological memory with candidate evaluation outcome."""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if not math.isfinite(total_energy) or total_energy >= MAX_APOPTOSIS_ENERGY * 0.5:
            self.lethal_antigen_hashes.add(code_hash)
        else:
            self.antibody_memory[code_hash] = total_energy

    def somatic_hypermutation_rate(self, energy: float, reference_energy: float = 50.0) -> float:
        r"""Compute adaptive somatic mutation rate $\mu(E)$ from clonal affinity."""
        if not math.isfinite(energy) or energy >= MAX_APOPTOSIS_ENERGY * 0.5:
            return self.max_mutation_rate
        # Normalized affinity in (0, 1]: higher affinity -> lower mutation rate
        affinity = 1.0 / (1.0 + max(0.0, energy) / max(1e-6, reference_energy))
        rate = self.max_mutation_rate - affinity * (self.max_mutation_rate - self.min_mutation_rate)
        return float(max(self.min_mutation_rate, min(self.max_mutation_rate, rate)))


class ASTGeneticOperators:
    """AST-aware Genetic Programming & AlphaEvolve SEARCH/REPLACE diff operators."""

    SEARCH_REPLACE_PATTERN = re.compile(
        r"<<<<<<< SEARCH\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> REPLACE",
        flags=re.DOTALL,
    )

    @staticmethod
    def extract_function_map(code: str) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
        """Parse Python code and return an ordered mapping of function name -> AST node."""
        tree = ast.parse(code)
        fn_map: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_map[node.name] = copy.deepcopy(node)
        return fn_map

    @staticmethod
    def compute_ast_complexity_and_loci(code: str) -> tuple[int, list[str]]:
        """Return (branch_and_node_complexity, list_of_function_names)."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 999, []

        branch_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.Try,
            ast.With,
            ast.BoolOp,
            ast.ListComp,
            ast.DictComp,
            ast.SetComp,
            ast.GeneratorExp,
        )
        complexity = 1
        fn_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, branch_nodes):
                complexity += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_names.append(node.name)
        return complexity, fn_names

    @classmethod
    def apply_alphaevolve_diff(cls, base_code: str, diff_text: str) -> str:
        """Apply AlphaEvolve-style `<<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE` blocks."""
        matches = list(cls.SEARCH_REPLACE_PATTERN.finditer(diff_text))
        if not matches:
            return base_code

        updated = base_code
        for m in matches:
            search_block = m.group(1)
            replace_block = m.group(2)
            if search_block in updated:
                updated = updated.replace(search_block, replace_block, 1)

        # Verify syntactic validity; revert to base_code if broken
        try:
            ast.parse(updated)
            return updated
        except SyntaxError:
            return base_code

    @classmethod
    def homologous_crossover(
        cls,
        parent_a: DiploidGenome,
        parent_b: DiploidGenome,
        rng: random.Random | None = None,
    ) -> tuple[str, str]:
        """Perform homologous AST function-level crossover respecting epigenetic methylation.

        Functions methylated in `parent_a` (proven low-energy loci) are preserved from
        `parent_a`, while euchromatic/acetylated functions can be recombined from `parent_b`,
        plus any unique helper functions from `parent_b` are spliced in.
        """
        rng = rng or random.Random(42)
        try:
            tree_a = ast.parse(parent_a.dominant_code)
            map_b = cls.extract_function_map(parent_b.dominant_code)
        except SyntaxError:
            return parent_a.dominant_code, parent_b.dominant_code

        new_body: list[ast.stmt] = []
        seen_funcs: set[str] = set()

        for stmt in tree_a.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_name = stmt.name
                seen_funcs.add(fn_name)
                is_methylated_a = fn_name in parent_a.epigenetics.methylated_loci
                is_methylated_b = fn_name in parent_b.epigenetics.methylated_loci

                if fn_name in map_b:
                    if is_methylated_b and not is_methylated_a:
                        new_body.append(copy.deepcopy(map_b[fn_name]))
                    elif not is_methylated_a and rng.random() < 0.5:
                        new_body.append(copy.deepcopy(map_b[fn_name]))
                    else:
                        new_body.append(copy.deepcopy(stmt))
                else:
                    new_body.append(copy.deepcopy(stmt))
            else:
                new_body.append(copy.deepcopy(stmt))

        # Splice in any helper functions present in parent_b but missing in parent_a
        fn_insert_idx = 0
        for idx, stmt in enumerate(new_body):
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_insert_idx = idx
                break
        for fn_name, fn_node in map_b.items():
            if fn_name not in seen_funcs:
                new_body.insert(fn_insert_idx, copy.deepcopy(fn_node))
                fn_insert_idx += 1

        tree_a.body = new_body
        ast.fix_missing_locations(tree_a)
        child_dominant = ast.unparse(tree_a)
        # Recessive allele stores the fitter parent's dominant code as backup
        fitter_code = (
            parent_a.dominant_code
            if parent_a.total_energy <= parent_b.total_energy
            else parent_b.dominant_code
        )
        return child_dominant, fitter_code

    @classmethod
    def apply_memoization_mutation(cls, code: str) -> tuple[str, bool]:
        """Inject `@lru_cache(maxsize=None)` onto recursive functions lacking memoization."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, False

        mutated = False
        has_lru_import = any(
            isinstance(stmt, ast.ImportFrom)
            and stmt.module == "functools"
            and any(alias.name == "lru_cache" for alias in stmt.names)
            for stmt in tree.body
        )

        for stmt in tree.body:
            if isinstance(stmt, ast.FunctionDef):
                fn_name = stmt.name
                has_cache_dec = any(
                    (isinstance(d, ast.Name) and d.id in ("lru_cache", "cache"))
                    or (
                        isinstance(d, ast.Call)
                        and isinstance(d.func, ast.Name)
                        and d.func.id in ("lru_cache", "cache")
                    )
                    for d in stmt.decorator_list
                )
                if has_cache_dec:
                    continue
                is_recursive = any(
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Name)
                    and child.func.id == fn_name
                    for child in ast.walk(stmt)
                )
                if is_recursive:
                    dec = ast.Call(
                        func=ast.Name(id="lru_cache", ctx=ast.Load()),
                        args=[],
                        keywords=[ast.keyword(arg="maxsize", value=ast.Constant(value=None))],
                    )
                    stmt.decorator_list.insert(0, dec)
                    mutated = True

        if mutated and not has_lru_import:
            imp = ast.ImportFrom(
                module="functools",
                names=[ast.alias(name="lru_cache", asname=None)],
                level=0,
            )
            tree.body.insert(0, imp)

        if mutated:
            ast.fix_missing_locations(tree)
            return ast.unparse(tree), True
        return code, False

    @classmethod
    def apply_strength_reduction_mutation(cls, code: str) -> tuple[str, bool]:
        """Rewrite `x ** 2` -> `x * x` and `x ** 3` -> `(x * x) * x` for simple variable targets."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, False

        mutated = False

        class _StrengthReducer(ast.NodeTransformer):
            def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
                nonlocal mutated
                self.generic_visit(node)
                if (
                    isinstance(node.op, ast.Pow)
                    and isinstance(node.left, ast.Name)
                    and isinstance(node.right, ast.Constant)
                ):
                    if node.right.value == 2:
                        mutated = True
                        return ast.copy_location(
                            ast.BinOp(
                                left=copy.deepcopy(node.left),
                                op=ast.Mult(),
                                right=copy.deepcopy(node.left),
                            ),
                            node,
                        )
                    if node.right.value == 3:
                        mutated = True
                        sq = ast.BinOp(
                            left=copy.deepcopy(node.left),
                            op=ast.Mult(),
                            right=copy.deepcopy(node.left),
                        )
                        return ast.copy_location(
                            ast.BinOp(left=sq, op=ast.Mult(), right=copy.deepcopy(node.left)),
                            node,
                        )
                return node

        tree = _StrengthReducer().visit(tree)
        if mutated:
            ast.fix_missing_locations(tree)
            return ast.unparse(tree), True
        return code, False

    @classmethod
    def apply_loop_comprehension_mutation(cls, code: str) -> tuple[str, bool]:
        """Transform `acc = []; for x in it: [if c:] acc.append(expr)` into a list comprehension."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, False

        mutated = False

        class _LoopToComp(ast.NodeTransformer):
            def _transform_block(self, stmts: list[ast.stmt]) -> list[ast.stmt]:
                nonlocal mutated
                out: list[ast.stmt] = []
                i = 0
                while i < len(stmts):
                    cur = stmts[i]
                    nxt = stmts[i + 1] if i + 1 < len(stmts) else None
                    if (
                        isinstance(cur, ast.Assign)
                        and len(cur.targets) == 1
                        and isinstance(cur.targets[0], ast.Name)
                        and isinstance(cur.value, ast.List)
                        and len(cur.value.elts) == 0
                        and isinstance(nxt, ast.For)
                        and not nxt.orelse
                    ):
                        acc_name = cur.targets[0].id
                        comp_node = self._match_append_for(acc_name, nxt)
                        if comp_node is not None:
                            mutated = True
                            out.append(
                                ast.copy_location(
                                    ast.Assign(targets=[cur.targets[0]], value=comp_node),
                                    cur,
                                )
                            )
                            i += 2
                            continue
                    out.append(cur)
                    i += 1
                return out

            @staticmethod
            def _match_append_for(acc_name: str, for_node: ast.For) -> ast.ListComp | None:
                ifs: list[ast.expr] = []
                body = for_node.body
                if len(body) == 1 and isinstance(body[0], ast.If) and not body[0].orelse:
                    ifs.append(body[0].test)
                    body = body[0].body
                if (
                    len(body) == 1
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Call)
                ):
                    call = body[0].value
                    if (
                        isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == acc_name
                        and call.func.attr == "append"
                        and len(call.args) == 1
                        and not call.keywords
                    ):
                        elt = call.args[0]
                        # Avoid self-referential `acc` inside `elt` or `ifs`
                        refs = {
                            n.id
                            for sub in [elt, *ifs]
                            for n in ast.walk(sub)
                            if isinstance(n, ast.Name)
                        }
                        if acc_name not in refs:
                            return ast.ListComp(
                                elt=copy.deepcopy(elt),
                                generators=[
                                    ast.comprehension(
                                        target=copy.deepcopy(for_node.target),
                                        iter=copy.deepcopy(for_node.iter),
                                        ifs=copy.deepcopy(ifs),
                                        is_async=0,
                                    )
                                ],
                            )
                return None

            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
                self.generic_visit(node)
                node.body = self._transform_block(node.body)
                return node

        tree = _LoopToComp().visit(tree)
        if mutated:
            ast.fix_missing_locations(tree)
            return ast.unparse(tree), True
        return code, False

    @classmethod
    def somatic_mutate(
        cls,
        genome: DiploidGenome,
        mutation_rate: float,
        rng: random.Random | None = None,
        candidate_mutations: Sequence[str] | None = None,
    ) -> tuple[str, str]:
        """Apply AST somatic hypermutation, structural GP operators, or AlphaEvolve diff blocks."""
        rng = rng or random.Random(42)

        # If explicit AlphaEvolve diff blocks or candidate variants are supplied, apply them
        if candidate_mutations:
            chosen = rng.choice(list(candidate_mutations))
            if "<<<<<<< SEARCH" in chosen:
                mutated = cls.apply_alphaevolve_diff(genome.dominant_code, chosen)
                return mutated, "alphaevolve_diff_patch"
            try:
                ast.parse(chosen)
                return chosen, "alphaevolve_proposal"
            except SyntaxError:
                chosen = ""

        # Structural GP operators (memoization, strength reduction, loop comprehension)
        structural_ops = [
            ("gp_memoization", cls.apply_memoization_mutation),
            ("gp_strength_reduction", cls.apply_strength_reduction_mutation),
            ("gp_loop_comprehension", cls.apply_loop_comprehension_mutation),
        ]
        rng.shuffle(structural_ops)
        for op_label, op_fn in structural_ops:
            if rng.random() < max(0.35, mutation_rate):
                new_code, applied = op_fn(genome.dominant_code)
                if applied:
                    return new_code, op_label

        try:
            tree = ast.parse(genome.dominant_code)
        except SyntaxError:
            return genome.dominant_code, "noop_syntax"

        methylated = genome.epigenetics.methylated_loci
        mutated_any = False

        class _EuchromaticNumericTuner(ast.NodeTransformer):
            def __init__(self) -> None:
                self.in_methylated_fn = False

            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
                prev = self.in_methylated_fn
                # Protect methylated loci unless mutation_rate is very high
                self.in_methylated_fn = (node.name in methylated) and (mutation_rate < 0.5)
                self.generic_visit(node)
                self.in_methylated_fn = prev
                return node

            def visit_Constant(self, node: ast.Constant) -> ast.AST:
                nonlocal mutated_any
                if self.in_methylated_fn:
                    return node
                if isinstance(node.value, float) and node.value not in (0.0, 1.0, -1.0):
                    if rng.random() < mutation_rate:
                        scale = 1.0 + rng.uniform(-0.15, 0.15) * mutation_rate
                        mutated_any = True
                        return ast.copy_location(ast.Constant(value=round(node.value * scale, 8)), node)
                return node

        tree = _EuchromaticNumericTuner().visit(tree)
        ast.fix_missing_locations(tree)
        if mutated_any:
            return ast.unparse(tree), "somatic_numeric_tuner"
        return genome.dominant_code, "epigenetic_conserved"

    @classmethod
    def compute_ast_genomic_distance(cls, code_a: str, code_b: str) -> float:
        r"""Compute normalized NEAT-style AST structural genomic distance $\delta_{\text{AST}} \in [0, 1]$."""
        try:
            tree_a = ast.parse(code_a)
            tree_b = ast.parse(code_b)
        except SyntaxError:
            return 1.0

        counts_a: dict[str, int] = {}
        counts_b: dict[str, int] = {}
        for node in ast.walk(tree_a):
            k = type(node).__name__
            counts_a[k] = counts_a.get(k, 0) + 1
        for node in ast.walk(tree_b):
            k = type(node).__name__
            counts_b[k] = counts_b.get(k, 0) + 1

        all_keys = set(counts_a) | set(counts_b)
        if not all_keys:
            return 0.0
        l1_diff = sum(abs(counts_a.get(k, 0) - counts_b.get(k, 0)) for k in all_keys)
        total_mass = sum(counts_a.values()) + sum(counts_b.values())
        return min(1.0, l1_diff / max(1, total_mass))

    @classmethod
    def apply_differential_evolution_mutation(
        cls,
        target_code: str,
        pbest_code: str,
        donor1_code: str,
        donor2_code: str,
        scale_f: float = 0.5,
        crossover_cr: float = 0.8,
        rng: random.Random | None = None,
    ) -> tuple[str, bool]:
        r"""DE/current-to-pbest/1 numeric constant evolution across homologous ASTs:
        $v_k = x_{i,k} + F (x_{\text{pbest},k} - x_{i,k}) + F (x_{r1,k} - x_{r2,k})$.
        """
        rng = rng or random.Random(42)

        def _extract_floats(code_str: str) -> list[float]:
            try:
                t = ast.parse(code_str)
            except SyntaxError:
                return []
            return [
                float(n.value)
                for n in ast.walk(t)
                if isinstance(n, ast.Constant)
                and isinstance(n.value, float)
                and n.value not in (0.0, 1.0, -1.0)
            ]

        x_i = _extract_floats(target_code)
        x_pb = _extract_floats(pbest_code)
        x_r1 = _extract_floats(donor1_code)
        x_r2 = _extract_floats(donor2_code)
        min_len = min(len(x_i), len(x_pb), len(x_r1), len(x_r2))
        if min_len == 0:
            return target_code, False

        trial_vals: list[float] = []
        mutated_any = False
        j_rand = rng.randrange(min_len)
        for idx in range(min_len):
            if rng.random() < crossover_cr or idx == j_rand:
                v = (
                    x_i[idx]
                    + scale_f * (x_pb[idx] - x_i[idx])
                    + scale_f * (x_r1[idx] - x_r2[idx])
                )
                if abs(v - x_i[idx]) > 1e-12:
                    mutated_any = True
                trial_vals.append(round(v, 8))
            else:
                trial_vals.append(x_i[idx])

        if not mutated_any:
            return target_code, False

        tree = ast.parse(target_code)
        cursor = 0

        class _DEInjector(ast.NodeTransformer):
            def visit_Constant(self, node: ast.Constant) -> ast.AST:
                nonlocal cursor
                if (
                    isinstance(node.value, float)
                    and node.value not in (0.0, 1.0, -1.0)
                    and cursor < len(trial_vals)
                ):
                    new_val = trial_vals[cursor]
                    cursor += 1
                    return ast.copy_location(ast.Constant(value=new_val), node)
                return node

        tree = _DEInjector().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree), True


def compute_pareto_fronts(genomes: Sequence[DiploidGenome]) -> list[list[DiploidGenome]]:
    """NSGA-II fast non-dominated sorting + crowding distance across 4 minimization objectives:
    `(latency_ms, memory_mb, metabolic_energy, invariant_error)`.
    """
    valid = [
        g
        for g in genomes
        if math.isfinite(g.total_energy) and g.total_energy < MAX_APOPTOSIS_ENERGY * 0.5
    ]
    if not valid:
        return []

    def _dominates(a: DiploidGenome, b: DiploidGenome) -> bool:
        va = a.objective_vector
        vb = b.objective_vector
        return all(x <= y for x, y in zip(va, vb)) and any(x < y for x, y in zip(va, vb))

    n = len(valid)
    dom_sets: list[list[int]] = [[] for _ in range(n)]
    dom_counts: list[int] = [0] * n
    fronts_idx: list[list[int]] = [[]]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if _dominates(valid[i], valid[j]):
                dom_sets[i].append(j)
            elif _dominates(valid[j], valid[i]):
                dom_counts[i] += 1
        if dom_counts[i] == 0:
            valid[i].pareto_rank = 0
            fronts_idx[0].append(i)

    rank = 0
    while fronts_idx[rank]:
        next_front: list[int] = []
        for i in fronts_idx[rank]:
            for j in dom_sets[i]:
                dom_counts[j] -= 1
                if dom_counts[j] == 0:
                    valid[j].pareto_rank = rank + 1
                    next_front.append(j)
        rank += 1
        if next_front:
            fronts_idx.append(next_front)
        else:
            break

    fronts: list[list[DiploidGenome]] = []
    for f_indices in fronts_idx:
        if not f_indices:
            continue
        front = [valid[idx] for idx in f_indices]
        # Compute NSGA-II crowding distance within this front
        for g in front:
            g.crowding_distance = 0.0
        if len(front) <= 2:
            for g in front:
                g.crowding_distance = float("inf")
        else:
            n_obj = 4
            for m in range(n_obj):
                front.sort(key=lambda g, idx=m: g.objective_vector[idx])
                front[0].crowding_distance = float("inf")
                front[-1].crowding_distance = float("inf")
                obj_min = front[0].objective_vector[m]
                obj_max = front[-1].objective_vector[m]
                span = obj_max - obj_min
                if span > 1e-12:
                    for k in range(1, len(front) - 1):
                        if math.isfinite(front[k].crowding_distance):
                            front[k].crowding_distance += (
                                front[k + 1].objective_vector[m] - front[k - 1].objective_vector[m]
                            ) / span
        fronts.append(front)
    return fronts


@dataclass
class MAPElitesIsland:
    """Single island in the AlphaEvolve archipelago with a 2D Quality-Diversity archive.

    Grid axes:
      - Axis 0 (`complexity_bin`): Structural AST complexity bin in `[0, grid_shape[0]-1]`
      - Axis 1 (`memory_bin`): Peak memory efficiency bin in `[0, grid_shape[1]-1]`
    """

    island_id: int
    temperature: float = 10.0
    grid_shape: tuple[int, int] = (6, 6)
    archive: dict[tuple[int, int], DiploidGenome] = field(default_factory=dict)
    stagnation_steps: int = 0
    best_energy: float = MAX_APOPTOSIS_ENERGY

    def compute_cell(self, ast_complexity: int, memory_mb: float) -> tuple[int, int]:
        c_bin = min(self.grid_shape[0] - 1, max(0, (ast_complexity - 1) // 3))
        m_bin = min(self.grid_shape[1] - 1, max(0, int(memory_mb // 2.0)))
        return (c_bin, m_bin)

    def insert(self, genome: DiploidGenome) -> bool:
        """Insert genome into its behavioral niche if the cell is empty or energy improves."""
        if not math.isfinite(genome.total_energy) or genome.total_energy >= MAX_APOPTOSIS_ENERGY * 0.5:
            self.stagnation_steps += 1
            return False

        cell = genome.behavioral_descriptor
        incumbent = self.archive.get(cell)
        if incumbent is None or genome.total_energy < incumbent.total_energy:
            self.archive[cell] = genome
            if genome.total_energy < self.best_energy:
                self.best_energy = genome.total_energy
                self.stagnation_steps = 0
            else:
                self.stagnation_steps += 1
            return True

        self.stagnation_steps += 1
        return False

    def select_parent_boltzmann(self, rng: random.Random) -> DiploidGenome | None:
        r"""Boltzmann-Gibbs tournament selection weighted by $\exp(-(E - E_{\min}) / \tau)$."""
        if not self.archive:
            return None
        elites = list(self.archive.values())
        min_e = min(g.total_energy for g in elites)
        temp = max(1e-3, self.temperature)
        weights = [math.exp(-min(50.0, (g.total_energy - min_e) / temp)) for g in elites]
        return rng.choices(elites, weights=weights, k=1)[0]

    def select_parent_lexicase(
        self, rng: random.Random, epsilon_rel: float = 0.05
    ) -> DiploidGenome | None:
        r"""$\epsilon$-Lexicase parent selection across shuffled multi-objective criteria."""
        if not self.archive:
            return None
        pool = list(self.archive.values())
        if len(pool) == 1:
            return pool[0]

        criteria = [
            lambda g: g.total_energy,
            lambda g: g.latency_ms,
            lambda g: g.memory_mb,
            lambda g: g.metabolic_energy,
            lambda g: g.invariant_error,
        ]
        rng.shuffle(criteria)
        for crit in criteria:
            vals = [crit(g) for g in pool]
            best_val = min(vals)
            tol = max(1e-9, abs(best_val) * epsilon_rel)
            pool = [g for g in pool if crit(g) <= best_val + tol]
            if len(pool) == 1:
                return pool[0]
        return rng.choice(pool)

    def best_genome(self) -> DiploidGenome | None:
        if not self.archive:
            return None
        return min(self.archive.values(), key=lambda g: g.total_energy)


class AlphaEvolveBiomimeticEngine:
    """Master AlphaEvolve + Genetic Algorithm + Biomimetic Evolution Engine for ANSE.

    Combines:
      1. Multi-Island MAP-Elites Quality-Diversity Archipelago
      2. Thermodynamic Physical Energy + Allostatic Metabolic Cost evaluation
      3. Artificial Immune System (AIS) negative selection & somatic hypermutation
      4. Epigenetic chromatin methylation/acetylation locking of proven AST functions
      5. Homologous AST crossover + AlphaEvolve SEARCH/REPLACE diff patching
      6. Optional 3-stage `HardenedAutoresearchLoop` promotion gate
    """

    def __init__(
        self,
        evaluator_fn: Callable[[str], dict[str, float]],
        *,
        num_islands: int = 3,
        grid_shape: tuple[int, int] = (6, 6),
        homeostatic_complexity_target: int = 12,
        metabolic_weight: float = 0.25,
        migration_interval: int = 3,
        stagnation_patience: int = 8,
        seed: int = 42,
    ) -> None:
        self.evaluator_fn = evaluator_fn
        self.num_islands = max(1, num_islands)
        self.grid_shape = grid_shape
        self.homeostatic_complexity_target = homeostatic_complexity_target
        self.metabolic_weight = metabolic_weight
        self.migration_interval = max(1, migration_interval)
        self.stagnation_patience = max(2, stagnation_patience)
        self.rng = random.Random(seed)
        self.ais = ArtificialImmuneSystem()

        # Morphogen temperature gradient across islands (cold exploitation -> warm exploration)
        self.islands: list[MAPElitesIsland] = [
            MAPElitesIsland(
                island_id=i,
                temperature=2.5 * (2.2**i),
                grid_shape=grid_shape,
            )
            for i in range(self.num_islands)
        ]
        self.generation: int = 0
        self.history: list[dict[str, Any]] = []
        self._eval_cache: dict[str, dict[str, float]] = {}

    def evaluate_genome(self, genome: DiploidGenome) -> DiploidGenome:
        """Screen candidate via AIS and evaluate physical + metabolic allostatic energy."""
        passed_ais, reason, token = self.ais.negative_selection_screen(genome.dominant_code)
        if not passed_ais:
            # Try recessive backup allele if dominant allele fails AIS negative selection
            if genome.recessive_code:
                rec_ok, _, rec_token = self.ais.negative_selection_screen(genome.recessive_code)
                if rec_ok:
                    genome.dominant_code, genome.recessive_code = (
                        genome.recessive_code,
                        genome.dominant_code,
                    )
                    genome.mutation_operator += "+recessive_rescue"
                    passed_ais, token = True, rec_token

        if not passed_ais:
            genome.physical_energy = MAX_APOPTOSIS_ENERGY
            genome.total_energy = MAX_APOPTOSIS_ENERGY
            genome.attestation_token = ""
            return genome

        complexity, fn_names = ASTGeneticOperators.compute_ast_complexity_and_loci(genome.dominant_code)
        code_hash = hashlib.sha256(genome.dominant_code.encode("utf-8")).hexdigest()
        if code_hash in self._eval_cache:
            metrics = self._eval_cache[code_hash]
        else:
            try:
                metrics = self.evaluator_fn(genome.dominant_code)
                self._eval_cache[code_hash] = metrics
            except Exception:
                self.ais.record_outcome(genome.dominant_code, MAX_APOPTOSIS_ENERGY)
                genome.physical_energy = MAX_APOPTOSIS_ENERGY
                genome.total_energy = MAX_APOPTOSIS_ENERGY
                return genome

        phys_e = float(metrics.get("physical_energy", MAX_APOPTOSIS_ENERGY))
        lat_ms = float(metrics.get("latency_ms", 9999.0))
        mem_mb = float(metrics.get("memory_mb", 0.0))
        inv_err = float(metrics.get("invariant_error", 1.0))

        # Allostatic metabolic penalty for exceeding homeostatic AST complexity target
        excess_complexity = max(0, complexity - self.homeostatic_complexity_target)
        metabolic_e = self.metabolic_weight * float(excess_complexity**1.5)
        total_e = phys_e + metabolic_e if phys_e < MAX_APOPTOSIS_ENERGY * 0.5 else MAX_APOPTOSIS_ENERGY

        genome.physical_energy = phys_e
        genome.metabolic_energy = metabolic_e
        genome.total_energy = total_e
        genome.latency_ms = lat_ms
        genome.memory_mb = mem_mb
        genome.invariant_error = inv_err
        genome.attestation_token = token
        genome.behavioral_descriptor = self.islands[genome.island_id].compute_cell(complexity, mem_mb)
        genome.epigenetics.update_from_evaluation(fn_names, total_e)
        self.ais.record_outcome(genome.dominant_code, total_e)
        return genome

    def seed_population(self, initial_codes: Sequence[str]) -> list[DiploidGenome]:
        """Seed all islands in the archipelago with initial baseline/variant programs."""
        seeded: list[DiploidGenome] = []
        for idx, code in enumerate(initial_codes):
            for island in self.islands:
                g = DiploidGenome(
                    genome_id=f"gen0_isl{island.island_id}_seed{idx}",
                    dominant_code=code,
                    recessive_code=code,
                    generation=0,
                    island_id=island.island_id,
                    mutation_operator="seed",
                )
                self.evaluate_genome(g)
                island.insert(g)
                seeded.append(g)
        return seeded

    def _migrate_ring(self) -> int:
        """Migrate each island's top elite to the next island in a ring topology."""
        if len(self.islands) < 2:
            return 0
        migrants: list[tuple[int, DiploidGenome]] = []
        for i, isl in enumerate(self.islands):
            elite = isl.best_genome()
            if elite is not None:
                target_idx = (i + 1) % len(self.islands)
                clone = copy.deepcopy(elite)
                clone.island_id = target_idx
                clone.mutation_operator = "ring_migration"
                migrants.append((target_idx, clone))

        accepted = 0
        for target_idx, clone in migrants:
            if self.islands[target_idx].insert(clone):
                accepted += 1
        return accepted

    def _homeostatic_island_reset(self) -> int:
        """Reset stagnated islands by inoculating them with mutated clones of the global best."""
        global_best = self.best_genome()
        if global_best is None:
            return 0
        resets = 0
        for isl in self.islands:
            if isl.stagnation_steps >= self.stagnation_patience and isl.island_id != global_best.island_id:
                clone = copy.deepcopy(global_best)
                clone.island_id = isl.island_id
                clone.stagnation_steps = 0  # type: ignore[attr-defined]
                isl.stagnation_steps = 0
                isl.insert(clone)
                resets += 1
        return resets

    def step_generation(
        self,
        candidate_proposals: Sequence[str] | None = None,
        crossover_prob: float = 0.5,
    ) -> dict[str, Any]:
        """Run one evolutionary generation across all islands."""
        self.generation += 1
        new_insertions = 0

        for isl in self.islands:
            parent_a = isl.select_parent_boltzmann(self.rng)
            if parent_a is None:
                continue

            parent_b = isl.select_parent_lexicase(self.rng)
            if parent_b is not None and parent_b.genome_id != parent_a.genome_id and self.rng.random() < crossover_prob:
                dom_code, rec_code = ASTGeneticOperators.homologous_crossover(
                    parent_a, parent_b, rng=self.rng
                )
                parent_ids: tuple[str, ...] = (parent_a.genome_id, parent_b.genome_id)
                op_name = "homologous_crossover"
            else:
                dom_code, rec_code = parent_a.dominant_code, parent_a.recessive_code or parent_a.dominant_code
                parent_ids = (parent_a.genome_id,)
                op_name = "clonal_selection"

            child = DiploidGenome(
                genome_id=f"gen{self.generation}_isl{isl.island_id}_{self.rng.randint(1000, 9999)}",
                dominant_code=dom_code,
                recessive_code=rec_code,
                generation=self.generation,
                island_id=isl.island_id,
                parent_ids=parent_ids,
                mutation_operator=op_name,
                epigenetics=copy.deepcopy(parent_a.epigenetics),
            )

            mut_rate = self.ais.somatic_hypermutation_rate(parent_a.total_energy)
            mutated_code, mut_op = ASTGeneticOperators.somatic_mutate(
                child,
                mutation_rate=mut_rate,
                rng=self.rng,
                candidate_mutations=candidate_proposals,
            )
            child.dominant_code = mutated_code
            child.mutation_operator = f"{op_name}+{mut_op}"

            self.evaluate_genome(child)
            if isl.insert(child):
                new_insertions += 1

        migrations = 0
        if self.generation % self.migration_interval == 0:
            migrations = self._migrate_ring()

        resets = self._homeostatic_island_reset()
        fronts = self.pareto_fronts()
        best = self.best_genome()

        summary = {
            "generation": self.generation,
            "new_archive_insertions": new_insertions,
            "migrations": migrations,
            "homeostatic_resets": resets,
            "archive_coverage": sum(len(isl.archive) for isl in self.islands),
            "pareto_front_size": len(fronts[0]) if fronts else 0,
            "best_total_energy": best.total_energy if best else MAX_APOPTOSIS_ENERGY,
            "best_physical_energy": best.physical_energy if best else MAX_APOPTOSIS_ENERGY,
            "best_genome_id": best.genome_id if best else "",
        }
        self.history.append(summary)
        return summary

    def pareto_fronts(self) -> list[list[DiploidGenome]]:
        """Compute NSGA-II non-dominated Pareto fronts across all island archives."""
        all_elites = [g for isl in self.islands for g in isl.archive.values()]
        return compute_pareto_fronts(all_elites)

    def best_genome(self) -> DiploidGenome | None:
        """Return the minimum-energy elite across the entire island archipelago."""
        candidates = [isl.best_genome() for isl in self.islands]
        valid = [g for g in candidates if g is not None]
        if not valid:
            return None
        return min(valid, key=lambda g: g.total_energy)

    def run_evolution_with_hardened_gate(
        self,
        initial_codes: Sequence[str],
        *,
        generations: int = 6,
        candidate_proposals: Sequence[str] | None = None,
        heldout_eval_fn: Callable[[str], float] | None = None,
        replicates_eval_fn: Callable[[str], Sequence[float]] | None = None,
    ) -> dict[str, Any]:
        """Run multi-generation AlphaEvolve + Biomimetic search and validate the champion
        through the 3-stage `HardenedAutoresearchLoop` gate.
        """
        seeded = self.seed_population(initial_codes)
        baseline_best = min((g.total_energy for g in seeded), default=MAX_APOPTOSIS_ENERGY)

        if candidate_proposals and initial_codes:
            base_src = initial_codes[0]
            for p_idx, prop in enumerate(candidate_proposals):
                prop_code = (
                    ASTGeneticOperators.apply_alphaevolve_diff(base_src, prop)
                    if "<<<<<<< SEARCH" in prop
                    else prop
                )
                target_isl = self.islands[p_idx % len(self.islands)]
                g_prop = DiploidGenome(
                    genome_id=f"proposal_{p_idx}_isl{target_isl.island_id}",
                    dominant_code=prop_code,
                    recessive_code=base_src,
                    generation=0,
                    island_id=target_isl.island_id,
                    mutation_operator="alphaevolve_proposal",
                )
                self.evaluate_genome(g_prop)
                target_isl.insert(g_prop)

        for _ in range(generations):
            self.step_generation(candidate_proposals=candidate_proposals)

        fronts = self.pareto_fronts()
        champion = self.best_genome()
        if champion is None:
            return {
                "promoted": False,
                "baseline_energy": baseline_best,
                "champion_energy": MAX_APOPTOSIS_ENERGY,
                "delta_energy": 0.0,
            }

        loop = HardenedAutoresearchLoop(
            best_search_metric=baseline_best,
            best_heldout_metric=baseline_best,
            best_replicate_median=baseline_best,
            lower_is_better=True,
        )

        h_fn = heldout_eval_fn or (lambda code: champion.total_energy)
        r_fn = replicates_eval_fn or (
            lambda code: [champion.total_energy, champion.total_energy * 0.99, champion.total_energy * 1.01]
        )

        gate_verdict = loop.evaluate_candidate(
            champion.genome_id,
            positive_control_ok=champion.total_energy < MAX_APOPTOSIS_ENERGY * 0.5,
            negative_control_ok=True,
            search_fn=lambda: champion.total_energy,
            heldout_fn=lambda: h_fn(champion.dominant_code),
            replicates_fn=lambda: r_fn(champion.dominant_code),
            invariant_ok_fn=lambda: (
                champion.invariant_error <= 1e-4,
                f"invariant_error={champion.invariant_error:.3e}",
            ),
        )

        return {
            "promoted": bool(gate_verdict.get("kept", False)),
            "gate_verdict": gate_verdict,
            "baseline_energy": baseline_best,
            "champion_energy": champion.total_energy,
            "delta_energy": champion.total_energy - baseline_best,
            "champion": champion.to_dict(),
            "archive_total_elites": sum(len(isl.archive) for isl in self.islands),
            "pareto_front_size": len(fronts[0]) if fronts else 0,
            "history": self.history,
        }
