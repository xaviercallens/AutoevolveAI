//! Negative-control probe for `verify_sqisign_response` (Paper C, edition 2).
//!
//! Input (argv): one or more cases `label:a:b:c:d` for elements a + b i + c j + d k of the
//! Lipschitz lattice in B_{3,inf} (i^2 = -1, j^2 = -3).  For each case the probe calls
//! `verify_sqisign_response(&q, 2, 16, 6561)` exactly as edition 1's Table 2 did and prints one
//! JSON object per line: label, coordinates, reduced norm, verified flag.
use sqisign_flt_verifier::{verify_sqisign_response, DeuringQuaternionOrderElement};

fn main() {
    for arg in std::env::args().skip(1) {
        let parts: Vec<&str> = arg.split(':').collect();
        assert_eq!(parts.len(), 5, "case must be label:a:b:c:d");
        let v: Vec<i128> = parts[1..].iter().map(|s| s.parse().expect("integer")).collect();
        let q = DeuringQuaternionOrderElement { p_char: 3, q_norm: 1, a: v[0], b: v[1], c: v[2], d: v[3] };
        let cert = verify_sqisign_response(&q, 2, 16, 6561);
        println!(
            "{{\"label\":\"{}\",\"a\":{},\"b\":{},\"c\":{},\"d\":{},\"nrd\":{},\"verified\":{}}}",
            parts[0], v[0], v[1], v[2], v[3], cert.quaternion_reduced_norm, cert.verified
        );
    }
}
