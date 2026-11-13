#!/usr/bin/env python3
"""Does recombination beat mutation when the gate is a Lean proof?

Three rounds of this programme asked whether recombination is DETECTABLE in
evolved programs and refuted it each time: behavioural profiles are not
heritable (Paper H, 0/24, 0/23, 0/22 against clonal floors), the address-indexed
ablation contribution is not a site-wise heritable character (0.200-0.545
transmitted against a 0.70 bar), and a mutation-only arm -- a tree by
construction -- carries quartet certificates at the same rate as a crossover
arm. None of them asked the prior question: does recombination HELP?

It was too expensive to ask. A verified answer needs a formal gate, and the gate
cost one Lean invocation per candidate, so a paired experiment over hundreds of
candidates meant hours of Lean. It now costs one invocation per BATCH -- a Lean
compile reports a per-declaration verdict even when it exits nonzero, so a batch
of eight is one invocation at any failure rate -- which brings the experiment
inside a few minutes.

THE ARCHITECTURE, and why it is sound. Fitness is exact rational agreement with
the spec at sample points, computed in Python over `Fraction`, costing no Lean
at all. Acceptance is the Lean kernel. Those are deliberately different things:
a wrong Python fitness would MISGUIDE the search and waste effort, but it can
never cause a wrong acceptance, because nothing is accepted without a proof
whose `#print axioms` line is free of `sorryAx` and of non-whitelisted axioms.
Fitness guides, the kernel decides.

The genome is an expression tree, so it is evaluated in its native
representation and never parsed back out of Lean source. Rendering to Lean
happens once, for candidates that already achieve exact agreement.

CONTROLS, pre-registered.
  * Positive: the target `qNext` is REACHABLE in this grammar, so an arm that
    never solves it is broken rather than informative. The exact target
    expression is constructed and checked to score zero before any arm runs.
  * Negative: a target that is NOT reachable (it needs an operator outside the
    grammar) must never be solved by any arm, and must never pass the Lean gate.
    An arm that "solves" it has a bug in fitness or in the gate.
  * Paired: both arms get identical seeds, identical initial populations and an
    identical evaluation budget. The only difference is whether crossover is
    used. A difference that appears only because one arm drew luckier seeds is
    what pairing removes.
  * The comparison can go either way and the abandonment criterion is stated
    before running: if the crossover arm's median evaluations-to-solution is not
    at least 10% below the mutation-only arm's across seeds, recombination does
    not help here and that is the result.

Usage:
    .venv/bin/python scripts/lean_gated_recombination.py \\
        --seeds 24 --budget 4000 --out results/lean_gated_recombination.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import subprocess
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Callable, Sequence

REPO = Path(__file__).resolve().parents[1]
FORMAL = REPO / "formal"

VARIABLES: tuple[str, ...] = ("h", "w", "q", "p")
CONSTANTS: tuple[Fraction, ...] = (Fraction(1), Fraction(2), Fraction(1, 2))
BINARY_OPS: tuple[str, ...] = ("+", "-", "*")


@dataclass(frozen=True)
class Node:
    """An expression tree node: either a leaf (op is None) or a binary operator."""

    op: str | None
    left: "Node | None" = None
    right: "Node | None" = None
    leaf: str | Fraction | None = None

    def size(self) -> int:
        if self.op is None:
            return 1
        assert self.left is not None and self.right is not None
        return 1 + self.left.size() + self.right.size()


def leaf(value: str | Fraction) -> Node:
    return Node(op=None, leaf=value)


def binary(op: str, left: Node, right: Node) -> Node:
    return Node(op=op, left=left, right=right)


def evaluate(node: Node, env: dict[str, Fraction]) -> Fraction:
    """Exact rational evaluation. No floats anywhere in the fitness path."""
    if node.op is None:
        if isinstance(node.leaf, Fraction):
            return node.leaf
        assert isinstance(node.leaf, str)
        return env[node.leaf]
    assert node.left is not None and node.right is not None
    a = evaluate(node.left, env)
    b = evaluate(node.right, env)
    if node.op == "+":
        return a + b
    if node.op == "-":
        return a - b
    if node.op == "*":
        return a * b
    raise ValueError(f"unknown operator {node.op!r}")


def render_lean(node: Node) -> str:
    """Render to a Lean term. Fully parenthesised, so precedence cannot differ."""
    if node.op is None:
        if isinstance(node.leaf, Fraction):
            if node.leaf.denominator == 1:
                return f"({node.leaf.numerator} : Rat)"
            return f"(({node.leaf.numerator} : Rat)/{node.leaf.denominator})"
        return str(node.leaf)
    assert node.left is not None and node.right is not None
    return f"({render_lean(node.left)} {node.op} {render_lean(node.right)})"


def target_expression() -> Node:
    """`qNext h w q p = q + h*p - (h^2 * w^2 / 2) * q`, in this grammar.

    h^2 and w^2 become h*h and w*w, and the division by two becomes a
    multiplication by the constant 1/2, so the target is reachable without
    needing `^` or `/` as operators. This is the positive control's whole point:
    an unreachable target would make every arm's failure uninformative.
    """
    h, w, q, p = (leaf(v) for v in VARIABLES)
    h2 = binary("*", h, h)
    w2 = binary("*", w, w)
    half = leaf(Fraction(1, 2))
    coeff = binary("*", binary("*", h2, w2), half)
    return binary("-", binary("+", q, binary("*", h, p)), binary("*", coeff, q))


def target_ladder() -> list[tuple[str, Node]]:
    """Reachable targets of increasing size, for calibrating difficulty.

    The first attempt put both arms at the full 17-node target and BOTH solved
    0 of 24, with the best fitness reached anywhere being about 55.4 and nothing
    under 10. That is a non-discriminating comparison: two arms failing equally
    say nothing about recombination, and reporting it as "crossover does not
    help" would be reading a result off a test that could not distinguish the
    arms. The response variable has to vary first.

    So difficulty is calibrated on the POOLED solve rate of both arms together
    and the rung is chosen where it lands in [0.3, 0.7] -- a band where either
    arm can be seen to win or lose. The criterion is pooled and fixed in advance
    on purpose: selecting the rung that flattered crossover would be choosing the
    apparatus to suit the answer, which is the defect this programme keeps
    finding in its own work.
    """
    h, w, q, p = (leaf(v) for v in VARIABLES)
    half = leaf(Fraction(1, 2))
    base = binary("+", q, binary("*", h, p))                      # q + h*p
    rungs: list[tuple[str, Node]] = [
        ("L1_base", base),
        ("L2_minus_q", binary("-", base, q)),
        ("L3_minus_wq", binary("-", base, binary("*", w, q))),
        ("L4_minus_hwq", binary("-", base, binary("*", binary("*", h, w), q))),
        ("L5_minus_half_hwq",
         binary("-", base, binary("*", binary("*", binary("*", h, w), half), q))),
        ("L6_full", target_expression()),
    ]
    return rungs


def sample_points(rng: random.Random, count: int) -> list[dict[str, Fraction]]:
    """Exact rational points, denominators bounded so arithmetic stays small."""
    points: list[dict[str, Fraction]] = []
    while len(points) < count:
        env = {
            v: Fraction(rng.randint(-9, 9), rng.randint(1, 7))
            for v in VARIABLES
        }
        if env not in points:
            points.append(env)
    return points


def fitness(node: Node, points: Sequence[dict[str, Fraction]],
            spec: Callable[[dict[str, Fraction]], Fraction]) -> Fraction:
    """Total absolute exact error over the sample points. Zero means agreement.

    Agreement is NOT equality -- that is what the Lean gate is for -- but a
    nonzero value is a witness of inequality and so a sound refutation.
    """
    total = Fraction(0)
    for env in points:
        total += abs(evaluate(node, env) - spec(env))
    return total


def random_tree(rng: random.Random, depth: int) -> Node:
    if depth <= 0 or rng.random() < 0.3:
        if rng.random() < 0.7:
            return leaf(rng.choice(VARIABLES))
        return leaf(rng.choice(CONSTANTS))
    return binary(
        rng.choice(BINARY_OPS),
        random_tree(rng, depth - 1),
        random_tree(rng, depth - 1),
    )


def all_addresses(node: Node, prefix: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    out = [prefix]
    if node.op is not None:
        assert node.left is not None and node.right is not None
        out += all_addresses(node.left, prefix + (0,))
        out += all_addresses(node.right, prefix + (1,))
    return out


def subtree_at(node: Node, address: tuple[int, ...]) -> Node:
    for step in address:
        assert node.left is not None and node.right is not None
        node = node.left if step == 0 else node.right
    return node


def replace_at(node: Node, address: tuple[int, ...], replacement: Node) -> Node:
    if not address:
        return replacement
    assert node.left is not None and node.right is not None
    step, rest = address[0], address[1:]
    if step == 0:
        return binary(node.op or "+", replace_at(node.left, rest, replacement), node.right)
    return binary(node.op or "+", node.left, replace_at(node.right, rest, replacement))


def all_context_coefficients(
    tree: Node, env: dict[str, Fraction],
) -> dict[tuple[int, ...], Fraction]:
    """Every address's coefficient B in `output = A + B * v`, in ONE pass pair.

    The first implementation computed B per address with two whole-tree
    evaluations, costing O(size) evaluations per address and O(size^2) per
    sample point. Measured, that made the homologous arms spend 5.5x the
    tree-point evaluations of the others -- a hidden cost large enough to make
    any win on fitness evaluations meaningless.

    B has exact reverse-mode structure, so it needs no such thing. Forward pass
    for every node's value; backward pass seeded with B(root) = 1, where
      '+'  sends B to both children,
      '-'  sends B left and -B right,
      '*'  sends B * value(sibling) to each child.
    That is exact rational arithmetic, O(size) per point, and it makes the
    homology probe cost about one fitness evaluation instead of hundreds.
    """
    values: dict[tuple[int, ...], Fraction] = {}

    def forward(node: Node, address: tuple[int, ...]) -> Fraction:
        if node.op is None:
            value = node.leaf if isinstance(node.leaf, Fraction) else env[str(node.leaf)]
            values[address] = value
            return value
        assert node.left is not None and node.right is not None
        a = forward(node.left, address + (0,))
        b = forward(node.right, address + (1,))
        if node.op == "+":
            out = a + b
        elif node.op == "-":
            out = a - b
        elif node.op == "*":
            out = a * b
        else:
            raise ValueError(f"unknown operator {node.op!r}")
        values[address] = out
        return out

    forward(tree, ())
    coefficients: dict[tuple[int, ...], Fraction] = {}

    def backward(node: Node, address: tuple[int, ...], upstream: Fraction) -> None:
        coefficients[address] = upstream
        if node.op is None:
            return
        assert node.left is not None and node.right is not None
        left_address = address + (0,)
        right_address = address + (1,)
        if node.op == "+":
            backward(node.left, left_address, upstream)
            backward(node.right, right_address, upstream)
        elif node.op == "-":
            backward(node.left, left_address, upstream)
            backward(node.right, right_address, -upstream)
        else:
            backward(node.left, left_address, upstream * values[right_address])
            backward(node.right, right_address, upstream * values[left_address])

    backward(tree, (), Fraction(1))
    return coefficients


def context_coefficient(
    tree: Node, address: tuple[int, ...], points: Sequence[dict[str, Fraction]],
    counter: list[int],
) -> tuple[Fraction, ...]:
    """The exact coefficient B in `output = A + B * v` for the subtree at `address`.

    In the grammar {+, -, *} an address occurs once, so the whole expression is
    AFFINE in that subtree's value v. Therefore B = f(v=1) - f(v=0), computed
    exactly in two evaluations per sample point and with no derivative
    approximation anywhere.

    B is the measured cause of crossover's failure. A donor subtree contributing
    B_donor * v inside its own parent contributes B_site * v once transplanted, so
    unless the two coefficients agree the donor's CONTRIBUTION is rescaled or
    sign-flipped even though its syntax arrived intact. That is why a subtree swap
    behaves as a macromutation, and it is what hypothesis AR.H3-gp found from the
    other direction when transfer fidelity fell with the multiplicative operators
    on the root-to-insertion path.
    """
    one = replace_at(tree, address, leaf(Fraction(1)))
    zero = replace_at(tree, address, leaf(Fraction(0)))
    counter[0] += 2 * len(points)
    return tuple(
        evaluate(one, env) - evaluate(zero, env) for env in points
    )


def sign_pattern(coefficients: Sequence[Fraction]) -> tuple[int, ...]:
    """The sign of B at each sample point: the homology signature."""
    return tuple((0 if c == 0 else (1 if c > 0 else -1)) for c in coefficients)


def homologous_crossover(
    a: Node, b: Node, rng: random.Random, max_size: int,
    points: Sequence[dict[str, Fraction]], counter: list[int], anti: bool = False,
) -> tuple[Node, bool]:
    """Recombine only where the donor's context coefficient matches the site's.

    Biology recombines at HOMOLOGOUS positions; a random subtree swap is the
    non-homologous analogue, which in biology is catastrophic rather than
    creative. Homology here is the sign pattern of B across the sample points,
    so a donor is admitted only into a site that preserves the DIRECTION of its
    contribution at every point.

    With `anti=True` it does the opposite and recombines only where the sign
    pattern is inverted. That is the negative control: if homology is what
    matters, anti-homology must do WORSE than choosing at random, and if both
    arms behave alike then the signature is not carrying anything.

    Returns the child and whether a matching site was found. When none is found
    the caller falls back to mutation, and the fallback is counted, because an
    arm that silently became mutation-only would look like a success of
    recombination.
    """
    # One forward/backward pass per sample point gives every address's
    # coefficient in both trees, so the whole probe costs about two fitness
    # evaluations rather than hundreds.
    donor_coefficients = [all_context_coefficients(b, env) for env in points]
    site_coefficients = [all_context_coefficients(a, env) for env in points]
    counter[0] += 2 * len(points)

    donor_address = rng.choice(all_addresses(b))
    donor = subtree_at(b, donor_address)
    donor_signature = sign_pattern(
        [table[donor_address] for table in donor_coefficients]
    )

    sites = all_addresses(a)
    rng.shuffle(sites)
    for site in sites:
        site_signature = sign_pattern([table[site] for table in site_coefficients])
        matches = (site_signature == donor_signature)
        if matches != anti:
            candidate = replace_at(a, site, donor)
            if candidate.size() <= max_size:
                return candidate, True
    return a, False


def constant_ratio(
    donor: Sequence[Fraction], site: Sequence[Fraction]
) -> Fraction | None:
    """The single rational k with donor = k * site at every point, or None.

    This is the condition under which a transplant can preserve the donor's
    CONTRIBUTION exactly rather than merely its direction. The donor contributes
    B_d * v inside its own parent and B_s * v at the site, so inserting k * D
    with k = B_d / B_s restores B_d * v -- but only if that ratio is the same
    rational at every sample point, since one scalar cannot correct a
    point-varying ratio.

    A point where the site coefficient is zero kills the donor's contribution
    there and cannot be corrected by any scaling, so it is admissible only if the
    donor's coefficient is zero too; then it constrains nothing.
    """
    found: Fraction | None = None
    for d, s in zip(donor, site):
        if s == 0:
            if d != 0:
                return None
            continue
        ratio = d / s
        if found is None:
            found = ratio
        elif ratio != found:
            return None
    # All-zero site coefficients: the donor is in a dead position either way.
    return found


def contribution_preserving_crossover(
    a: Node, b: Node, rng: random.Random, max_size: int,
    points: Sequence[dict[str, Fraction]], counter: list[int], rescale: bool = True,
) -> tuple[Node, bool]:
    """Transplant only where the donor's contribution can be preserved exactly.

    The successor this programme recorded as untested after matching sign(B)
    failed. A site is admissible only when the coefficient ratio is a single
    rational across every sample point; the donor is then inserted scaled by that
    ratio, so its contribution to the output is EXACTLY what it was in its own
    parent -- not merely the same sign, which is what the refuted homology arm
    matched.

    With `rescale=False` the same sites are chosen and the donor is inserted
    UNSCALED. That is the control that separates the two things this operator
    does: selecting a constant-ratio site, and correcting the contribution once
    there. If the two arms agree, the scaling is doing nothing and only the site
    selection matters; if both match plain crossover, neither does.
    """
    donor_tables = [all_context_coefficients(b, env) for env in points]
    site_tables = [all_context_coefficients(a, env) for env in points]
    counter[0] += 2 * len(points)

    donor_address = rng.choice(all_addresses(b))
    donor = subtree_at(b, donor_address)
    donor_coefficients = [table[donor_address] for table in donor_tables]

    sites = all_addresses(a)
    rng.shuffle(sites)
    for site in sites:
        site_coefficients = [table[site] for table in site_tables]
        k = constant_ratio(donor_coefficients, site_coefficients)
        if k is None:
            continue
        if rescale:
            # k == 1 needs no wrapper, which keeps the child smaller and is the
            # common case: B is 1 at every address reached through only '+' and
            # the left of '-'.
            graft = donor if k == 1 else binary("*", leaf(k), donor)
        else:
            graft = donor
        candidate = replace_at(a, site, graft)
        if candidate.size() <= max_size:
            return candidate, True
    return a, False


def required_values(
    tree: Node, address: tuple[int, ...], want: Sequence[Fraction],
    points: Sequence[dict[str, Fraction]], counter: list[int],
) -> list[Fraction | None]:
    """The value the subtree at `address` MUST take for the tree to be correct.

    Since the expression is affine in that subtree's value, out = A + B*v, and the
    forward pass already yields both v and out, the required value follows in
    closed form with nothing extra to evaluate:

        v* = v + (want - out) / B

    Verified exact: splicing v* in makes the whole tree equal the target at that
    point in 24303 of 24303 (address, point) pairs with B != 0.

    Where B == 0 the address cannot affect the output at that point at all, so
    there is no requirement to meet. Those entries are None -- genuine DON'T
    CARES, 4.8% of pairs measured, and extra freedom rather than missing data.
    This is semantic backpropagation, done in exact rationals so no step is an
    approximation.
    """
    out: list[Fraction | None] = []
    for index, env in enumerate(points):
        table = all_context_coefficients(tree, env)
        coefficient = table[address]
        if coefficient == 0:
            out.append(None)
            continue
        value = evaluate(subtree_at(tree, address), env)
        total = evaluate(tree, env)
        out.append(value + (want[index] - total) / coefficient)
    counter[0] += 3 * len(points)
    return out


def semantic_library(
    population: "Sequence[Node]", rng: random.Random,
    points: Sequence[dict[str, Fraction]], counter: list[int], sample: int = 16,
) -> list[tuple[Node, tuple[Fraction, ...]]]:
    """Subtrees paired with their exact value vectors: the search space for a splice.

    Terminals are always present, since a required vector that happens to be a
    constant or a plain variable is the cheapest possible repair. The rest is a
    BOUNDED sample of subtrees drawn from the live population, so the operator's
    cost stays proportional to `sample` rather than to the population's total
    size, and every evaluation it spends is counted.
    """
    library: list[tuple[Node, tuple[Fraction, ...]]] = []
    candidates: list[Node] = [leaf(v) for v in VARIABLES] + [leaf(c) for c in CONSTANTS]
    for _ in range(sample):
        if not population:
            break
        donor = population[rng.randrange(len(population))]
        candidates.append(subtree_at(donor, rng.choice(all_addresses(donor))))
    for node in candidates:
        library.append((node, tuple(evaluate(node, env) for env in points)))
    counter[0] += len(candidates) * len(points)
    return library


def semantic_splice(
    tree: Node, population: "Sequence[Node]", rng: random.Random, max_size: int,
    want: Sequence[Fraction], points: Sequence[dict[str, Fraction]],
    counter: list[int], use_required: bool = True,
) -> tuple[Node, bool]:
    """Replace a subtree with one whose semantics are what the position requires.

    Pick an address, compute the vector it must produce, and splice in a subtree
    from the library that produces exactly that -- matching only at the points
    that are actually constrained, since an inert point imposes nothing.

    MATCHING IS NEAREST, NOT EXACT, AND THAT WAS MEASURED RATHER THAN CHOSEN. The
    first version demanded an exact match on every constrained point and failed
    23991 times out of about 24000 attempts -- a 99.96% failure rate. A required
    vector is twelve arbitrary rationals, and essentially no library subtree
    produces exactly that, so the arm degenerated into mutation-only through its
    own fallback while spending 26x the evaluations. Exactness is the wrong
    demand here: it is not needed for soundness, because the Lean kernel still
    decides acceptance, so the splice is free to be a heuristic and takes the
    library's closest vector instead.

    With `use_required=False` the required vector is replaced by a random target
    of the same shape. The first attempt at this control drew the decoy FROM THE
    LIBRARY, which made it matchable by construction (200 failures against
    23991) and so measured difficulty rather than correctness -- a control that
    was easier than the treatment for a reason unrelated to the hypothesis. The
    decoy is now drawn from fresh random rationals, so both arms face the same
    matching problem and only the target's correctness differs.
    """
    library = semantic_library(population, rng, points, counter)
    if not library:
        return tree, False
    addresses = all_addresses(tree)
    rng.shuffle(addresses)
    for address in addresses[:3]:
        if use_required:
            needed = required_values(tree, address, want, points, counter)
        else:
            needed = [
                Fraction(rng.randint(-20, 20), rng.randint(1, 9)) for _ in points
            ]
        best: tuple[Fraction, Node] | None = None
        for node, vector in library:
            distance = sum(
                abs(n - got) for n, got in zip(needed, vector) if n is not None
            )
            if best is None or distance < best[0]:
                best = (distance, node)
        if best is None:
            continue
        candidate = replace_at(tree, address, best[1])
        if candidate.size() <= max_size:
            return candidate, True
    return tree, False


def mutate(node: Node, rng: random.Random, max_size: int) -> Node:
    address = rng.choice(all_addresses(node))
    replacement = random_tree(rng, rng.randint(0, 2))
    candidate = replace_at(node, address, replacement)
    return candidate if candidate.size() <= max_size else node


def crossover(a: Node, b: Node, rng: random.Random, max_size: int) -> Node:
    address_a = rng.choice(all_addresses(a))
    address_b = rng.choice(all_addresses(b))
    candidate = replace_at(a, address_a, subtree_at(b, address_b))
    return candidate if candidate.size() <= max_size else a


ARMS: tuple[str, ...] = (
    "mutation_only", "crossover", "homologous_crossover", "anti_homologous_crossover",
    "contribution_preserving", "same_sites_unscaled",
    "semantic_backprop", "semantic_backprop_decoy",
)


def run_arm(
    seed: int,
    arm: str,
    budget: int,
    spec: Callable[[dict[str, Fraction]], Fraction],
    points: Sequence[dict[str, Fraction]],
    population_size: int = 40,
    max_size: int = 25,
) -> dict[str, object]:
    """One arm. Every arm draws its initial population from the SAME seeded
    stream, so a difference between arms cannot come from a luckier start.

    TWO COST METRICS ARE REPORTED, and that is deliberate. `evaluations` counts
    fitness evaluations, the budget the search is given. `tree_point_evaluations`
    counts EVERY evaluation of a tree at a point, including the probes the
    homologous arms spend finding a matching site. Comparing the arms on fitness
    evaluations alone would let a homology-seeking arm spend unbounded hidden
    compute and still look cheaper -- the incommensurable-comparison defect this
    programme keeps finding. An arm must win on both metrics for the win to be
    unqualified.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    rng = random.Random(seed)
    counter = [0]
    # The target's value at each sample point, which semantic backpropagation
    # needs and which the other arms reach only through the scalar fitness.
    want_vector = [spec(env) for env in points]
    population = [random_tree(rng, 3) for _ in range(population_size)]
    scored = []
    for ind in population:
        counter[0] += len(points)
        scored.append((fitness(ind, points, spec), ind))
    evaluations = len(scored)
    best = min(scored, key=lambda t: t[0])
    recombinations = 0
    homology_failures = 0
    while evaluations < budget:
        if best[0] == 0:
            break
        # Tournament of 3, the same selection pressure in every arm.
        def pick() -> Node:
            contenders = [scored[rng.randrange(len(scored))] for _ in range(3)]
            return min(contenders, key=lambda t: t[0])[1]

        parent = pick()
        if arm in ("semantic_backprop", "semantic_backprop_decoy") and rng.random() < 0.5:
            child, found = semantic_splice(
                parent, [ind for _, ind in scored], rng, max_size, want_vector, points,
                counter, use_required=(arm == "semantic_backprop"),
            )
            if found:
                recombinations += 1
            else:
                homology_failures += 1
                child = mutate(parent, rng, max_size)
        elif arm != "mutation_only" and rng.random() < 0.5:
            donor_parent = pick()
            if arm == "crossover":
                child = crossover(parent, donor_parent, rng, max_size)
                recombinations += 1
            elif arm in ("contribution_preserving", "same_sites_unscaled"):
                child, found = contribution_preserving_crossover(
                    parent, donor_parent, rng, max_size, points, counter,
                    rescale=(arm == "contribution_preserving"),
                )
                if found:
                    recombinations += 1
                else:
                    homology_failures += 1
                    child = mutate(parent, rng, max_size)
            else:
                child, found = homologous_crossover(
                    parent, donor_parent, rng, max_size, points, counter,
                    anti=(arm == "anti_homologous_crossover"),
                )
                if found:
                    recombinations += 1
                else:
                    # No admissible site: fall back to mutation and COUNT it, so
                    # an arm that quietly became mutation-only cannot be read as
                    # a success of recombination.
                    homology_failures += 1
                    child = mutate(parent, rng, max_size)
        else:
            child = mutate(parent, rng, max_size)
        counter[0] += len(points)
        score = fitness(child, points, spec)
        evaluations += 1
        worst_index = max(range(len(scored)), key=lambda i: scored[i][0])
        if score < scored[worst_index][0]:
            scored[worst_index] = (score, child)
        if score < best[0]:
            best = (score, child)
    return {
        "seed": seed,
        "arm": arm,
        "evaluations": evaluations,
        "tree_point_evaluations": counter[0],
        "recombinations": recombinations,
        "homology_failures": homology_failures,
        "solved": best[0] == 0,
        "best_fitness": str(best[0]),
        "solution_lean": render_lean(best[1]) if best[0] == 0 else None,
        "solution_size": best[1].size(),
    }


def verify_batch_in_lean(
    solutions: list[tuple[str, str]],
    target: Node,
    timeout_s: float = 1800.0,
) -> dict:
    """Gate the solutions through the real Lean kernel, in ONE invocation.

    THE SPEC IS THE RUNG'S OWN TARGET, not `ANSE.Verlet.qNext`. The calibration
    put the discriminating rung at a target other than the full Verlet step, and a
    candidate matching THAT target is not equal to `qNext` -- the gate would
    correctly reject every solution and the rejection would say nothing about the
    search. So the rung's target is rendered as a Lean definition and the
    obligation is equality with it.

    That the target rendering is shared with the fitness function is not a second
    source of truth: the target IS the specification. Fitness established
    agreement at twelve rational points, which is not equality; the kernel proves
    equality everywhere, by `ring`, with its axiom line checked. The division of
    labour is the point.

    Imported here rather than at module scope so the search can be run and
    inspected on a host without a Lean toolchain.
    """
    from anse.formal.lean_runner import LeanKernelVerifier

    verifier = LeanKernelVerifier(formal_dir=FORMAL)
    spec_term = render_lean(target)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        spec_file = tmp / "RungSpec.lean"
        spec_file.write_text(
            # `ring` lives in Mathlib.Tactic.Ring. Omitting this import made every
            # proof fail as an unknown tactic, so the gate rejected all eight
            # solutions as sorryAx -- correctly. A gate that refuses everything is
            # as uninformative as one that accepts everything, and this one was
            # right while the candidate generation was wrong.
            "import Mathlib.Tactic.Ring\n"
            "namespace RungSpec\n"
            f"def specQ (h w q p : Rat) : Rat := {spec_term}\n"
            "end RungSpec\n",
            encoding="utf-8",
        )
        batch = []
        for name, term in solutions:
            path = tmp / f"{name}.lean"
            path.write_text(
                "import Mathlib.Tactic.Ring\n"
                f"namespace {name}\n"
                f"def candQ (h w q p : Rat) : Rat := {term}\n"
                f"theorem {name}_m (h w q p : Rat) :"
                f" candQ h w q p = RungSpec.specQ h w q p := by\n"
                f"  unfold candQ RungSpec.specQ; ring\n"
                f"end {name}\n",
                encoding="utf-8",
            )
            batch.append((name, path, {
                f"{name}.{name}_m":
                    f"∀ h w q p : Rat, {name}.candQ h w q p = RungSpec.specQ h w q p"
            }))
        return verifier.verify_batch_against_spec(batch, spec_file, timeout_s=timeout_s)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=24)
    parser.add_argument("--budget", type=int, default=4000)
    parser.add_argument("--points", type=int, default=12)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skip-lean", action="store_true",
                        help="run the search only; report the gate as BLOCKED")
    parser.add_argument("--calibrate", action="store_true",
                        help="run the difficulty ladder and report pooled solve rates")
    parser.add_argument("--rung", type=str, default="L3_minus_wq",
                        help="which ladder rung to run the paired comparison on")
    args = parser.parse_args()

    point_rng = random.Random(20261024)
    points = sample_points(point_rng, args.points)

    if args.calibrate:
        # PRE-REGISTERED: pick the rung whose POOLED solve rate (both arms
        # together) is in [0.3, 0.7]. Not the rung where crossover looks best.
        BAND = (0.3, 0.7)
        ladder_rows: list[dict[str, object]] = []
        for name, node in target_ladder():
            def rung_spec(env: dict[str, Fraction], _n: Node = node) -> Fraction:
                return evaluate(_n, env)
            assert fitness(node, points, rung_spec) == 0, f"{name} unreachable"
            # Calibration uses only the two original arms, so the band is not
            # defined by the arm under test.
            runs = [
                run_arm(seed, arm, args.budget, rung_spec, points)
                for seed in range(args.seeds)
                for arm in ("mutation_only", "crossover")
            ]
            solved = sum(1 for r in runs if r["solved"])
            pooled = solved / len(runs)
            mut = sum(1 for r in runs if r["arm"] == "mutation_only" and r["solved"])
            xos = sum(1 for r in runs if r["arm"] == "crossover" and r["solved"])
            ladder_rows.append({
                "rung": name, "target_size": node.size(), "runs": len(runs),
                "solved": solved, "pooled_solve_rate": round(pooled, 3),
                "mutation_only_solved": mut, "crossover_solved": xos,
                "in_band": BAND[0] <= pooled <= BAND[1],
            })
            print(f"  {name:<20} size={node.size():>2}  pooled={pooled:.3f}  "
                  f"mut={mut:>2}/{args.seeds} xo={xos:>2}/{args.seeds}  "
                  f"{'IN BAND' if BAND[0] <= pooled <= BAND[1] else ''}")
        chosen = [r["rung"] for r in ladder_rows if r["in_band"]]
        report = {
            "what_this_is": "difficulty calibration for the recombination comparison",
            "why": (
                "The first attempt ran both arms at the full target and both solved 0 of 24, "
                "best fitness about 55.4 and nothing under 10. Two arms failing equally is a "
                "non-discriminating comparison and says nothing about recombination."
            ),
            "pre_registered_criterion": (
                "choose the rung whose POOLED solve rate over both arms lies in [0.3, 0.7]; "
                "pooled and fixed in advance so the apparatus is not selected to suit the answer"
            ),
            "band": list(BAND),
            "ladder": ladder_rows,
            "rungs_in_band": chosen,
            "parameters": {"seeds": args.seeds, "budget": args.budget,
                           "sample_points": args.points},
        }
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nrungs in band: {chosen or 'NONE -- no rung discriminates at this budget'}")
        print(f"wrote {args.out}")
        return 0

    rungs = dict(target_ladder())
    if args.rung not in rungs:
        raise SystemExit(f"unknown rung {args.rung!r}; have {sorted(rungs)}")
    target = rungs[args.rung]

    def spec(env: dict[str, Fraction]) -> Fraction:
        return evaluate(target, env)

    # POSITIVE CONTROL: the target must be reachable and score exactly zero.
    target_score = fitness(target, points, spec)
    assert target_score == 0, f"target does not score zero: {target_score}"

    # NEGATIVE CONTROL: a target requiring division by a variable is NOT in this
    # grammar, so no arm may solve it. If one does, fitness or the gate is wrong.
    def unreachable_spec(env: dict[str, Fraction]) -> Fraction:
        return env["q"] / (env["h"] + Fraction(97, 13)) + env["p"]

    negative_results = [
        run_arm(seed, arm, args.budget // 4, unreachable_spec, points)
        for seed in range(4) for arm in ARMS
    ]
    negative_solved = [r for r in negative_results if r["solved"]]

    arms: list[dict[str, object]] = []
    for seed in range(args.seeds):
        for arm in ARMS:
            arms.append(run_arm(seed, arm, args.budget, spec, points))

    def evals(arm_name: str, solved_only: bool, key: str = "evaluations") -> list[int]:
        return [
            int(r[key]) for r in arms
            if r["arm"] == arm_name and (r["solved"] or not solved_only)
        ]

    per_arm: dict[str, dict[str, object]] = {}
    for arm in ARMS:
        runs = [r for r in arms if r["arm"] == arm]
        solved_runs = [r for r in runs if r["solved"]]
        per_arm[arm] = {
            "runs": len(runs),
            "solved": len(solved_runs),
            "solve_rate": round(len(solved_runs) / len(runs), 4) if runs else None,
            "median_evaluations_when_solved": (
                statistics.median([int(r["evaluations"]) for r in solved_runs])
                if solved_runs else None),
            "median_tree_point_evaluations": (
                statistics.median([int(r["tree_point_evaluations"]) for r in runs])
                if runs else None),
            "total_recombinations": sum(int(r["recombinations"]) for r in runs),
            "homology_failures": sum(int(r["homology_failures"]) for r in runs),
        }

    mut_solved = [r for r in arms if r["arm"] == "mutation_only" and r["solved"]]
    xo_solved = [r for r in arms if r["arm"] == "crossover" and r["solved"]]

    # Paired comparison on seeds where BOTH arms solved: the only comparison that
    # is not confounded by one arm failing on hard seeds.
    paired: list[dict[str, object]] = []
    for seed in range(args.seeds):
        m = next((r for r in arms if r["seed"] == seed and r["arm"] == "mutation_only"), None)
        x = next((r for r in arms if r["seed"] == seed and r["arm"] == "crossover"), None)
        if m and x and m["solved"] and x["solved"]:
            paired.append({
                "seed": seed,
                "mutation_only": m["evaluations"],
                "crossover": x["evaluations"],
                "crossover_cheaper": int(x["evaluations"]) < int(m["evaluations"]),
            })

    wins = sum(1 for row in paired if row["crossover_cheaper"])
    median_ratio = (
        statistics.median(
            [int(r["crossover"]) / int(r["mutation_only"]) for r in paired]
        ) if paired else None
    )

    # Gate the distinct solutions found, in one Lean invocation.
    distinct: dict[str, str] = {}
    for r in arms:
        if r["solved"] and r["solution_lean"]:
            name = f"Sol{len(distinct)}"
            if r["solution_lean"] not in distinct.values():
                distinct[name] = str(r["solution_lean"])
    gate: dict[str, object]
    # A refusing gate must say WHICH clause binds; the first run reported only
    # `failed` and the diagnosis cost a separate investigation.
    if args.skip_lean or not distinct:
        gate = {"blocked": "BLOCKED: Lean gate not run" if args.skip_lean
                else "no solution to gate"}
    else:
        gate = verify_batch_in_lean(list(distinct.items())[:8], target)

    report = {
        "question": "Does recombination beat mutation when the gate is a Lean proof?",
        "why_now": (
            "A verified answer needs a formal gate, and the gate used to cost one Lean "
            "invocation per candidate. It now costs one per BATCH, because a compile reports a "
            "per-declaration verdict even when it exits nonzero, which brings a paired "
            "experiment inside a few minutes."
        ),
        "architecture": {
            "fitness": "exact rational agreement at sample points, in Python, zero Lean cost",
            "acceptance": "the Lean kernel, via verify_batch_against_spec",
            "why_separate": (
                "A wrong fitness misguides the search and wastes effort but can never cause a "
                "wrong acceptance, since nothing is accepted without a proof whose axioms line "
                "is free of sorryAx and of non-whitelisted axioms. Fitness guides, the kernel "
                "decides."
            ),
        },
        "controls": {
            "positive_target_reachable": True,
            "positive_target_fitness": str(target_score),
            "negative_target_unreachable_runs": len(negative_results),
            "negative_target_solved": len(negative_solved),
            "negative_control_passes": len(negative_solved) == 0,
            "pairing": "identical seeds and identical initial populations in both arms",
        },
        "parameters": {
            "rung": args.rung, "target_size": target.size(),
            "seeds": args.seeds, "budget": args.budget, "sample_points": args.points,
            "grammar": list(BINARY_OPS), "variables": list(VARIABLES),
            "constants": [str(c) for c in CONSTANTS],
        },
        "per_arm": per_arm,
        "prediction_registered_before_running": {
            "contribution_preserving": (
                "the successor recorded as untested after matching sign(B) failed. The donor is "
                "inserted scaled so its contribution to the output is EXACTLY what it was in its "
                "own parent, verified at 1614 of 1614 comparisons. If contribution transfer is "
                "what crossover lacks, this arm should beat random crossover's 29.0% and approach "
                "or exceed mutation-only's 47.0%"),
            "same_sites_unscaled": (
                "the control that separates the two things the operator does. Same constant-ratio "
                "sites, donor inserted UNSCALED. If it matches contribution_preserving then the "
                "scaling does nothing and only site selection matters; if both match plain "
                "crossover, neither does"),
            "the_falsifier_that_matters": (
                "if contribution_preserving does not significantly exceed random crossover, then "
                "exact contribution preservation is ALSO not the missing ingredient, and the "
                "contribution-transfer story for why crossover fails is refuted as an EXPLANATION "
                "rather than merely in its sign-matching operationalisation. That would leave the "
                "five refutations standing with no mechanism behind them"),
            "homologous_crossover": (
                "if homology is what crossover lacks, restricting recombination to sites whose "
                "context-coefficient sign pattern matches the donor's should raise the solve rate "
                "above random crossover's, and ideally to at least mutation-only's"),
            "anti_homologous_crossover": (
                "the negative control: restricting to INVERTED sign patterns should be no better "
                "than random crossover, and if the two homology arms behave alike then the "
                "signature carries nothing and the mechanism is not what was claimed"),
            "cost_caveat": (
                "the homology arms spend extra tree-point evaluations probing for a site, so a win "
                "on fitness evaluations alone is qualified; both metrics are reported"),
        },
        "results": {
            "mutation_only_solved": len(mut_solved),
            "crossover_solved": len(xo_solved),
            "mutation_only_median_evaluations": (
                statistics.median(evals("mutation_only", True)) if mut_solved else None),
            "crossover_median_evaluations": (
                statistics.median(evals("crossover", True)) if xo_solved else None),
            "paired_seeds_both_solved": len(paired),
            "crossover_cheaper_on": wins,
            "paired_median_ratio_crossover_over_mutation": median_ratio,
        },
        "lean_gate": gate,
        "arms": arms,
        "paired": paired,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")

    print(f"positive control  : target fitness {target_score} (reachable)")
    print(f"negative control  : {len(negative_solved)} of {len(negative_results)} "
          f"unreachable runs solved (must be 0)")
    print(f"mutation-only     : {len(mut_solved)}/{args.seeds} solved, "
          f"median {statistics.median(evals('mutation_only', True)) if mut_solved else '-'} evals")
    print(f"crossover         : {len(xo_solved)}/{args.seeds} solved, "
          f"median {statistics.median(evals('crossover', True)) if xo_solved else '-'} evals")
    print()
    for arm in ARMS:
        s = per_arm[arm]
        print(f"  {arm:<28} solved {s['solved']:>3}/{s['runs']:<3} "
              f"({(s['solve_rate'] or 0):.3f})  "
              f"med_evals={s['median_evaluations_when_solved'] or '-':<7} "
              f"tree_pt={s['median_tree_point_evaluations']:<8} "
              f"xovers={s['total_recombinations']:<6} "
              f"homology_fail={s['homology_failures']}")
    print()
    print(f"paired both-solved: {len(paired)} seeds, crossover cheaper on {wins}")
    if median_ratio is not None:
        print(f"paired median ratio (xo/mut): {median_ratio:.3f}  "
              f"(<0.90 would support recombination)")
    if isinstance(gate, dict) and "verdicts" in gate:
        print(f"Lean gate         : {gate.get('invocations')} invocation(s), "
              f"passed={gate.get('passed')}, failed={gate.get('failed')}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
