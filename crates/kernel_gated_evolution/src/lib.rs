//! Kernel-Gated Evolution (KGE).
//!
//! A biomimetic search over exact-rational expression genomes, built from the
//! three life-inspired mechanisms that measurement supported in this programme:
//!
//! * **Darwinian variation and selection.** Point/subtree mutation with
//!   tournament selection and steady-state replacement. This is the operator
//!   that solved targets in every comparison run so far.
//! * **Apoptotic checkpoints.** A one-sided exact screen: a candidate that
//!   disagrees with the specification at any sample point is refuted outright
//!   (no proof of a false identity exists), while agreement grants nothing. Like
//!   apoptosis, the checkpoint can only remove; it never confers survival.
//! * **Exact dosage analysis.** Every expression is affine in any one subtree's
//!   value, `out = A + B*v`. `B` is the locus's *dosage* -- exactly how much its
//!   value contributes to the phenotype -- and is computed for every locus in one
//!   forward and one backward pass. Loci with `B = 0` at every sample point are
//!   *inert*: they cannot affect the phenotype and are dead code.
//!
//! The final arbiter is not this crate. Survivors are rendered to Lean 4 and must
//! pass the kernel (`#print axioms` free of `sorryAx`), through the project's
//! `anse/formal/lean_runner.py`. Fitness guides; the kernel decides. A wrong
//! fitness can only waste search effort, never manufacture an acceptance.

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, Zero};
use rand::{RngExt, SeedableRng};
use rand_pcg::Pcg64;
use serde::Serialize;
use std::collections::HashMap;

/// Exact rational. Every quantity in the search is one of these.
pub type Rat = BigRational;

/// The genome's variables, in the order a Lean candidate binds them.
pub const VARIABLES: [&str; 4] = ["h", "w", "q", "p"];

/// An evaluation point: one value per variable.
pub type Env = [Rat; 4];

/// A locus: the path from the root, 0 = left child, 1 = right child.
pub type Address = Vec<u8>;

pub fn rat(n: i64, d: i64) -> Rat {
    Rat::new(BigInt::from(n), BigInt::from(d))
}

pub fn int(n: i64) -> Rat {
    Rat::from_integer(BigInt::from(n))
}

/// The constant terminals available to the genome.
pub fn constants() -> Vec<Rat> {
    vec![int(1), int(2), rat(1, 2)]
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
pub enum Opcode {
    Add,
    Sub,
    Mul,
}

impl Opcode {
    pub fn symbol(self) -> &'static str {
        match self {
            Opcode::Add => "+",
            Opcode::Sub => "-",
            Opcode::Mul => "*",
        }
    }
}

pub const OPCODES: [Opcode; 3] = [Opcode::Add, Opcode::Sub, Opcode::Mul];

/// An expression genome.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Node {
    Var(usize),
    Const(Rat),
    Op(Opcode, Box<Node>, Box<Node>),
}

impl Node {
    pub fn op(code: Opcode, left: Node, right: Node) -> Node {
        Node::Op(code, Box::new(left), Box::new(right))
    }

    pub fn size(&self) -> usize {
        match self {
            Node::Var(_) | Node::Const(_) => 1,
            Node::Op(_, l, r) => 1 + l.size() + r.size(),
        }
    }

    /// Exact evaluation.
    pub fn eval(&self, env: &Env) -> Rat {
        match self {
            Node::Var(i) => env[*i].clone(),
            Node::Const(c) => c.clone(),
            Node::Op(code, l, r) => {
                let a = l.eval(env);
                let b = r.eval(env);
                match code {
                    Opcode::Add => a + b,
                    Opcode::Sub => a - b,
                    Opcode::Mul => a * b,
                }
            }
        }
    }

    /// Every locus, root first.
    pub fn addresses(&self) -> Vec<Address> {
        let mut out = Vec::new();
        self.collect_addresses(Vec::new(), &mut out);
        out
    }

    fn collect_addresses(&self, prefix: Address, out: &mut Vec<Address>) {
        out.push(prefix.clone());
        if let Node::Op(_, l, r) = self {
            let mut lp = prefix.clone();
            lp.push(0);
            l.collect_addresses(lp, out);
            let mut rp = prefix;
            rp.push(1);
            r.collect_addresses(rp, out);
        }
    }

    pub fn at(&self, address: &[u8]) -> &Node {
        let mut node = self;
        for step in address {
            node = match node {
                Node::Op(_, l, r) => {
                    if *step == 0 {
                        l
                    } else {
                        r
                    }
                }
                _ => panic!("address descends through a leaf"),
            };
        }
        node
    }

    pub fn replace_at(&self, address: &[u8], replacement: Node) -> Node {
        if address.is_empty() {
            return replacement;
        }
        match self {
            Node::Op(code, l, r) => {
                if address[0] == 0 {
                    Node::op(*code, l.replace_at(&address[1..], replacement), (**r).clone())
                } else {
                    Node::op(*code, (**l).clone(), r.replace_at(&address[1..], replacement))
                }
            }
            _ => panic!("address descends through a leaf"),
        }
    }

    /// Render as a fully parenthesised Lean term over `Rat`, so operator
    /// precedence can never differ between what was evaluated and what is proved.
    pub fn render_lean(&self) -> String {
        match self {
            Node::Var(i) => VARIABLES[*i].to_string(),
            Node::Const(c) => {
                if c.denom().is_one() {
                    format!("({} : Rat)", c.numer())
                } else {
                    format!("(({} : Rat)/{})", c.numer(), c.denom())
                }
            }
            Node::Op(code, l, r) => {
                format!("({} {} {})", l.render_lean(), code.symbol(), r.render_lean())
            }
        }
    }
}

// --------------------------------------------------------------------------
// Targets and sample points
// --------------------------------------------------------------------------

/// Reachable targets of increasing size, used to calibrate difficulty. L6 is the
/// Verlet position update `q + h*p - (h^2 w^2 / 2) q`, written in this grammar.
pub fn target_ladder() -> Vec<(&'static str, Node)> {
    use Node::Var;
    let (h, w, q, p) = (Var(0), Var(1), Var(2), Var(3));
    let half = Node::Const(rat(1, 2));
    let base = Node::op(Opcode::Add, q.clone(), Node::op(Opcode::Mul, h.clone(), p.clone()));
    let hw = Node::op(Opcode::Mul, h.clone(), w.clone());
    let h2w2 = Node::op(
        Opcode::Mul,
        Node::op(Opcode::Mul, h.clone(), h.clone()),
        Node::op(Opcode::Mul, w.clone(), w.clone()),
    );
    vec![
        ("L1_base", base.clone()),
        ("L2_minus_q", Node::op(Opcode::Sub, base.clone(), q.clone())),
        (
            "L3_minus_wq",
            Node::op(Opcode::Sub, base.clone(), Node::op(Opcode::Mul, w.clone(), q.clone())),
        ),
        (
            "L4_minus_hwq",
            Node::op(Opcode::Sub, base.clone(), Node::op(Opcode::Mul, hw.clone(), q.clone())),
        ),
        (
            "L5_minus_half_hwq",
            Node::op(
                Opcode::Sub,
                base.clone(),
                Node::op(Opcode::Mul, Node::op(Opcode::Mul, hw, half.clone()), q.clone()),
            ),
        ),
        (
            "L6_full",
            Node::op(
                Opcode::Sub,
                base,
                Node::op(Opcode::Mul, Node::op(Opcode::Mul, h2w2, half), q),
            ),
        ),
    ]
}

/// Exact rational sample points with bounded denominators.
pub fn sample_points(rng: &mut Pcg64, count: usize) -> Vec<Env> {
    let mut points: Vec<Env> = Vec::new();
    while points.len() < count {
        let env: Env = [
            rat(rng.random_range(-9..=9), rng.random_range(1..=7)),
            rat(rng.random_range(-9..=9), rng.random_range(1..=7)),
            rat(rng.random_range(-9..=9), rng.random_range(1..=7)),
            rat(rng.random_range(-9..=9), rng.random_range(1..=7)),
        ];
        if !points.contains(&env) {
            points.push(env);
        }
    }
    points
}

/// Total absolute exact error against the target values. Zero is agreement at the
/// sample points -- not equality, which is the kernel's job -- but any nonzero
/// value is a witness of inequality and so a sound refutation.
pub fn fitness(node: &Node, points: &[Env], want: &[Rat]) -> Rat {
    let mut total = Rat::zero();
    for (env, w) in points.iter().zip(want) {
        total += (node.eval(env) - w).abs();
    }
    total
}

// --------------------------------------------------------------------------
// Variation
// --------------------------------------------------------------------------

pub fn random_tree(rng: &mut Pcg64, depth: u32) -> Node {
    if depth == 0 || rng.random::<f64>() < 0.3 {
        if rng.random::<f64>() < 0.7 {
            Node::Var(rng.random_range(0..VARIABLES.len()))
        } else {
            let cs = constants();
            Node::Const(cs[rng.random_range(0..cs.len())].clone())
        }
    } else {
        let code = OPCODES[rng.random_range(0..OPCODES.len())];
        Node::op(code, random_tree(rng, depth - 1), random_tree(rng, depth - 1))
    }
}

/// Replace a random locus with a fresh random subtree, respecting the size cap.
pub fn mutate(node: &Node, rng: &mut Pcg64, max_size: usize) -> Node {
    let addresses = node.addresses();
    let address = &addresses[rng.random_range(0..addresses.len())];
    let depth = rng.random_range(0..=2);
    let replacement = random_tree(rng, depth);
    let candidate = node.replace_at(address, replacement);
    if candidate.size() <= max_size {
        candidate
    } else {
        node.clone()
    }
}

// --------------------------------------------------------------------------
// Dosage analysis: exact context coefficients in one pass pair
// --------------------------------------------------------------------------

/// `B` for every locus: the coefficient in `out = A + B*v` for that locus's value
/// `v`, computed by one forward pass (values) and one backward pass seeded with
/// `B(root) = 1`, where `+` passes `B` to both children, `-` passes `B` left and
/// `-B` right, and `*` passes `B * value(sibling)` to each child. Exact, O(size).
pub fn context_coefficients(tree: &Node, env: &Env) -> HashMap<Address, Rat> {
    let mut values: HashMap<Address, Rat> = HashMap::new();
    forward(tree, Vec::new(), env, &mut values);
    let mut coefficients: HashMap<Address, Rat> = HashMap::new();
    backward(tree, Vec::new(), Rat::one(), &values, &mut coefficients);
    coefficients
}

fn forward(node: &Node, address: Address, env: &Env, values: &mut HashMap<Address, Rat>) -> Rat {
    let value = match node {
        Node::Var(i) => env[*i].clone(),
        Node::Const(c) => c.clone(),
        Node::Op(code, l, r) => {
            let mut la = address.clone();
            la.push(0);
            let mut ra = address.clone();
            ra.push(1);
            let a = forward(l, la, env, values);
            let b = forward(r, ra, env, values);
            match code {
                Opcode::Add => a + b,
                Opcode::Sub => a - b,
                Opcode::Mul => a * b,
            }
        }
    };
    values.insert(address, value.clone());
    value
}

fn backward(
    node: &Node,
    address: Address,
    upstream: Rat,
    values: &HashMap<Address, Rat>,
    coefficients: &mut HashMap<Address, Rat>,
) {
    coefficients.insert(address.clone(), upstream.clone());
    if let Node::Op(code, l, r) = node {
        let mut la = address.clone();
        la.push(0);
        let mut ra = address;
        ra.push(1);
        match code {
            Opcode::Add => {
                backward(l, la, upstream.clone(), values, coefficients);
                backward(r, ra, upstream, values, coefficients);
            }
            Opcode::Sub => {
                backward(l, la, upstream.clone(), values, coefficients);
                backward(r, ra, -upstream, values, coefficients);
            }
            Opcode::Mul => {
                let lv = values[&la].clone();
                let rv = values[&ra].clone();
                backward(l, la, &upstream * rv, values, coefficients);
                backward(r, ra, upstream * lv, values, coefficients);
            }
        }
    }
}

/// `B` by its definition, `f(v=1) - f(v=0)`: two whole-tree evaluations. Used to
/// verify the reverse-mode computation, never in the search.
pub fn context_coefficient_by_definition(tree: &Node, address: &[u8], env: &Env) -> Rat {
    let one = tree.replace_at(address, Node::Const(Rat::one()));
    let zero = tree.replace_at(address, Node::Const(Rat::zero()));
    one.eval(env) - zero.eval(env)
}

/// The value a locus MUST take for the tree to equal `want` at `env`, or `None`
/// when the locus is inert there (`B = 0`) and so imposes no requirement. Since
/// `out = A + B*v` and the forward pass yields `v` and `out`:
/// `v* = v + (want - out) / B`.
pub fn required_value(tree: &Node, address: &[u8], want: &Rat, env: &Env) -> Option<Rat> {
    let coefficients = context_coefficients(tree, env);
    let b = &coefficients[&address.to_vec()];
    if b.is_zero() {
        return None;
    }
    let v = tree.at(address).eval(env);
    let out = tree.eval(env);
    Some(v + (want - out) / b)
}

/// Fraction of loci that are inert at EVERY sample point: dead code whose value
/// cannot reach the phenotype.
pub fn inert_fraction(tree: &Node, points: &[Env]) -> f64 {
    let addresses = tree.addresses();
    let tables: Vec<HashMap<Address, Rat>> =
        points.iter().map(|env| context_coefficients(tree, env)).collect();
    let inert = addresses
        .iter()
        .filter(|a| tables.iter().all(|t| t[*a].is_zero()))
        .count();
    inert as f64 / addresses.len() as f64
}

// --------------------------------------------------------------------------
// Lifetime learning of constants: the Baldwin effect, exactly
// --------------------------------------------------------------------------

/// Whether, and how, an individual adapts its constant loci during its lifetime.
///
/// * `None` -- the plain population: constants are searched like everything else.
/// * `Baldwin` -- constants are solved exactly against the specification before
///   fitness is measured, but the GENOME is left unchanged; selection acts on the
///   adapted phenotype, and the adaptation is not inherited. This is the Baldwin
///   effect: learning smooths the landscape evolution climbs.
/// * `Lamarck` -- the solved constants are written back into the genome, so the
///   adaptation IS inherited. Biologically false for genes, routinely effective
///   in program search, and here an explicit arm rather than a hidden default.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
pub enum Tuning {
    None,
    Baldwin,
    Lamarck,
}

/// Solve constant loci exactly where the specification determines them.
///
/// For a constant leaf with value `v`, the required value at a sample point is
/// `v* = v + (want - out) / B` (proved: `ANSE.Alix.xav_required_value`). One leaf
/// holds one value, so it can only be set when the required value is the SAME
/// rational at every point where the leaf is not inert (`B != 0`); a leaf whose
/// required values disagree is left alone, since no constant satisfies them. One
/// change invalidates the other loci's `out` and `B`, so after each change the
/// pass restarts, up to `max_rounds`. Every evaluation is charged to `counter`.
///
/// This is exact repair of what the structure already gets right: a tree with
/// the right shape and a wrong coefficient becomes a solution in one round.
/// A tree with the wrong shape is unchanged by it.
pub fn tune_constants(
    tree: &Node,
    want: &[Rat],
    points: &[Env],
    counter: &mut usize,
    max_rounds: usize,
) -> (Node, usize) {
    let mut current = tree.clone();
    let mut changed_total = 0usize;
    for _ in 0..max_rounds {
        let const_addrs: Vec<Address> = current
            .addresses()
            .into_iter()
            .filter(|a| matches!(current.at(a), Node::Const(_)))
            .collect();
        if const_addrs.is_empty() {
            break;
        }
        let tables: Vec<HashMap<Address, Rat>> =
            points.iter().map(|env| context_coefficients(&current, env)).collect();
        let outs: Vec<Rat> = points.iter().map(|env| current.eval(env)).collect();
        *counter += 2 * points.len();
        let mut changed = false;
        for address in &const_addrs {
            let v = match current.at(address) {
                Node::Const(c) => c.clone(),
                _ => unreachable!("filtered to constants"),
            };
            let mut required: Option<Rat> = None;
            let mut consistent = true;
            for (i, _) in points.iter().enumerate() {
                let b = &tables[i][address];
                if b.is_zero() {
                    continue;
                }
                let r = &v + (&want[i] - &outs[i]) / b;
                match &required {
                    None => required = Some(r),
                    Some(q) => {
                        if *q != r {
                            consistent = false;
                            break;
                        }
                    }
                }
            }
            if consistent {
                if let Some(r) = required {
                    if r != v {
                        current = current.replace_at(address, Node::Const(r));
                        changed = true;
                        changed_total += 1;
                        break;
                    }
                }
            }
        }
        if !changed {
            break;
        }
    }
    (current, changed_total)
}

// --------------------------------------------------------------------------
// Apoptotic checkpoint: a one-sided exact screen
// --------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub enum Checkpoint {
    /// Disagreement at this sample point index: a witness that no proof exists.
    Refuted { point: usize },
    /// Agreed at every sample point. This is NOT acceptance; the kernel decides.
    Survives,
}

/// Compare a candidate against the specification at the sample points. A single
/// disagreement refutes it outright; agreement everywhere merely lets it proceed
/// to the kernel. The checkpoint can remove, never confer survival.
pub fn checkpoint(candidate: &Node, spec: &Node, points: &[Env]) -> Checkpoint {
    for (index, env) in points.iter().enumerate() {
        if candidate.eval(env) != spec.eval(env) {
            return Checkpoint::Refuted { point: index };
        }
    }
    Checkpoint::Survives
}

// --------------------------------------------------------------------------
// Search
// --------------------------------------------------------------------------

#[derive(Clone, Debug, Serialize)]
pub struct ArmResult {
    pub seed: u64,
    pub solved: bool,
    /// Fitness evaluations: the budgeted currency.
    pub evaluations: usize,
    /// EVERY evaluation of a tree at a point, including the dosage passes spent
    /// on lifetime learning. An arm must not win in one currency by hiding its
    /// cost in the other.
    pub tree_point_evaluations: usize,
    /// Constant loci set by lifetime learning across the run (0 for `Tuning::None`).
    pub constants_tuned: usize,
    pub best_fitness: String,
    pub best_size: usize,
    pub inert_fraction_of_best: f64,
    pub solution_lean: Option<String>,
}

pub struct SearchConfig {
    pub budget: usize,
    pub population_size: usize,
    pub max_size: usize,
    pub tournament: usize,
    pub tuning: Tuning,
    pub tuning_rounds: usize,
}

impl Default for SearchConfig {
    fn default() -> Self {
        SearchConfig {
            budget: 4000,
            population_size: 40,
            max_size: 25,
            tournament: 3,
            tuning: Tuning::None,
            tuning_rounds: 4,
        }
    }
}

/// Darwinian mutation-selection, steady state. Fitness is exact; `want` is the
/// target's value at each sample point. Stops at the first exact agreement, which
/// is then a kernel candidate rather than an accepted solution.
///
/// With lifetime learning, an individual's constants are solved against the
/// specification before its fitness is measured. Under `Baldwin` the genome kept
/// in the population is the UNADAPTED one and only the phenotype's fitness
/// counts; under `Lamarck` the adapted tree replaces it. In both cases the
/// candidate handed to the kernel is the adapted phenotype, which is what was
/// measured to agree.
pub fn evolve(seed: u64, target: &Node, points: &[Env], config: &SearchConfig) -> ArmResult {
    let mut rng = Pcg64::seed_from_u64(seed);
    let want: Vec<Rat> = points.iter().map(|env| target.eval(env)).collect();
    let mut tree_points = 0usize;
    let mut constants_tuned = 0usize;

    // Returns (fitness, genome to keep, phenotype that was measured).
    let assess = |ind: Node, tree_points: &mut usize, tuned_count: &mut usize| -> (Rat, Node, Node) {
        let phenotype = match config.tuning {
            Tuning::None => ind.clone(),
            Tuning::Baldwin | Tuning::Lamarck => {
                let (t, n) = tune_constants(&ind, &want, points, tree_points, config.tuning_rounds);
                *tuned_count += n;
                t
            }
        };
        *tree_points += points.len();
        let score = fitness(&phenotype, points, &want);
        let genome = if config.tuning == Tuning::Lamarck { phenotype.clone() } else { ind };
        (score, genome, phenotype)
    };

    let mut scored: Vec<(Rat, Node)> = Vec::with_capacity(config.population_size);
    let mut best: Option<(Rat, Node)> = None;
    for _ in 0..config.population_size {
        let ind = random_tree(&mut rng, 3);
        let (score, genome, phenotype) = assess(ind, &mut tree_points, &mut constants_tuned);
        if best.as_ref().map_or(true, |(s, _)| score < *s) {
            best = Some((score.clone(), phenotype));
        }
        scored.push((score, genome));
    }
    let mut evaluations = scored.len();

    while evaluations < config.budget && !best.as_ref().unwrap().0.is_zero() {
        let parent = {
            let mut winner: Option<&(Rat, Node)> = None;
            for _ in 0..config.tournament {
                let c = &scored[rng.random_range(0..scored.len())];
                if winner.map_or(true, |w| c.0 < w.0) {
                    winner = Some(c);
                }
            }
            winner.unwrap().1.clone()
        };
        let child = mutate(&parent, &mut rng, config.max_size);
        let (score, genome, phenotype) = assess(child, &mut tree_points, &mut constants_tuned);
        evaluations += 1;
        let worst = (0..scored.len()).max_by(|&i, &j| scored[i].0.cmp(&scored[j].0)).unwrap();
        if score < scored[worst].0 {
            scored[worst] = (score.clone(), genome);
        }
        if score < best.as_ref().unwrap().0 {
            best = Some((score, phenotype));
        }
    }

    let (best_score, best_tree) = best.unwrap();
    let solved = best_score.is_zero();
    ArmResult {
        seed,
        solved,
        evaluations,
        tree_point_evaluations: tree_points,
        constants_tuned,
        best_fitness: best_score.to_string(),
        best_size: best_tree.size(),
        inert_fraction_of_best: inert_fraction(&best_tree, points),
        solution_lean: if solved { Some(best_tree.render_lean()) } else { None },
    }
}

// --------------------------------------------------------------------------
// Targets from outside the ladder: a prefix-notation parser
// --------------------------------------------------------------------------

/// Parse a target written in prefix notation over the genome's grammar, e.g.
/// `(- (+ q (* h p)) (* w q))`. Leaves are the variable names `h w q p`, or
/// rationals written `n` or `n/d`. Only `+ - *` are accepted: a target outside
/// the grammar cannot be a solution and is refused rather than approximated.
pub fn parse_prefix(text: &str) -> Result<Node, String> {
    let tokens: Vec<String> = text
        .replace('(', " ( ")
        .replace(')', " ) ")
        .split_whitespace()
        .map(|s| s.to_string())
        .collect();
    let mut index = 0usize;
    let node = parse_tokens(&tokens, &mut index)?;
    if index != tokens.len() {
        return Err(format!("trailing tokens after position {index}"));
    }
    Ok(node)
}

fn parse_tokens(tokens: &[String], index: &mut usize) -> Result<Node, String> {
    let token = tokens.get(*index).ok_or("unexpected end of input")?.clone();
    *index += 1;
    if token == "(" {
        let op = tokens.get(*index).ok_or("operator expected")?.clone();
        *index += 1;
        let code = match op.as_str() {
            "+" => Opcode::Add,
            "-" => Opcode::Sub,
            "*" => Opcode::Mul,
            other => return Err(format!("operator {other:?} is outside the grammar {{+,-,*}}")),
        };
        let left = parse_tokens(tokens, index)?;
        let right = parse_tokens(tokens, index)?;
        match tokens.get(*index).map(String::as_str) {
            Some(")") => {
                *index += 1;
                Ok(Node::op(code, left, right))
            }
            _ => Err("')' expected".to_string()),
        }
    } else if let Some(i) = VARIABLES.iter().position(|v| *v == token) {
        Ok(Node::Var(i))
    } else {
        let mut parts = token.split('/');
        let n: i64 = parts.next().unwrap().parse().map_err(|_| format!("bad leaf {token:?}"))?;
        let d: i64 = match parts.next() {
            Some(d) => d.parse().map_err(|_| format!("bad denominator in {token:?}"))?,
            None => 1,
        };
        if d == 0 {
            return Err("zero denominator".to_string());
        }
        Ok(Node::Const(rat(n, d)))
    }
}

// --------------------------------------------------------------------------
// The naive baseline: random search at the same budget
// --------------------------------------------------------------------------

/// Draw `budget` random trees and keep the best. No selection, no inheritance:
/// the floor any search must clear to claim it searched at all.
pub fn random_search(seed: u64, target: &Node, points: &[Env], budget: usize) -> ArmResult {
    let mut rng = Pcg64::seed_from_u64(seed);
    let want: Vec<Rat> = points.iter().map(|env| target.eval(env)).collect();
    let mut best: Option<(Rat, Node)> = None;
    let mut evaluations = 0usize;
    while evaluations < budget {
        let depth = rng.random_range(2..=4);
        let candidate = random_tree(&mut rng, depth);
        let score = fitness(&candidate, points, &want);
        evaluations += 1;
        if best.as_ref().map_or(true, |(s, _)| score < *s) {
            let done = score.is_zero();
            best = Some((score, candidate));
            if done {
                break;
            }
        }
    }
    let (score, node) = best.unwrap();
    let solved = score.is_zero();
    ArmResult {
        seed,
        solved,
        evaluations,
        tree_point_evaluations: evaluations * points.len(),
        constants_tuned: 0,
        best_fitness: score.to_string(),
        best_size: node.size(),
        inert_fraction_of_best: inert_fraction(&node, points),
        solution_lean: if solved { Some(node.render_lean()) } else { None },
    }
}

// --------------------------------------------------------------------------
// The control that the population must beat: a plain hill-climber
// --------------------------------------------------------------------------

#[derive(Clone, Debug, Serialize)]
pub struct ClimbResult {
    pub seed: u64,
    pub solved: bool,
    pub evaluations: usize,
    pub restarts: usize,
    pub best_fitness: String,
}

/// Greedy descent with optional restarts, charged the SAME fitness-evaluation
/// budget as `evolve`. One individual, no population, no selection, no crossover:
/// the simplest thing that could possibly work. If it matches the genetic
/// algorithm, the population machinery is decoration for this problem.
///
/// A step samples `neighbours` mutations and moves to the best strictly
/// improving one. At a local optimum it either stops (`allow_restarts` false) or
/// restarts from a fresh random tree, paying for the restart out of the same
/// budget -- an unlimited restart budget would turn this into random search with
/// extra steps.
pub fn hill_climb(
    seed: u64,
    target: &Node,
    points: &[Env],
    budget: usize,
    max_size: usize,
    neighbours: usize,
    allow_restarts: bool,
) -> ClimbResult {
    let mut rng = Pcg64::seed_from_u64(seed);
    let want: Vec<Rat> = points.iter().map(|env| target.eval(env)).collect();
    let mut current = random_tree(&mut rng, 3);
    let mut score = fitness(&current, points, &want);
    let mut evaluations = 1usize;
    let mut restarts = 0usize;
    let mut best = score.clone();
    while evaluations < budget && !best.is_zero() {
        let mut candidates: Vec<(Rat, Node)> = Vec::new();
        for _ in 0..neighbours {
            if evaluations >= budget {
                break;
            }
            let child = mutate(&current, &mut rng, max_size);
            candidates.push((fitness(&child, points, &want), child));
            evaluations += 1;
        }
        if candidates.is_empty() {
            break;
        }
        let (local_score, local_node) =
            candidates.into_iter().min_by(|a, b| a.0.cmp(&b.0)).unwrap();
        if local_score < score {
            current = local_node;
            score = local_score;
            if score < best {
                best = score.clone();
            }
        } else if allow_restarts {
            restarts += 1;
            current = random_tree(&mut rng, 3);
            score = fitness(&current, points, &want);
            evaluations += 1;
            if score < best {
                best = score.clone();
            }
        } else {
            break;
        }
    }
    ClimbResult {
        seed,
        solved: best.is_zero(),
        evaluations,
        restarts,
        best_fitness: best.to_string(),
    }
}
