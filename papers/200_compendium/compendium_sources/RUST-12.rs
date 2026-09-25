use std::cmp::Ordering;
use std::collections::BinaryHeap;

#[derive(Copy, Clone, Eq, PartialEq)]
struct State { cost: u64, node: usize }
impl Ord for State {
    fn cmp(&self, o: &Self) -> Ordering { o.cost.cmp(&self.cost) }
}
impl PartialOrd for State {
    fn partial_cmp(&self, o: &Self) -> Option<Ordering> { Some(self.cmp(o)) }
}

fn main() {
    let n = std::hint::black_box(100);
    let mut adj = vec![vec![]; n];
    for i in 0..n {
        for step in [1, 2, 5, 13] {
            let j = (i + step) % n;
            let w = ((i * 17 + j * 23) % 50 + 1) as u64;
            adj[i].push((j, w));
        }
    }
    let mut dist = vec![u64::MAX; n];
    let mut heap = BinaryHeap::new();
    dist[0] = 0;
    heap.push(State { cost: 0, node: 0 });
    while let Some(State { cost, node }) = heap.pop() {
        if cost > dist[node] { continue; }
        for &(next, weight) in &adj[node] {
            let next_cost = cost + weight;
            if next_cost < dist[next] {
                dist[next] = next_cost;
                heap.push(State { cost: next_cost, node: next });
            }
        }
    }
    let mut triangle_violations = 0;
    for u in 0..n {
        if dist[u] == u64::MAX { continue; }
        for &(v, w) in &adj[u] {
            if dist[v] > dist[u] + w { triangle_violations += 1; }
        }
    }
    println!("INVARIANT_CHECK: {}", if triangle_violations == 0 { "PASSED" } else { "FAILED" });
    println!("INVARIANT_ERROR: {:.10e}", triangle_violations as f64);
}