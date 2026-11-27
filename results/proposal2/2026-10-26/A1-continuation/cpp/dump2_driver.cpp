// Dump driver 2 for proposal 2 / A1 continuation (L1 port of the remaining stages).
// Includes the UNMODIFIED corpus headers (via -I) and prints exact interval endpoints (integers u, v of [u/Q, v/Q],
// Q = 2^144). Everything printed is either a corpus global after the corpus functions ran (ts, orig, pts, cels, co, ...)
// or a value of a verbatim replica of a corpus function body with print statements added (the corpus keeps these values
// in function locals). Every replica is checked against the corpus run in the same process:
//   * table_states(): copy of the propagation loop of table(); its states are pushed through the corpus fh() again and
//     the resulting pts/cels must equal the corpus pts/cels bit for bit (else abort);
//   * core_test_dump(): copy of core_test(); per-cell (norm, dsm, sm2) and the running (bc, dsum, d2);
//   * bdsup_dump(), global_grid_dump(), inside_hess_dump(): copies with row checkpoints every STRIDE inner steps; their
//     final results must equal the corpus bdsup() result and the printed endpoints (checked here for bdsup, and
//     against the 22 record pairs by the Python side for the others).
// The corpus is never edited.
#include "grids.hpp"
#include <fstream>
#include <cstdlib>

static std::ofstream o;
static void pv(const IV& x) { o << ' ' << x.u << ' ' << x.v; }
static void put(const std::string& name, const IV& x) { o << name; pv(x); o << '\n'; }

static std::vector<SState> pointS, cellS;

static void table_states() {
    // verbatim copy of core.hpp:253-262 (state propagation), ts/orig already built by table(24000)
    pointS.assign(ts.size(), SState()); cellS.assign(ts.size() - 1, SState());
    JS initial = ss0(J(small)); SState S; S.s1 = initial.s1.A[0]; S.s2 = initial.s2.A[0];
    for (auto& kv : initial.ps) S.ps[kv.first] = kv.second.A[0];
    put("init_s1", S.s1); put("init_s2", S.s2);
    for (auto& kv : S.ps) { o << "init_ps " << kv.first; pv(kv.second); o << '\n'; }
    for (size_t i = 1; i < ts.size(); ++i) {
        IV x = ts[i], old = ts[i-1], H = x - old; int sgprev = orig[i-1];
        if (sgprev >= 1) {
            IV mid = (old + x) / 2; J tc{IV(old.u, x.v), one}, tm{mid, one};
            auto zm = dels(tm, sgprev), zc = dels(tc, sgprev); SState ns, bs;
            ns.s1 = S.s1 + integ(H, zm[0], zc[0]); ns.s2 = S.s2 + integ(H, zm[1], zc[1]);
            for (auto& kv : S.ps) { int ke = kv.first; ns.ps[ke] = pow(old/x, ke)*kv.second + integ(H, pow(tm/x, ke)*zm[2], pow(tc/x, ke)*zc[2]); }
            cpp_int bb = maxint(absint(zc[2].A[0].u), absint(zc[2].A[0].v)); IV err = H*IV(-bb, bb);
            bs.s1 = S.s1 + IV(0, H.v)*zc[0].A[0]; bs.s2 = S.s2 + IV(0, H.v)*zc[1].A[0];
            for (auto& kv : S.ps) bs.ps[kv.first] = pow(old/tc.A[0], kv.first)*kv.second + err;
            cellS[i-1] = std::move(bs); S = std::move(ns);
        }
        pointS[i] = S;
    }
    // re-derive pts/cels from the replica states with the corpus fh() and compare bit for bit
    long bad = 0;
    #pragma omp parallel for schedule(dynamic,4) reduction(+:bad)
    for (long i = 0; i < long(ts.size()); ++i) {
        J tt{ts[i], one}; auto pp = fh(tt, orig[i], orig[i]==0 ? nullptr : &pointS[i]);
        for (int k = 0; k < 6; ++k) if (pp[k].u != pts[i][k].u || pp[k].v != pts[i][k].v) ++bad;
        if (i > 0) { J tc{IV(ts[i-1].u, ts[i].v), one}; auto cc = fh(tc, orig[i-1], orig[i-1] < 1 ? nullptr : &cellS[i-1]);
            for (int k = 0; k < 6; ++k) if (cc[k].u != cels[i-1][k].u || cc[k].v != cels[i-1][k].v) ++bad; }
    }
    o << "table_replica_mismatches " << bad << '\n';
    if (bad) { std::cerr << "table replica mismatch\n"; std::exit(3); }
}

static void core_test_dump() {
    // verbatim copy of core.hpp:269-275 with prints
    IV h = rat(".00022"), bc, dsum, d2;
    for (int seg = 0; seg < 6; ++seg) {
        IV aa = breaks[seg], bb = breaks[seg+1]; int n = nsamp(aa, bb, h); std::vector<std::array<IV,3>> result(n);
        #pragma omp parallel for schedule(dynamic,4)
        for (int j = 0; j < n; ++j) {
            IV lo = aa + (bb-aa)*j/n, hi = aa + (bb-aa)*(j+1)/n; J tt{IV(lo.u, hi.v), one}; auto bd = basis(tt, seg);
            J bi = bd.first.der() + 1/tt; IV norm = abs(bi.A[0]) + abs(bi.A[1]) + abs(bi.A[2]), dsm, sm2;
            for (size_t i = 0; i < ks.size(); ++i) { IV v1; for (auto& x : bd.second[i].A) v1 += abs(x); dsm += pow(IV(ks[i]+1), 3)*v1; sm2 += pow(IV(ks[i]+1), 2)*v1; }
            result[j] = {norm, dsm, sm2};
        }
        o << "ct_seg " << seg << ' ' << n << '\n';
        for (int j = 0; j < n; ++j) { o << "ct " << seg << ' ' << j; pv(result[j][0]); pv(result[j][1]); pv(result[j][2]); o << '\n'; }
        for (auto& r : result) { if (r[0].v > bc.v) bc = r[0]; if (r[1].v > dsum.v) dsum = r[1]; if (r[2].v > d2.v) d2 = r[2]; }
        o << "ct_run " << seg; pv(bc); pv(dsum); pv(d2); o << '\n';
        if (!(bc.v < 6000*Q && dsum.v < 2000000*Q)) { std::cerr << "core_test bound failed\n"; std::exit(4); }
    }
}

static const int STRIDE_BD = 64, STRIDE_GG = 128, STRIDE_IH = 64;

static std::vector<IV> bdsup_dump() {
    const IV H = rat("0.0008"); const IV dlo = rat(".28209"), dup = rat(".697"), shi = rat(".65");
    const int nd = nsamp(dlo, dup, H), ns = nsamp(zero, shi, H); const IV hd = (dup-dlo)/nd, hs = shi/ns;
    o << "bd_mesh " << nd << ' ' << ns << '\n';
    std::vector<std::array<IV,5>> rows(nd); std::vector<std::vector<std::pair<int, std::array<IV,5>>>> cps(nd);
    #pragma omp parallel for schedule(dynamic,1)
    for (int j = 0; j < nd; ++j) {
        auto& row = rows[j]; for (auto& value : row) value = zero;
        const IV lo = dlo + hd*j; const IV d(lo.u, (lo+hd).v);
        for (int i = 0; i < ns; ++i) {
            const IV slo = hs*i; const IV s(slo.u, (slo+hs).v); const auto ranges = G(d, s, true);
            for (int k = 0; k < 5; ++k) row[k] = row[k].hull(ranges[k]);
            if ((i+1) % STRIDE_BD == 0 || i+1 == ns) cps[j].push_back({i+1, row});
        }
    }
    for (int j = 0; j < nd; ++j) for (auto& c : cps[j]) { o << "bd " << j << ' ' << c.first; for (auto& z : c.second) pv(z); o << '\n'; }
    std::vector<IV> b(5, zero); for (const auto& row : rows) for (int k = 0; k < 5; ++k) b[k] = b[k].hull(row[k]);
    for (int k = 0; k < 5; ++k) put("bd_out" + std::to_string(k), b[k]);
    return b;
}

static void global_grid_dump(const std::string& stepd, const std::string& stepx, const std::vector<IV>& supplied_bounds) {
    std::vector<IV> b; for (const auto& value : supplied_bounds) b.push_back(value.abs());
    const IV chi = b[4], Gdd = b[3], Gs = b[2], Gd = b[1];
    const IV Bmin = rat(".28209"), Tmax = rat(".697"), Smax = rat(".65");
    const IV dl = rat(".52528"), du = rat(".54930"), sl = rat(".29420"), su = rat(".32621");
    std::vector<IV> dseq, sseq;
    append_grid_seq(dseq, Bmin, dl, rat(stepd), false); append_grid_seq(dseq, dl, du, rat(stepd), false); append_grid_seq(dseq, du, Tmax, rat(stepd), true);
    append_grid_seq(sseq, zero, sl, rat(stepx), false); append_grid_seq(sseq, sl, su, rat(stepx), false); append_grid_seq(sseq, su, Smax, rat(stepx), true);
    const int nd = int(dseq.size()), ns = int(sseq.size()) - 1;
    o << "gg_mesh " << nd << ' ' << ns << '\n';
    for (int j = 0; j < nd; ++j) { o << "gg_d " << j; pv(dseq[j]); o << '\n'; }
    for (int i = 0; i <= ns; ++i) { o << "gg_s " << i; pv(sseq[i]); o << '\n'; }
    cpp_int hmax = 0, dmax = 0;
    for (int i = 0; i < ns; ++i) { const cpp_int width = sseq[i+1].v - sseq[i].u; if (width > hmax) hmax = width; }
    for (int i = 0; i < nd-1; ++i) { const cpp_int width = dseq[i+1].v - dseq[i].u; if (width > dmax) dmax = width; }
    const IV H(0, hmax), Dh(0, dmax);
    const IV er0 = 2*Smax*pow(H,2)*chi/24; const IV eri = 2*(pow(Dh,2)*Smax*Gdd + pow(H,2)*Gs)/8;
    const IV factor = er0 + IV(0, eri.v); const IV er_drop = Smax*(H/4*Gs + Dh/2*Gd);
    put("gg_factor", factor); put("gg_er_drop", er_drop);
    struct CP { int i; IV g, drop, gmin; };
    std::vector<std::vector<CP>> cps(nd); std::vector<std::array<IV,2>> rows(nd);
    #pragma omp parallel for schedule(dynamic,1)
    for (int j = 0; j < nd; ++j) {
        const IV& d = dseq[j]; const bool needall = d.u <= dl.v || d.v >= du.u;
        IV g = zero, drop = zero, gmin = 10*one; if ((-K).u < gmin.u) gmin = -K;
        cps[j].push_back({0, g, drop, gmin});
        for (int i = 0; i < ns; ++i) {
            const IV& lo = sseq[i]; const IV& hi = sseq[i+1]; const IV h = hi - lo;
            const IV gv = h*G(d, (lo+hi)/2); g = g + gv; const IV minus_gv_h = -gv/h;
            const IV clipped(std::max(cpp_int(0), minus_gv_h.u), std::max(cpp_int(0), minus_gv_h.v));
            drop = drop + h*clipped;
            if ((needall || hi.v <= sl.v || hi.u >= su.u)) { const IV value = 2*g - K; if (value.u < gmin.u) gmin = value; }
            if ((i+1) % STRIDE_GG == 0 || i+1 == ns) cps[j].push_back({i+1, g, drop, gmin});
        }
        rows[j] = {gmin, drop};
    }
    for (int j = 0; j < nd; ++j) for (auto& c : cps[j]) { o << "gg " << j << ' ' << c.i; pv(c.g); pv(c.drop); pv(c.gmin); o << '\n'; }
    IV gmin = 10*one, drneg = -10*one;
    for (const auto& row : rows) { if (row[0].u < gmin.u) gmin = row[0]; if (row[1].v > drneg.v) drneg = row[1]; }
    put("gg_gmin", gmin); put("gg_drneg", drneg);
    put("gg_gmin_minus_factor", gmin - factor); put("gg_neg_lhs", drneg + er_drop + K);
}

static void inside_hess_dump(const std::string& dxmax, const std::string& sxmax) {
    const IV dl = rat(".52528"), du = rat(".54930"), sl = rat(".29420"), su = rat(".32621");
    const auto dseq = grid_seq(dl, du, rat(dxmax)); std::vector<IV> xseq;
    append_grid_seq(xseq, zero, sl, rat(sxmax), false); append_grid_seq(xseq, sl, su, rat(sxmax), true);
    const int nd = int(dseq.size()) - 1, ns = int(xseq.size()) - 1;
    o << "ih_mesh " << nd << ' ' << ns << '\n';
    for (int j = 0; j <= nd; ++j) { o << "ih_d " << j; pv(dseq[j]); o << '\n'; }
    for (int i = 0; i <= ns; ++i) { o << "ih_s " << i; pv(xseq[i]); o << '\n'; }
    struct Row { IV dd, dgl, glx, glxx, det; bool init = false; std::uint64_t failures = 0; };
    std::vector<std::vector<std::pair<int, Row>>> cps(nd); std::vector<Row> rows(nd);
    #pragma omp parallel for schedule(dynamic,1)
    for (int j = 0; j < nd; ++j) {
        const IV d(dseq[j].u, dseq[j+1].v); Row row; row.dd = zero;
        cps[j].push_back({0, row});
        for (int i = 0; i < ns; ++i) {
            const IV& lsx = xseq[i]; const IV& usx = xseq[i+1]; const IV sx(lsx.u, usx.v), h = usx - lsx;
            const auto values = G(d, sx, true); const IV& xdi = values[1]; const IV& xxi = values[2]; const IV& sd2 = values[3];
            const IV ddcc = row.dd + IV(0, h.v)*sd2; row.dd = row.dd + h*sd2;
            if (usx.u >= sl.u) {
                const IV det = ddcc*xxi - xdi*xdi;
                if (!row.init) { row.dgl = ddcc; row.glx = xdi; row.glxx = xxi; row.det = det; row.init = true; }
                else { row.dgl = row.dgl.hull(ddcc); row.glx = row.glx.hull(xdi); row.glxx = row.glxx.hull(xxi); row.det = row.det.hull(det); }
                if (ddcc.u <= 0 || xxi.u <= 0 || det.u <= 0) ++row.failures;
            }
            if ((i+1) % STRIDE_IH == 0 || i+1 == ns) cps[j].push_back({i+1, row});
        }
        rows[j] = row;
    }
    for (int j = 0; j < nd; ++j) for (auto& c : cps[j]) { const Row& r = c.second;
        o << "ih " << j << ' ' << c.first << ' ' << (r.init ? 1 : 0) << ' ' << r.failures; pv(r.dd); pv(r.dgl); pv(r.glx); pv(r.glxx); pv(r.det); o << '\n'; }
    IV dgl = zero, glx = zero, glxx = zero, min_det = zero; bool init = false;
    for (const auto& r : rows) { if (!r.init || r.failures) { std::cerr << "inside_hess row failure\n"; std::exit(5); }
        if (!init) { dgl = r.dgl; glx = r.glx; glxx = r.glxx; min_det = r.det; init = true; }
        else { dgl = dgl.hull(r.dgl); glx = glx.hull(r.glx); glxx = glxx.hull(r.glxx); min_det = min_det.hull(r.det); } }
    put("ih_dgl", dgl); put("ih_glx", glx); put("ih_glxx", glxx); put("ih_det", min_det);
}

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: dump2_driver OUTFILE\n"; return 2; }
    o.open(argv[1]);
    init_constants();
    put("ln2", ln2); put("pi", pi); put("p", p); put("R", R); put("a", a);
    init_core();  // cs, init_after_co, table(24000), bcons/eps, core_test (corpus)
    for (int m = 1; m <= M; ++m) put("co" + std::to_string(m), co[m]);
    put("hx", hx); put("l", l); put("bcons", bcons); put("eps", eps); put("small", small); put("cut", cut); put("v", v);
    for (size_t i = 0; i < breaks.size(); ++i) put("break" + std::to_string(i), breaks[i]);
    o << "ntable " << ts.size() << '\n';
    for (size_t i = 0; i < ts.size(); ++i) { o << "node " << i << ' ' << orig[i]; pv(ts[i]); for (auto& z : pts[i]) pv(z); o << '\n'; }
    for (size_t i = 0; i < cels.size(); ++i) { o << "cell " << i; for (auto& z : cels[i]) pv(z); o << '\n'; }
    o.flush();
    table_states();
    for (size_t i = 0; i < ts.size(); ++i) { const SState& s = pointS[i]; o << "pS " << i << ' ' << s.ps.size(); pv(s.s1); pv(s.s2); for (auto& kv : s.ps) { o << ' ' << kv.first; pv(kv.second); } o << '\n'; }
    for (size_t i = 0; i < cellS.size(); ++i) { const SState& s = cellS[i]; o << "cS " << i << ' ' << s.ps.size(); pv(s.s1); pv(s.s2); for (auto& kv : s.ps) { o << ' ' << kv.first; pv(kv.second); } o << '\n'; }
    o.flush();
    core_test_dump(); o.flush();
    calcLam(); put("lambda", lambda_); put("mu", mu);
    calcK(); put("K", K); o.flush();
    const auto bs = bdsup(); for (int k = 0; k < 5; ++k) put("bound" + std::to_string(k), bs[k]);
    const auto bs2 = bdsup_dump();
    for (int k = 0; k < 5; ++k) if (bs2[k].u != bs[k].u || bs2[k].v != bs[k].v) { std::cerr << "bdsup replica mismatch\n"; return 6; }
    o << "bdsup_replica_ok\n"; o.flush();
    global_grid_dump(".00019", ".00018", bs); o.flush();
    inside_hess_dump(".00004", ".00008");
    o << "DONE\n";
    return 0;
}
