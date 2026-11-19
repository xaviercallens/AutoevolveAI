//! The invariants KGE rests on, asserted in exact arithmetic on random genomes.
//! An optimisation or an identity that is not tested is an assertion; these
//! make them measurements.

use kernel_gated_evolution::*;
use num_traits::Zero;
use rand::SeedableRng;
use rand_pcg::Pcg64;

#[test]
fn reverse_mode_dosage_equals_the_definition() {
    let mut rng = Pcg64::seed_from_u64(7);
    let points = sample_points(&mut Pcg64::seed_from_u64(11), 4);
    let mut checked = 0;
    for _ in 0..60 {
        let tree = random_tree(&mut rng, 4);
        for env in &points {
            let table = context_coefficients(&tree, env);
            for address in tree.addresses() {
                let direct = context_coefficient_by_definition(&tree, &address, env);
                assert_eq!(table[&address], direct, "reverse mode disagrees at {address:?}");
                checked += 1;
            }
        }
    }
    assert!(checked > 500, "only {checked} comparisons");
}

#[test]
fn minus_negates_right_and_times_scales_by_sibling() {
    let (h, w, q) = (Node::Var(0), Node::Var(1), Node::Var(2));
    let tree = Node::op(Opcode::Sub, q, Node::op(Opcode::Mul, h, w)); // q - h*w
    let env: Env = [int(2), int(5), int(1), int(0)];
    let table = context_coefficients(&tree, &env);
    assert_eq!(table[&vec![0u8]], int(1));
    assert_eq!(table[&vec![1u8]], int(-1), "right of a minus is inverted");
    assert_eq!(table[&vec![1u8, 0]], int(-5), "h: -1 * value(w)");
    assert_eq!(table[&vec![1u8, 1]], int(-2), "w: -1 * value(h)");
}

#[test]
fn required_value_makes_the_tree_exact_at_that_point() {
    let mut rng = Pcg64::seed_from_u64(21);
    let points = sample_points(&mut Pcg64::seed_from_u64(23), 6);
    let target = target_ladder().into_iter().find(|(n, _)| *n == "L6_full").unwrap().1;
    let (mut checked, mut inert) = (0, 0);
    for _ in 0..150 {
        let tree = random_tree(&mut rng, 4);
        for env in &points {
            let want = target.eval(env);
            for address in tree.addresses() {
                match required_value(&tree, &address, &want, env) {
                    None => inert += 1,
                    Some(v_star) => {
                        let spliced = tree.replace_at(&address, Node::Const(v_star));
                        assert_eq!(spliced.eval(env), want, "v* did not hit the target");
                        checked += 1;
                    }
                }
            }
        }
    }
    assert!(checked > 2000, "only {checked} checks");
    assert!(inert > 0, "no inert loci found; the None branch is untested");
}

#[test]
fn checkpoint_refutes_wrong_keeps_right_and_cannot_accept() {
    let points = sample_points(&mut Pcg64::seed_from_u64(5), 5);
    let target = target_ladder().into_iter().find(|(n, _)| *n == "L3_minus_wq").unwrap().1;
    // Right: identical tree survives.
    assert_eq!(checkpoint(&target.clone(), &target, &points), Checkpoint::Survives);
    // Wrong: every other rung is refuted.
    for (name, other) in target_ladder() {
        if name != "L3_minus_wq" {
            assert!(matches!(checkpoint(&other, &target, &points), Checkpoint::Refuted { .. }), "{name}");
        }
    }
    // One-sided: a candidate equal to the target at every sample point but not
    // equal as a function SURVIVES the checkpoint. The product over (h - h_i)
    // vanishes at every point's h and nowhere else.
    let h = Node::Var(0);
    let mut vanishing = Node::Const(int(1));
    for env in &points {
        vanishing = Node::op(Opcode::Mul, vanishing, Node::op(Opcode::Sub, h.clone(), Node::Const(env[0].clone())));
    }
    let evader = Node::op(Opcode::Add, target.clone(), vanishing);
    assert_eq!(checkpoint(&evader, &target, &points), Checkpoint::Survives);
    // ...and it is genuinely a different function.
    let probe: Env = [int(100), int(1), int(1), int(1)];
    assert_ne!(evader.eval(&probe), target.eval(&probe), "the evader must differ somewhere");
}

#[test]
fn targets_are_reachable_and_the_search_solves_the_easy_rung() {
    let mut rng = Pcg64::seed_from_u64(20261024);
    let points = sample_points(&mut rng, 12);
    for (name, target) in target_ladder() {
        let want: Vec<Rat> = points.iter().map(|e| target.eval(e)).collect();
        assert!(fitness(&target, &points, &want).is_zero(), "{name} not reachable");
    }
    // L2 is the rung measured easiest (pooled 0.969 in the Python calibration,
    // 8/8 in the Rust smoke run): `q + h*p - q` reduces to `h*p`, so many trees
    // realise it. A stochastic bound belongs on the rung least likely to make
    // this test flaky, not on the one that happened to be listed first.
    let l2 = target_ladder().into_iter().find(|(n, _)| *n == "L2_minus_q").unwrap().1;
    let config = SearchConfig { budget: 4000, ..SearchConfig::default() };
    let solved = (0..8u64).filter(|&s| evolve(s, &l2, &points, &config).solved).count();
    assert!(solved >= 5, "L2 should be solvable most of the time; got {solved}/8");
}

#[test]
fn prefix_parser_rebuilds_the_ladder_and_refuses_the_outside() {
    // Every ladder target, written in prefix notation, must parse to exactly
    // the tree the ladder constructs -- structural equality, not just equal
    // values -- so a target given on the command line is the target searched.
    let written = [
        ("L1_base", "(+ q (* h p))"),
        ("L2_minus_q", "(- (+ q (* h p)) q)"),
        ("L3_minus_wq", "(- (+ q (* h p)) (* w q))"),
        ("L4_minus_hwq", "(- (+ q (* h p)) (* (* h w) q))"),
        ("L5_minus_half_hwq", "(- (+ q (* h p)) (* (* (* h w) 1/2) q))"),
        ("L6_full", "(- (+ q (* h p)) (* (* (* (* h h) (* w w)) 1/2) q))"),
    ];
    let ladder = target_ladder();
    for (name, text) in written {
        let built = &ladder.iter().find(|(n, _)| *n == name).unwrap().1;
        let parsed = parse_prefix(text).expect(name);
        assert_eq!(&parsed, built, "{name} parsed differently from the ladder's construction");
    }
    // Outside the grammar is refused, not approximated.
    assert!(parse_prefix("(/ q h)").is_err(), "division is outside {{+,-,*}}");
    assert!(parse_prefix("(+ q)").is_err(), "arity");
    assert!(parse_prefix("(+ q x)").is_err(), "unknown variable");
    assert!(parse_prefix("(+ q 1/0)").is_err(), "zero denominator");
}

#[test]
fn random_search_is_a_real_floor_and_reports_its_cost() {
    let mut rng = Pcg64::seed_from_u64(20261024);
    let points = sample_points(&mut rng, 12);
    let l1 = target_ladder().into_iter().find(|(n, _)| *n == "L1_base").unwrap().1;
    let r = random_search(3, &l1, &points, 500);
    assert!(r.evaluations <= 500, "must respect the budget");
    assert!(r.best_size >= 1);
    // Either it solved (and stopped early, reporting fewer evaluations) or it
    // spent the whole budget; a run that claims a solution with nonzero fitness
    // would be a bug.
    if r.solved {
        assert_eq!(r.best_fitness, "0");
        assert!(r.solution_lean.is_some());
    } else {
        assert_eq!(r.evaluations, 500);
        assert!(r.solution_lean.is_none());
    }
}

#[test]
fn lifetime_learning_repairs_a_wrong_constant_exactly_and_leaves_shape_errors_alone() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let l5 = target_ladder().into_iter().find(|(n, _)| *n == "L5_minus_half_hwq").unwrap().1;
    let want: Vec<Rat> = points.iter().map(|e| l5.eval(e)).collect();
    // L5 with its 1/2 replaced by 3: right shape, wrong coefficient.
    let wrong = parse_prefix("(- (+ q (* h p)) (* (* (* h w) 3) q))").unwrap();
    assert!(!fitness(&wrong, &points, &want).is_zero());
    let mut cost = 0usize;
    let (fixed, changed) = tune_constants(&wrong, &want, &points, &mut cost, 4);
    assert_eq!(changed, 1, "exactly one locus should be set");
    assert!(fitness(&fixed, &points, &want).is_zero(), "the repaired tree must agree everywhere");
    assert_eq!(fixed, l5, "and it must be L5 itself, not merely an agreeing tree");
    assert!(cost > 0, "the dosage passes must be charged");
    // A correct tree is left alone.
    let (same, n) = tune_constants(&l5, &want, &points, &mut cost, 4);
    assert_eq!(n, 0);
    assert_eq!(same, l5);
    // A wrong SHAPE cannot be repaired by any constant: L4's shape against L6's values.
    let l6 = target_ladder().into_iter().find(|(n, _)| *n == "L6_full").unwrap().1;
    let want6: Vec<Rat> = points.iter().map(|e| l6.eval(e)).collect();
    let l4 = parse_prefix("(- (+ q (* h p)) (* (* (* h w) 1) q))").unwrap();
    let (still, m) = tune_constants(&l4, &want6, &points, &mut cost, 4);
    assert_eq!(m, 0, "no single constant makes L4's shape equal L6");
    assert_eq!(still, l4);
}

#[test]
fn baldwin_keeps_the_genome_and_lamarck_writes_it_back() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let l2 = target_ladder().into_iter().find(|(n, _)| *n == "L2_minus_q").unwrap().1;
    for tuning in [Tuning::None, Tuning::Baldwin, Tuning::Lamarck] {
        let config = SearchConfig { budget: 1500, tuning, ..SearchConfig::default() };
        let r = evolve(5, &l2, &points, &config);
        assert!(r.tree_point_evaluations >= r.evaluations * points.len(),
                "tree-point cost must at least cover the fitness evaluations");
        if tuning == Tuning::None {
            assert_eq!(r.constants_tuned, 0);
            assert_eq!(r.tree_point_evaluations, r.evaluations * points.len());
        }
        if r.solved {
            assert_eq!(r.best_fitness, "0");
            assert!(r.solution_lean.is_some());
        }
    }
}

#[test]
fn inert_fraction_is_zero_for_a_minimal_target_and_positive_with_dead_code() {
    let points = sample_points(&mut Pcg64::seed_from_u64(9), 6);
    let l1 = target_ladder().into_iter().find(|(n, _)| *n == "L1_base").unwrap().1;
    assert_eq!(inert_fraction(&l1, &points), 0.0);
    // q + h*p + 0*(w*w): the w*w subtree is inert everywhere.
    let dead = Node::op(
        Opcode::Add,
        l1,
        Node::op(Opcode::Mul, Node::Const(Rat::zero()), Node::op(Opcode::Mul, Node::Var(1), Node::Var(1))),
    );
    assert!(inert_fraction(&dead, &points) > 0.0);
}

#[test]
fn diversity_is_measured_and_immigration_is_paid_from_the_budget() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let l5 = target_ladder().into_iter().find(|(n, _)| *n == "L5_minus_half_hwq").unwrap().1;
    let mut saw_collapse = false;
    let mut saw_immigration = false;
    for seed in 0..12u64 {
        let plain = evolve(seed, &l5, &points, &SearchConfig { budget: 3000, ..SearchConfig::default() });
        let imm = evolve(seed, &l5, &points,
                         &SearchConfig { budget: 3000, immigration: true, ..SearchConfig::default() });
        // The budget binds both arms: immigrants are not free.
        assert!(plain.evaluations <= 3000 && imm.evaluations <= 3000);
        assert!(plain.collapsed_generations <= plain.generations_observed);
        assert_eq!(plain.immigration_events, 0, "no immigration unless asked");
        assert!(imm.immigration_events <= imm.collapsed_generations);
        assert!(plain.final_distinct_fitness >= 1);
        saw_collapse |= plain.collapsed_generations > 0;
        saw_immigration |= imm.immigration_events > 0;
    }
    assert!(saw_collapse, "collapse never observed on L5; the diagnostic is untested");
    assert!(saw_immigration, "immigration never triggered; the intervention is untested");
}

// ---------------------------------------------------------------------------
// Perturb-the-best at collapse: invariants the experiment's analysis relies on.
// ---------------------------------------------------------------------------

fn rung(name: &str) -> Node {
    target_ladder().into_iter().find(|(n, _)| n.starts_with(name)).map(|(_, t)| t).unwrap()
}

fn pb_configs() -> Vec<(&'static str, SearchConfig)> {
    let base = SearchConfig { budget: 1200, tuning: Tuning::Baldwin, ..SearchConfig::default() };
    let mk = |m: ImmigrationMode| SearchConfig { immigration_mode: m, ..SearchConfig { budget: base.budget, tuning: Tuning::Baldwin, ..SearchConfig::default() } };
    vec![
        ("pb13-forced", mk(ImmigrationMode::PerturbBest { kmin: 1, kmax: 3, admit: Admit::Forced })),
        ("pb13-matched", mk(ImmigrationMode::PerturbBest { kmin: 1, kmax: 3, admit: Admit::Normal })),
        ("clone", mk(ImmigrationMode::CloneBest)),
    ]
}

/// The pairing guarantee that makes the McNemar analysis a PAIRED test: a seed whose population never
/// collapses must be bit-identical to the baseline under every new mode, because the intervention draws
/// only from its own stream and the generation clock counts main-loop children.
#[test]
fn new_modes_equal_the_baseline_on_every_seed_that_never_collapses() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let target = rung("L3");
    let base_cfg = SearchConfig { budget: 1200, tuning: Tuning::Baldwin, ..SearchConfig::default() };
    let (mut compared, mut collapsed_seen) = (0usize, 0usize);
    for seed in 0..30u64 {
        let base = evolve(seed, &target, &points, &base_cfg);
        for (name, cfg) in pb_configs() {
            let r = evolve(seed, &target, &points, &cfg);
            if base.first_collapse_generation.is_none() {
                assert_eq!((r.solved, r.evaluations, r.tree_point_evaluations), (base.solved, base.evaluations, base.tree_point_evaluations),
                    "{name} diverged from baseline on seed {seed} with no collapse");
                assert_eq!(r.inserted_total, 0, "{name} inserted without a collapse");
                compared += 1;
            } else {
                collapsed_seen += 1;
            }
        }
    }
    assert!(compared >= 30, "only {compared} no-collapse comparisons; the test would be vacuous");
    assert!(collapsed_seen > 0, "no seed collapsed, so the intervention path was never exercised");
}

/// Bookkeeping that the analysis reads: every insertion is eventually accounted for, the budget is a
/// hard ceiling, an intervention is charged, and the legacy modes still use the legacy clock.
#[test]
fn interventions_are_charged_and_accounted() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let target = rung("L4");
    let mut exercised = 0usize;
    for seed in 0..20u64 {
        for (name, cfg) in pb_configs() {
            let r = evolve(seed, &target, &points, &cfg);
            assert!(r.evaluations <= cfg.budget, "{name} exceeded the budget: {}", r.evaluations);
            assert!(r.admitted_total <= r.inserted_total, "{name}: admitted more than were charged");
            assert_eq!(r.survival_gens.len(), r.admitted_total, "{name}: admissions and survival records disagree on seed {seed}");
            assert!(r.inserted_equal_to_best_fitness <= r.inserted_total);
            if name != "pb13-matched" {
                assert_eq!(r.admitted_total, r.inserted_total, "{name}: forced admission must admit every charged candidate");
            }
            if r.immigration_events > 0 {
                exercised += 1;
                assert!(r.inserted_total + r.dedup_fail >= 1, "{name}: an event inserted nothing and failed nothing");
                assert!(r.inserted_total <= r.immigration_events * (SearchConfig::default().population_size / 2));
            }
        }
    }
    assert!(exercised > 0, "no run reached the intervention; the test would be vacuous");
}

/// The clone control adds no genotype: every clone has exactly the best's fitness, so it can only change
/// selection pressure and evaluation count, never variance.
#[test]
fn clone_control_inserts_only_best_fitness_copies() {
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let target = rung("L4");
    let cfg = SearchConfig { budget: 1200, tuning: Tuning::Baldwin, immigration_mode: ImmigrationMode::CloneBest, ..SearchConfig::default() };
    let mut total = 0usize;
    for seed in 0..20u64 {
        let r = evolve(seed, &target, &points, &cfg);
        assert_eq!(r.inserted_equal_to_best_fitness, r.inserted_total, "a clone had a different fitness on seed {seed}");
        total += r.inserted_total;
    }
    assert!(total > 0, "the clone control never fired");
}

#[test]
fn perturb_best_stays_within_the_size_cap_and_actually_changes_the_genome() {
    let mut rng = Pcg64::seed_from_u64(99);
    let mut changed = 0usize;
    for _ in 0..1000 {
        let best = random_tree(&mut rng, 3);
        let out = perturb_best(&best, 1, 3, &mut rng, 25);
        assert!(out.size() <= 25, "size {} exceeds the cap", out.size());
        if out != best {
            changed += 1;
        }
    }
    assert!(changed > 900, "only {changed}/1000 perturbations changed the genome");
}

#[test]
fn the_legacy_default_is_unchanged_by_the_new_field() {
    let cfg = SearchConfig::default();
    assert_eq!(cfg.immigration_mode, ImmigrationMode::Legacy);
    assert!(!cfg.immigration);
    let points = sample_points(&mut Pcg64::seed_from_u64(20261024), 12);
    let t = rung("L3");
    let a = evolve(3, &t, &points, &SearchConfig { budget: 800, ..SearchConfig::default() });
    let b = evolve(3, &t, &points, &SearchConfig { budget: 800, immigration_mode: ImmigrationMode::Legacy, ..SearchConfig::default() });
    assert_eq!((a.solved, a.evaluations, a.tree_point_evaluations), (b.solved, b.evaluations, b.tree_point_evaluations));
}
