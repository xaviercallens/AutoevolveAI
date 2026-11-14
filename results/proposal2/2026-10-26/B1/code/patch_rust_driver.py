"""One-off edit: register the scha module and add the `scha` subcommand to lattice_phonon (rusty-SUNDIALS-wt-p2)."""

ROOT = "/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2/crates/qf-yukawa-crystal/src/"

p = ROOT + "bin/lattice_phonon.rs"
s = open(p).read()
s = s.replace(
    "//! * `lattice_phonon curv a N h` prints `c = Lap E_zp(rho)/4` at the triangular point for `exp(-pi a r^2)`.\n",
    "//! * `lattice_phonon curv a N h` prints `c = Lap E_zp(rho)/4` at the triangular point for `exp(-pi a r^2)`.\n"
    "//! * `lattice_phonon scha a x y lam N` prints the T = 0 self-consistent-harmonic energy of `exp(-pi a r^2)` and the\n"
    "//!   harmonic `E_static + lam E_zp` on the same zone rule.\n",
    1,
)
s = s.replace(
    "use qf_yukawa_crystal::phonon_spectral::{GaussPoisson, curvature_at_rho_gauss, ezp_gauss_duffy};\n",
    "use qf_yukawa_crystal::phonon_spectral::{GaussPoisson, curvature_at_rho_gauss, ezp_gauss_duffy};\n"
    "use qf_yukawa_crystal::scha::{harmonic_energy, scha_solve};\n",
    1,
)
old = '        other => return Err(format!("unknown command {other}")),'
new = '''        "scha" => {
            // T = 0 self-consistent harmonic approximation for the Gaussian exp(-pi a r^2)
            let (a, x, y, lam) = (f(2)?, f(3)?, f(4)?, f(5)?);
            let n = arg(6)?.parse::<usize>().map_err(|e| e.to_string())?;
            let r = scha_solve(a, x, y, lam, n, 1e-14, 2000);
            println!(
                "{{\\"a\\":{a},\\"x\\":{x},\\"y\\":{y},\\"lam\\":{lam},\\"n\\":{n},\\"e_scha\\":{:.15e},\\"kinetic\\":{:.15e},\\"u2\\":{:.15e},\\"iterations\\":{},\\"converged\\":{},\\"min_ratio\\":{:.9e},\\"e_harmonic\\":{:.15e}}}",
                r.energy,
                r.kinetic,
                r.u2,
                r.iterations,
                r.converged,
                r.min_ratio,
                harmonic_energy(a, x, y, lam, n)
            );
        }
''' + old
assert old in s and "scha_solve" not in s.split("use qf_yukawa_crystal::scha")[0][-10:]
s = s.replace(old, new, 1)
open(p, "w").write(s)
p = ROOT + "lib.rs"
s = open(p).read()
if "pub mod scha;" not in s:
    s = s.replace("pub mod phonon_spectral;\n", "pub mod phonon_spectral;\npub mod scha;\n", 1)
open(p, "w").write(s)
print("ok")
