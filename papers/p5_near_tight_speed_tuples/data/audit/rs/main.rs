// Auditor's independent near-tight screen (LR-SPEC audit). Not derived from the producer's C.
// Method: the witness set is EVERY reduced fraction a/b in (0, 1/2] with b <= 2N.
// Every candidate time of Cordella Lemma 2.2 (m/(vi+vj), m/|vi-vj|, peaks (2m+1)/(2vi)) reduces to such
// a fraction (or its mirror 1-t), so: tuple NOT near-tight  <=>  some fraction in the set has n*||t v_i|| >= 1 for all i.
// Hence near-tight <=> AND of per-speed bitsets is zero. No second "exact stage" is needed.
// ML for near-tight primitive tuples: max over the same full fraction set of min_i ||a v_i / b||, exact integers.
// usage: nt n N threads out_file [strict]
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

struct Ctx {
    n: usize,
    nmax: usize,
    words: usize,
    masks: Vec<Vec<u64>>, // masks[s][w]
    fracs: Vec<(u64, u64)>,
}

fn ml_exact(ctx: &Ctx, v: &[u64]) -> (u64, u64) {
    // best = bn/bd
    let (mut bn, mut bd) = (0u64, 1u64);
    for &(a, b) in &ctx.fracs {
        let mut mn = b;
        for &x in v {
            let r = (a * x) % b;
            let d = if r < b - r { r } else { b - r };
            if d < mn {
                mn = d;
            }
        }
        if mn * bd > bn * b {
            bn = mn;
            bd = b;
        }
    }
    let g = gcd(bn, bd);
    (bn / g, bd / g)
}

struct Out {
    survivors: u64,
    lines: Vec<String>,
    tuples: u64,
    nt_all: u64,
}

fn dfs(ctx: &Ctx, depth: usize, last: usize, cur: &[(usize, u64)], v: &mut Vec<u64>, out: &mut Out) {
    let n = ctx.n;
    if depth == n - 1 {
        for s in (last + 1)..=ctx.nmax {
            out.tuples += 1;
            let m = &ctx.masks[s];
            let mut hit = false;
            for &(w, x) in cur {
                if x & m[w] != 0 {
                    hit = true;
                    break;
                }
            }
            if !hit {
                v.push(s as u64);
                leaf(ctx, v, out);
                v.pop();
            }
        }
        return;
    }
    let mut nxt: Vec<(usize, u64)> = Vec::with_capacity(cur.len());
    for s in (last + 1)..=(ctx.nmax - (n - 1 - depth)) {
        nxt.clear();
        let m = &ctx.masks[s];
        for &(w, x) in cur {
            let y = x & m[w];
            if y != 0 {
                nxt.push((w, y));
            }
        }
        v.push(s as u64);
        dfs(ctx, depth + 1, s, &nxt, v, out);
        v.pop();
    }
}

const PREW: usize = 6;

fn full_witness(ctx: &Ctx, v: &[u64]) -> bool {
    let n = ctx.n as u64;
    for &(a, b) in &ctx.fracs {
        let mut ok = true;
        for &x in v {
            let r = (a * x) % b;
            let d = if r < b - r { r } else { b - r };
            if n * d < b {
                ok = false;
                break;
            }
        }
        if ok {
            return true;
        }
    }
    false
}

fn dfs_pre(ctx: &Ctx, depth: usize, last: usize, cur: &[u64; PREW], v: &mut Vec<u64>, out: &mut Out) {
    let n = ctx.n;
    if depth == n - 1 {
        for s in (last + 1)..=ctx.nmax {
            out.tuples += 1;
            let m = &ctx.masks[s];
            let mut acc = 0u64;
            for w in 0..PREW {
                acc |= cur[w] & m[w];
            }
            if acc == 0 {
                v.push(s as u64);
                out.survivors += 1;
                if !full_witness(ctx, v) {
                    leaf(ctx, v, out);
                }
                v.pop();
            }
        }
        return;
    }
    let mut nxt = [0u64; PREW];
    for s in (last + 1)..=(ctx.nmax - (n - 1 - depth)) {
        let m = &ctx.masks[s];
        for w in 0..PREW {
            nxt[w] = cur[w] & m[w];
        }
        v.push(s as u64);
        dfs_pre(ctx, depth + 1, s, &nxt, v, out);
        v.pop();
    }
}

fn leaf(ctx: &Ctx, v: &[u64], out: &mut Out) {
    out.nt_all += 1;
    let mut g = 0;
    for &x in v {
        g = gcd(g, x);
    }
    if g != 1 {
        return;
    }
    let (p, q) = ml_exact(ctx, v);
    let n = ctx.n as u64;
    // sanity: must be < 1/n
    // in the correct mode this can never fire (mask test is exact); in strict (corrupted) mode ML may equal 1/n
    let k = if n * p < q { q - n * p } else { 0 };
    let mut s = String::new();
    for x in v {
        s.push_str(&format!("{} ", x));
    }
    s.push_str(&format!("{} {} {}", p, q, k));
    out.lines.push(s);
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let n: usize = args[1].parse().unwrap();
    let nmax: usize = args[2].parse().unwrap();
    let threads: usize = args[3].parse().unwrap();
    let outf = args[4].clone();
    let strict = args.len() > 5 && args[5] == "strict"; // corrupted: n*d > b
    let pre = args.len() > 6 && args[6] == "pre";
    let bmax = 2 * nmax as u64;
    let mut fracs = Vec::new();
    for b in 2..=bmax {
        for a in 1..=(b / 2) {
            if gcd(a, b) == 1 {
                fracs.push((a, b));
            }
        }
    }
    let words = (fracs.len() + 63) / 64;
    let mut masks = vec![vec![0u64; words]; nmax + 1];
    for s in 1..=nmax {
        for (i, &(a, b)) in fracs.iter().enumerate() {
            let r = (a * s as u64) % b;
            let d = if r < b - r { r } else { b - r };
            let far = if strict { (n as u64) * d > b } else { (n as u64) * d >= b };
            if far {
                masks[s][i / 64] |= 1u64 << (i % 64);
            }
        }
    }
    eprintln!("n={} N={} fractions={} words={} strict={}", n, nmax, fracs.len(), words, strict);
    let ctx = Arc::new(Ctx { n, nmax, words, masks, fracs });
    // work items: (v1, v2)
    let mut items = Vec::new();
    for a in 1..=nmax {
        for b in (a + 1)..=nmax {
            if b + (n - 2) <= nmax {
                items.push((a, b));
            }
        }
    }
    let items = Arc::new(items);
    let next = Arc::new(AtomicUsize::new(0));
    let res = Arc::new(Mutex::new(Out { survivors: 0, lines: vec![], tuples: 0, nt_all: 0 }));
    let mut hs = vec![];
    for _ in 0..threads {
        let ctx = ctx.clone();
        let items = items.clone();
        let next = next.clone();
        let res = res.clone();
        hs.push(std::thread::spawn(move || {
            let mut out = Out { survivors: 0, lines: vec![], tuples: 0, nt_all: 0 };
            let mut v: Vec<u64> = Vec::with_capacity(16);
            loop {
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= items.len() {
                    break;
                }
                let (a, b) = items[i];
                let mut cur: Vec<(usize, u64)> = Vec::new();
                for w in 0..ctx.words {
                    let y = ctx.masks[a][w] & ctx.masks[b][w];
                    if y != 0 {
                        cur.push((w, y));
                    }
                }
                v.clear();
                v.push(a as u64);
                v.push(b as u64);
                if ctx.n == 2 {
                    out.tuples += 1;
                    if cur.is_empty() {
                        leaf(&ctx, &v, &mut out);
                    }
                    continue;
                }
                if pre {
                    let mut c = [0u64; PREW];
                    for w in 0..PREW {
                        c[w] = ctx.masks[a][w] & ctx.masks[b][w];
                    }
                    dfs_pre(&ctx, 2, b, &c, &mut v, &mut out);
                } else {
                    dfs(&ctx, 2, b, &cur, &mut v, &mut out);
                }
            }
            let mut r = res.lock().unwrap();
            r.tuples += out.tuples;
            r.nt_all += out.nt_all;
            r.survivors += out.survivors;
            r.lines.extend(out.lines);
        }));
    }
    for h in hs {
        h.join().unwrap();
    }
    let mut r = res.lock().unwrap();
    r.lines.sort_by_key(|l| l.split_whitespace().map(|x| x.parse::<u64>().unwrap()).collect::<Vec<_>>());
    let mut f = std::fs::File::create(&outf).unwrap();
    for l in &r.lines {
        writeln!(f, "{}", l).unwrap();
    }
    eprintln!("tuples={} survivors={} neartight_all={} primitive={} pre={}", r.tuples, r.survivors, r.nt_all, r.lines.len(), pre);
}
