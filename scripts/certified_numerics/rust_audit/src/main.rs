//! Prints chi(z) = int_0^z dz/E(z) from rusty-SUNDIALS `qf-bao-distances` at the P1 fit point (Om = 0.29743,
//! radiation off) for several integrators, as JSON lines. The values are compared outside this program with the
//! kernel-checked enclosures in results/certified_numerics/P1_bao/bounds_*.json.

use qf_bao_distances::{FlatCosmology, Integrator, chi};

const ZS: [f64; 7] = [0.295, 0.51, 0.706, 0.934, 1.321, 1.484, 2.33];

fn emit(label: &str, om: f64, method: Integrator) {
    let cosmo = FlatCosmology::lcdm(om, 0.7);
    match chi(&cosmo, &ZS, method) {
        Ok(v) => {
            let vals: Vec<String> = v.iter().map(|x| format!("{x:.17e}")).collect();
            println!("{{\"label\": \"{label}\", \"Om\": {om}, \"chi\": [{}]}}", vals.join(", "));
        }
        Err(e) => println!("{{\"label\": \"{label}\", \"Om\": {om}, \"error\": \"{}\"}}", e.replace('"', "'")),
    }
}

fn main() {
    let om = 0.29743;
    emit("cvode_default", om, Integrator::CVODE);
    emit("quadrature_default", om, Integrator::QUADRATURE);
    emit("cvode_rtol1e-3", om, Integrator::Cvode { rtol: 1e-3, atol: 1e-6 });
    emit("cvode_rtol1e-2", om, Integrator::Cvode { rtol: 1e-2, atol: 1e-2 });
    emit("quadrature_default_Om101", om * 1.01, Integrator::QUADRATURE);
    emit("quadrature_default_EdS", 1.0, Integrator::QUADRATURE);
}
