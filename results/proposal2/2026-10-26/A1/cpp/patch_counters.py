"""Patch a COPY of the certificate sources with operation counters and exact end-of-stage dumps.

Only counting statements are inserted; no arithmetic is changed. Run with the copy's directory as argument.
"""
from __future__ import annotations

import sys
from pathlib import Path


COUNTERS = ("inline void counters(const std::string& stage){std::cerr<<\"COUNTS \"<<stage<<\" mul=\"<<C_MUL<<\" add=\"<<C_ADD<<\" inv=\"<<C_INV"
            "<<\" sqrt=\"<<C_SQRT<<\" log=\"<<C_LOG<<\" G=\"<<C_G<<\" Gfull=\"<<C_GF<<\" fh=\"<<C_FH<<\" lookup=\"<<C_LOOK<<std::endl;"
            "C_MUL=0;C_ADD=0;C_INV=0;C_SQRT=0;C_LOG=0;C_G=0;C_GF=0;C_FH=0;C_LOOK=0;}\n")


def sub(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"patch anchor not unique/found: {old[:60]!r} ({text.count(old)})")
    return text.replace(old, new)


def main(d: Path) -> None:
    core = (d / "core.hpp").read_text()
    core = sub(core, "#include <omp.h>\n", "#include <omp.h>\n#include <atomic>\n"
               "inline std::atomic<unsigned long long> C_MUL{0},C_ADD{0},C_INV{0},C_SQRT{0},C_LOG{0},C_G{0},C_GF{0},C_FH{0},C_LOOK{0};\n" + COUNTERS)
    core = sub(core, "co={zero};auto cc=cs(M);co.insert(co.end(),cc.begin(),cc.end());init_after_co();std::cerr<<\"building table\\n\";table(24000);",
               "counters(\"init_constants_again\");co={zero};auto cc=cs(M);counters(\"cs\");co.insert(co.end(),cc.begin(),cc.end());init_after_co();counters(\"init_after_co\");std::cerr<<\"building table\\n\";table(24000);counters(\"table\");")
    core = sub(core, 'std::cerr<<"core_test\\n";core_test();', 'counters("bcons_eps");std::cerr<<"core_test\\n";core_test();counters("core_test");')
    core = sub(core, "inline IV operator+(const IV&a,const IV&b){return IV(a.u+b.u,a.v+b.v);}",
               "inline IV operator+(const IV&a,const IV&b){C_ADD.fetch_add(1,std::memory_order_relaxed);return IV(a.u+b.u,a.v+b.v);}")
    core = sub(core, "inline IV operator*(const IV&a,const IV&b){\n",
               "inline IV operator*(const IV&a,const IV&b){\n C_MUL.fetch_add(1,std::memory_order_relaxed);\n")
    core = sub(core, " IV inv()const{\n", " IV inv()const{\n  C_INV.fetch_add(1,std::memory_order_relaxed);\n")
    core = sub(core, " IV sqrt()const{if(u<=0)", " IV sqrt()const{C_SQRT.fetch_add(1,std::memory_order_relaxed);if(u<=0)")
    core = sub(core, "inline IV IV::log()const{\n", "inline IV IV::log()const{\n C_LOG.fetch_add(1,std::memory_order_relaxed);\n")
    core = sub(core, "inline std::vector<IV> fh(const J&t,int seg,const SState*S=nullptr){\n",
               "inline std::vector<IV> fh(const J&t,int seg,const SState*S=nullptr){\n C_FH.fetch_add(1,std::memory_order_relaxed);\n")
    core = sub(core, "inline std::vector<IV>lookup(const IV&T,bool full=false){\n",
               "inline std::vector<IV>lookup(const IV&T,bool full=false){\n C_LOOK.fetch_add(1,std::memory_order_relaxed);\n")
    (d / "core.hpp").write_text(core)

    g = (d / "grids.hpp").read_text()
    g = sub(g, "inline IV G(const IV& d, const IV& s) {\n", "inline IV G(const IV& d, const IV& s) {\n    C_G.fetch_add(1,std::memory_order_relaxed);\n")
    g = sub(g, "inline std::array<IV,5> G(const IV& d, const IV& s, bool full) {\n",
            "inline std::array<IV,5> G(const IV& d, const IV& s, bool full) {\n    C_GF.fetch_add(1,std::memory_order_relaxed);\n")
    g = sub(g, "struct CertificateTimer {",
            "inline void exact(const std::string& n,const IV& x){std::cerr<<\"EXACT \"<<n<<' '<<x.u<<' '<<x.v<<std::endl;}\n"
            "struct CertificateTimer {")
    g = sub(g, "    assert((gmin-factor).u>0 && (drneg+er_drop+K).v<0);\n",
            "    exact(\"gmin\",gmin);exact(\"drneg\",drneg);exact(\"factor\",factor);exact(\"er_drop\",er_drop);"
            "exact(\"gmin_minus_factor\",gmin-factor);exact(\"neg_lhs\",drneg+er_drop+K);\n"
            "    assert((gmin-factor).u>0 && (drneg+er_drop+K).v<0);\n")
    g = sub(g, "    std::cout << \"hess hulls\" << std::endl;\n",
            "    exact(\"g_dd\",dgl);exact(\"g_dx\",glx);exact(\"g_xx\",glxx);exact(\"det\",min_det);\n"
            "    std::cout << \"hess hulls\" << std::endl;\n")
    # stage counters
    g = sub(g, "{ CertificateTimer timer(\"init_core including core_test\"); init_core(); }",
            "{ CertificateTimer timer(\"init_core including core_test\"); init_constants(); counters(\"init_constants\"); init_core(); counters(\"init_core_rest\"); }")
    g = sub(g, "{ CertificateTimer timer(\"calcLam\"); calcLam(); }", "{ CertificateTimer timer(\"calcLam\"); calcLam(); } counters(\"calcLam\");")
    g = sub(g, "{ CertificateTimer timer(\"calcK\"); calcK(); }", "{ CertificateTimer timer(\"calcK\"); calcK(); } counters(\"calcK\");")
    g = sub(g, "{ CertificateTimer timer(\"bdsup\"); bs=bdsup(); }", "{ CertificateTimer timer(\"bdsup\"); bs=bdsup(); } counters(\"bdsup\");")
    g = sub(g, "{ CertificateTimer timer(\"global_grid\"); global_grid(\".00019\",\".00018\",bs); }",
            "{ CertificateTimer timer(\"global_grid\"); global_grid(\".00019\",\".00018\",bs); } counters(\"global_grid\");")
    g = sub(g, "{ CertificateTimer timer(\"inside_hess\"); inside_hess(\".00004\",\".00008\"); }",
            "{ CertificateTimer timer(\"inside_hess\"); inside_hess(\".00004\",\".00008\"); } counters(\"inside_hess\");")
    (d / "grids.hpp").write_text(g)
    print("patched", d)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
