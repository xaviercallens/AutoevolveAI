//! `kge ladder` runs Kernel-Gated Evolution over the calibration ladder and
//! emits a JSON report plus Lean candidate files for the kernel gate.
//! `kge hillclimb` runs the population against a plain hill-climber on the same
//! seeds, points and budget, which is the control the population must beat.
//!
//! The kernel gate itself is NOT run here. Lean verification in this project goes
//! through `anse/formal/lean_runner.py` only, so this binary renders candidates
//! and their obligations and leaves acceptance to that gate.

use kernel_gated_evolution::{
    checkpoint, evolve, fitness, hill_climb, sample_points, target_ladder, Checkpoint, Env,
    Rat, SearchConfig,
};
use num_bigint::BigInt;
use num_traits::Zero;
use rand::SeedableRng;
use rand_pcg::Pcg64;
use serde::Serialize;
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::str::FromStr;

#[derive(Serialize)]
struct RungReport {
    rung: String,
    target_size: usize,
    target_lean: String,
    seeds: usize,
    solved: usize,
    solve_rate: f64,
    median_evaluations_when_solved: Option<f64>,
    median_inert_fraction_of_best: f64,
    distinct_solutions: usize,
    checkpoint_refuted_nonsolutions: usize,
    checkpoint_passed_solutions: usize,
    arms: Vec<kernel_gated_evolution::ArmResult>,
}

#[derive(Serialize)]
struct Report {
    algorithm: &'static str,
    parameters: HashMap<&'static str, usize>,
    points_source: String,
    rungs: Vec<RungReport>,
    lean_candidates_dir: Option<String>,
}

#[derive(Serialize)]
struct ClimbRung {
    rung: String,
    target_size: usize,
    seeds: usize,
    ga_solved: usize,
    descent_solved: usize,
    restarts_solved: usize,
    ga_rate: f64,
    descent_rate: f64,
    restarts_rate: f64,
    paired_ga_only: usize,
    paired_restarts_only: usize,
    paired_both: usize,
    median_restarts: f64,
}

#[derive(Serialize)]
struct ClimbReport {
    question: &'static str,
    fairness: &'static str,
    parameters: HashMap<&'static str, usize>,
    points_source: String,
    rungs: Vec<ClimbRung>,
}

fn median(mut v: Vec<f64>) -> Option<f64> {
    if v.is_empty() {
        return None;
    }
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let n = v.len();
    Some(if n % 2 == 1 { v[n / 2] } else { (v[n / 2 - 1] + v[n / 2]) / 2.0 })
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1).cloned())
}

/// Parse a rational written as "n/d" or "n".
fn parse_rat(text: &str) -> Rat {
    let mut parts = text.split('/');
    let n = BigInt::from_str(parts.next().unwrap().trim()).expect("numerator");
    let d = parts
        .next()
        .map(|d| BigInt::from_str(d.trim()).expect("denominator"))
        .unwrap_or_else(|| BigInt::from(1));
    Rat::new(n, d)
}

/// Sample points: the crate's own seeded draw, or a JSON file of
/// `[["n/d","n/d","n/d","n/d"], ...]` so a run can be made on exactly the points
/// another implementation used.
fn load_points(args: &[String]) -> (Vec<Env>, String) {
    if let Some(path) = arg(args, "--points-file") {
        let text = fs::read_to_string(&path).expect("read --points-file");
        let raw: Vec<Vec<String>> = serde_json::from_str(&text).expect("points JSON");
        let points: Vec<Env> = raw
            .iter()
            .map(|row| {
                assert_eq!(row.len(), 4, "each point needs four values");
                [parse_rat(&row[0]), parse_rat(&row[1]), parse_rat(&row[2]), parse_rat(&row[3])]
            })
            .collect();
        (points, format!("file:{path}"))
    } else {
        let mut point_rng = Pcg64::seed_from_u64(20261024);
        (sample_points(&mut point_rng, 12), "pcg64(20261024)".to_string())
    }
}

fn selected(args: &[String]) -> Option<Vec<String>> {
    arg(args, "--rungs").map(|s| s.split(',').map(|x| x.to_string()).collect())
}

fn run_ladder(args: &[String]) {
    let seeds: usize = arg(args, "--seeds").and_then(|s| s.parse().ok()).unwrap_or(24);
    let budget: usize = arg(args, "--budget").and_then(|s| s.parse().ok()).unwrap_or(4000);
    let out = PathBuf::from(arg(args, "--out").expect("--out is required"));
    let only = selected(args);
    let lean_out = arg(args, "--lean-out").map(PathBuf::from);
    let (points, points_source) = load_points(args);
    let config = SearchConfig { budget, ..SearchConfig::default() };

    if let Some(dir) = &lean_out {
        fs::create_dir_all(dir).expect("cannot create --lean-out");
    }

    let mut rungs = Vec::new();
    for (name, target) in target_ladder() {
        if let Some(only) = &only {
            if !only.iter().any(|r| r == name) {
                continue;
            }
        }
        // Positive control: the target must score exactly zero against itself.
        let want: Vec<Rat> = points.iter().map(|e| target.eval(e)).collect();
        assert!(fitness(&target, &points, &want).is_zero(), "{name}: target is not a solution");

        let arms: Vec<_> = (0..seeds as u64).map(|s| evolve(s, &target, &points, &config)).collect();
        let solved: Vec<_> = arms.iter().filter(|a| a.solved).collect();

        let mut distinct: Vec<String> = Vec::new();
        for (i, a) in arms.iter().enumerate() {
            if let Some(term) = &a.solution_lean {
                if !distinct.contains(term) {
                    distinct.push(term.clone());
                }
                if let Some(dir) = &lean_out {
                    let ns = format!("{}_S{}", name.replace('-', "_"), i);
                    let src = format!(
                        "import Mathlib.Tactic.Ring\nnamespace {ns}\n\
                         def candQ (h w q p : Rat) : Rat := {term}\n\
                         theorem {ns}_m (h w q p : Rat) : candQ h w q p = RungSpec.specQ h w q p := by\n\
                         \x20 unfold candQ RungSpec.specQ; ring\nend {ns}\n"
                    );
                    fs::write(dir.join(format!("{ns}.lean")), src).expect("write candidate");
                }
            }
        }

        // Exercise the checkpoint as a control with a known answer: each rung's
        // target must SURVIVE its own checkpoint, and every other rung's target
        // must be REFUTED by it. For six rungs the correct counts are exactly
        // 1 passed and 5 refuted; anything else means the checkpoint is wrong.
        let mut refuted_nonsolutions = 0;
        let mut passed_solutions = 0;
        for (other_name, other) in target_ladder() {
            match checkpoint(&other, &target, &points) {
                Checkpoint::Survives if other_name == name => passed_solutions += 1,
                Checkpoint::Refuted { .. } if other_name != name => refuted_nonsolutions += 1,
                _ => {}
            }
        }

        if let Some(dir) = &lean_out {
            let spec = format!(
                "import Mathlib.Tactic.Ring\nnamespace RungSpec\n\
                 def specQ (h w q p : Rat) : Rat := {}\nend RungSpec\n",
                target.render_lean()
            );
            fs::write(dir.join(format!("RungSpec_{name}.lean")), spec).expect("write spec");
        }

        let report = RungReport {
            rung: name.to_string(),
            target_size: target.size(),
            target_lean: target.render_lean(),
            seeds,
            solved: solved.len(),
            solve_rate: solved.len() as f64 / seeds as f64,
            median_evaluations_when_solved: median(
                solved.iter().map(|a| a.evaluations as f64).collect(),
            ),
            median_inert_fraction_of_best: median(
                arms.iter().map(|a| a.inert_fraction_of_best).collect(),
            )
            .unwrap_or(0.0),
            distinct_solutions: distinct.len(),
            checkpoint_refuted_nonsolutions: refuted_nonsolutions,
            checkpoint_passed_solutions: passed_solutions,
            arms,
        };
        println!(
            "  {:<20} size={:>2}  solved {:>3}/{}  ({:.3})  med_evals={:?}  inert_frac={:.3}  distinct={}  checkpoint: {} refuted / {} passed",
            report.rung,
            report.target_size,
            report.solved,
            seeds,
            report.solve_rate,
            report.median_evaluations_when_solved,
            report.median_inert_fraction_of_best,
            report.distinct_solutions,
            report.checkpoint_refuted_nonsolutions,
            report.checkpoint_passed_solutions
        );
        rungs.push(report);
    }

    let mut parameters = HashMap::new();
    parameters.insert("seeds", seeds);
    parameters.insert("budget", budget);
    parameters.insert("sample_points", points.len());
    parameters.insert("population_size", config.population_size);
    parameters.insert("max_size", config.max_size);
    parameters.insert("tournament", config.tournament);
    let report = Report {
        algorithm: "Kernel-Gated Evolution (Rust): mutation-selection + apoptotic checkpoint + exact dosage; Lean kernel decides acceptance via anse/formal/lean_runner.py",
        parameters,
        points_source,
        rungs,
        lean_candidates_dir: lean_out.map(|p| p.display().to_string()),
    };
    fs::write(&out, serde_json::to_string_pretty(&report).unwrap()).expect("write report");
    println!("wrote {}", out.display());
}

fn run_hillclimb(args: &[String]) {
    let seeds: usize = arg(args, "--seeds").and_then(|s| s.parse().ok()).unwrap_or(200);
    let budget: usize = arg(args, "--budget").and_then(|s| s.parse().ok()).unwrap_or(4000);
    let neighbours: usize = arg(args, "--neighbours").and_then(|s| s.parse().ok()).unwrap_or(8);
    let out = PathBuf::from(arg(args, "--out").expect("--out is required"));
    let only = selected(args);
    let (points, points_source) = load_points(args);
    let config = SearchConfig { budget, ..SearchConfig::default() };

    let mut rungs = Vec::new();
    for (name, target) in target_ladder() {
        if let Some(only) = &only {
            if !only.iter().any(|r| r == name) {
                continue;
            }
        }
        let (mut ga_solved, mut descent_solved, mut restarts_solved) = (0, 0, 0);
        let (mut ga_only, mut restarts_only, mut both) = (0, 0, 0);
        let mut restart_counts = Vec::new();
        for seed in 0..seeds as u64 {
            let ga = evolve(seed, &target, &points, &config).solved;
            let descent =
                hill_climb(seed, &target, &points, budget, config.max_size, neighbours, false).solved;
            let climb = hill_climb(seed, &target, &points, budget, config.max_size, neighbours, true);
            restart_counts.push(climb.restarts as f64);
            ga_solved += ga as usize;
            descent_solved += descent as usize;
            restarts_solved += climb.solved as usize;
            match (ga, climb.solved) {
                (true, true) => both += 1,
                (true, false) => ga_only += 1,
                (false, true) => restarts_only += 1,
                (false, false) => {}
            }
        }
        let rung = ClimbRung {
            rung: name.to_string(),
            target_size: target.size(),
            seeds,
            ga_solved,
            descent_solved,
            restarts_solved,
            ga_rate: ga_solved as f64 / seeds as f64,
            descent_rate: descent_solved as f64 / seeds as f64,
            restarts_rate: restarts_solved as f64 / seeds as f64,
            paired_ga_only: ga_only,
            paired_restarts_only: restarts_only,
            paired_both: both,
            median_restarts: median(restart_counts).unwrap_or(0.0),
        };
        println!(
            "  {:<20} size={:>2}  GA={:.3}  descent={:.3}  descent+restarts={:.3}   paired: GA-only {} / climb-only {} / both {}",
            rung.rung, rung.target_size, rung.ga_rate, rung.descent_rate, rung.restarts_rate,
            rung.paired_ga_only, rung.paired_restarts_only, rung.paired_both
        );
        rungs.push(rung);
    }
    let mut parameters = HashMap::new();
    parameters.insert("seeds", seeds);
    parameters.insert("budget", budget);
    parameters.insert("neighbours_per_step", neighbours);
    parameters.insert("sample_points", points.len());
    parameters.insert("population_size", config.population_size);
    parameters.insert("max_size", config.max_size);
    let report = ClimbReport {
        question: "Does the population buy anything over a plain hill-climber on the same seeds, points and budget?",
        fairness: "The climber is charged the same fitness evaluations the GA is given, counted the same way; restarts are paid out of that budget. Same seed -> same initial tree as the GA's first individual family, same sample points. The paired columns count seeds where exactly one method solved (McNemar's discordant pairs).",
        parameters,
        points_source,
        rungs,
    };
    fs::write(&out, serde_json::to_string_pretty(&report).unwrap()).expect("write report");
    println!("wrote {}", out.display());
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("ladder") => run_ladder(&args),
        Some("hillclimb") => run_hillclimb(&args),
        _ => {
            eprintln!(
                "usage:\n  kge ladder    --seeds N --budget B --out FILE [--rungs A,B] [--lean-out DIR] [--points-file F]\n  kge hillclimb --seeds N --budget B --out FILE [--rungs A,B] [--neighbours K] [--points-file F]"
            );
            std::process::exit(2);
        }
    }
}
