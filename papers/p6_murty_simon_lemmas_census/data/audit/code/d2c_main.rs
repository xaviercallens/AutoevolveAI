// Independent D2C filter (auditor). Reads graph6 on stdin, writes D2C graphs to file arg1.
// Method: common-neighbour characterisation of edge criticality, plus optional BFS brute force (arg2 == "bfs").
use std::io::{self, BufRead, BufWriter, Write};

fn parse_g6(s: &[u8]) -> (usize, Vec<u32>) {
    let n = (s[0] - 63) as usize;
    let mut adj = vec![0u32; n];
    let mut k = 0usize;
    for j in 1..n {
        for i in 0..j {
            let byte = (s[1 + k / 6] - 63) as u32;
            if (byte >> (5 - (k % 6))) & 1 == 1 {
                adj[i] |= 1 << j;
                adj[j] |= 1 << i;
            }
            k += 1;
        }
    }
    (n, adj)
}

fn diam_le2(n: usize, adj: &[u32]) -> bool {
    for i in 0..n {
        for j in (i + 1)..n {
            if adj[i] >> j & 1 == 0 && adj[i] & adj[j] == 0 {
                return false;
            }
        }
    }
    true
}

fn is_d2c_cn(n: usize, adj: &[u32]) -> bool {
    let full: u32 = (1u32 << n) - 1;
    if (0..n).all(|i| adj[i] | (1 << i) == full) {
        return false;
    }
    if !diam_le2(n, adj) {
        return false;
    }
    for u in 0..n {
        for v in (u + 1)..n {
            if adj[u] >> v & 1 == 0 {
                continue;
            }
            let mut crit = adj[u] & adj[v] == 0;
            if !crit {
                for (a, b) in [(u, v), (v, u)] {
                    let mut cand = !adj[a] & full & !(1 << a) & !(1 << b);
                    while cand != 0 {
                        let x = cand.trailing_zeros() as usize;
                        cand &= cand - 1;
                        if adj[a] & adj[x] == (1 << b) {
                            crit = true;
                            break;
                        }
                    }
                    if crit {
                        break;
                    }
                }
            }
            if !crit {
                return false;
            }
        }
    }
    true
}

fn ecc_ok_bfs(n: usize, adj: &[u32]) -> bool {
    for s in 0..n {
        let mut dist = vec![usize::MAX; n];
        dist[s] = 0;
        let mut q = std::collections::VecDeque::new();
        q.push_back(s);
        while let Some(x) = q.pop_front() {
            for y in 0..n {
                if adj[x] >> y & 1 == 1 && dist[y] == usize::MAX {
                    dist[y] = dist[x] + 1;
                    q.push_back(y);
                }
            }
        }
        if dist.iter().any(|&d| d > 2) {
            return false;
        }
    }
    true
}

fn is_d2c_bfs(n: usize, adj: &[u32]) -> bool {
    let full: u32 = (1u32 << n) - 1;
    if (0..n).all(|i| adj[i] | (1 << i) == full) {
        return false;
    }
    if !ecc_ok_bfs(n, adj) {
        return false;
    }
    let mut a = adj.to_vec();
    for u in 0..n {
        for v in (u + 1)..n {
            if adj[u] >> v & 1 == 0 {
                continue;
            }
            a[u] &= !(1 << v);
            a[v] &= !(1 << u);
            let still = ecc_ok_bfs(n, &a);
            a[u] |= 1 << v;
            a[v] |= 1 << u;
            if still {
                return false;
            }
        }
    }
    true
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let out = std::fs::File::create(&args[1]).unwrap();
    let mut w = BufWriter::new(out);
    let both = args.len() > 2 && args[2] == "bfs";
    let stdin = io::stdin();
    let mut lock = stdin.lock();
    let mut line = Vec::new();
    let (mut total, mut hits, mut mism) = (0u64, 0u64, 0u64);
    loop {
        line.clear();
        if lock.read_until(b'\n', &mut line).unwrap() == 0 {
            break;
        }
        let s = if line.last() == Some(&b'\n') { &line[..line.len() - 1] } else { &line[..] };
        if s.is_empty() {
            continue;
        }
        total += 1;
        let (n, adj) = parse_g6(s);
        let d = is_d2c_cn(n, &adj);
        if both && d != is_d2c_bfs(n, &adj) {
            mism += 1;
        }
        if d {
            hits += 1;
            w.write_all(s).unwrap();
            w.write_all(b"\n").unwrap();
        }
    }
    eprintln!(
        "total {} d2c {} bfs_mismatch {}",
        total,
        hits,
        if both { mism.to_string() } else { "n/a".into() }
    );
}
