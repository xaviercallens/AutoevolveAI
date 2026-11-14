// Dump driver for proposal 2 / A1a. Includes the UNMODIFIED corpus headers (via -I) and prints exact
// interval endpoints (integers u, v of [u/Q, v/Q], Q = 2^144) of the stage outputs needed for the Lean port.
// It reruns the same stage functions as run_certificate() up to bdsup; it never edits the corpus.
#include "grids.hpp"
#include <fstream>

static void put(std::ostream& o, const std::string& name, const IV& x) { o << name << ' ' << x.u << ' ' << x.v << '\n'; }

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: dump_driver OUTFILE\n"; return 2; }
    std::ofstream o(argv[1]);
    init_constants();
    put(o, "ln2", ln2); put(o, "pi", pi); put(o, "p", p); put(o, "R", R); put(o, "a", a);
    o.flush();
    init_core();
    for (int m = 1; m <= M; ++m) put(o, "co" + std::to_string(m), co[m]);
    put(o, "hx", hx); put(o, "l", l); put(o, "bcons", bcons); put(o, "eps", eps);
    o << "ntable " << ts.size() << '\n';
    o.flush();
    calcLam();
    put(o, "lambda", lambda_); put(o, "mu", mu);
    calcK();
    put(o, "K", K);
    const IV f0l = pts.back()[0] + eps;
    put(o, "f0l", f0l);
    put(o, "fl", f0l - lambda_ * l * l / 2 - mu);
    put(o, "slope", -pi * bcons - lambda_ / 2);
    put(o, "rat_m6731", rat("-6.731")); put(o, "rat_m6729", rat("-6.729"));
    // Table cells used by calcK: t in [p, sqrt(p^2+(R/2)^2)].
    const IV tmax = (p * p + (R / 2) * (R / 2)).sqrt();
    int im = std::max(0, int(std::lower_bound(VIL.begin(), VIL.end(), p.u) - VIL.begin()) - 1);
    int ix = std::min(int(cels.size()), int(std::upper_bound(UIL.begin(), UIL.end(), tmax.v) - UIL.begin()));
    o << "calcK_cells " << im << ' ' << ix << '\n';
    for (int i = im; i <= ix && i < int(ts.size()); ++i) {
        o << "node " << i << ' ' << ts[i].u << ' ' << ts[i].v;
        for (auto& z : pts[i]) o << ' ' << z.u << ' ' << z.v;
        o << '\n';
        if (i < int(cels.size())) {
            o << "cell " << i;
            for (auto& z : cels[i]) o << ' ' << z.u << ' ' << z.v;
            o << '\n';
        }
    }
    // Sample simple-G evaluations exactly as calcK forms them (first 8 midpoints).
    const int m = nsamp(zero, R / 2, rat(".0001"));
    const IV h = (R / 2) / m;
    o << "calcK_m " << m << '\n';
    put(o, "calcK_h", h);
    for (int i = 0; i < 8; ++i) { const IV sv = (i + rat(1, 2)) * h; put(o, "Gs_arg" + std::to_string(i), sv); put(o, "Gs_val" + std::to_string(i), G(p, sv)); }
    o.flush();
    const auto bs = bdsup();
    for (int k = 0; k < 5; ++k) put(o, "bound" + std::to_string(k), bs[k]);
    o << "DONE\n";
    return 0;
}
