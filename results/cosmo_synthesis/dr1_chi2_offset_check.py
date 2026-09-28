"""Round-1 referee item (stats, major 2): our DR1 chi2 minimum is 12.74 while
DESI 2024 VI Sec. 3.2 quotes chi2 = 12.66 for 10 dof on the same data vector.

This script tests candidate explanations by refitting DR1 (chi2 minimum over
Omega_m and h r_d, same public mean/cov files) with four background models:
  M0  primary model of the DR1 run (flat LCDM, no radiation)      [dr2_model.predict_quad]
  M1  M0 plus photon+massless-neutrino radiation (astropy Omega_r) [dr2_model.predict_quad]
  M2  CAMB background, all neutrinos massless (N_eff 3.044)
  M3  CAMB background, one 0.06 eV massive neutrino (DESI baseline)
For M2/M3 h is fixed at 0.6851 and omega_b at 0.02218 (BBN mean); Omega_m includes
the massive neutrino. Writes results/cosmo_synthesis/dr1_chi2_offset_check.json.
Run with /mnt/disks/disk-socrateai-local-1/venv-cosmo/bin/python.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Callable

import camb
import numpy as np
from scipy.optimize import minimize, minimize_scalar

WT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(WT / "scripts/desi_dr2_bao"))
import dr2_model as m  # noqa: E402

OUT = WT / "results/cosmo_synthesis/dr1_chi2_offset_check.json"
H = 0.6851
OMBH2 = 0.02218
NNU = 3.044


def fit_analytic(ds: m.Dataset, orad: float) -> dict[str, float]:
    def f(x: np.ndarray) -> float:
        return float(m.chi2_vals(ds, m.predict_quad(ds, float(x[0]), float(x[1]), -1.0, orad)))
    r = minimize(f, x0=np.array([0.294, 101.9]), method="Nelder-Mead",
                 options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 5000})
    return {"Om": float(r.x[0]), "hrd": float(r.x[1]), "chi2": float(r.fun)}


def camb_vec_factory(ds: m.Dataset, mnu: float) -> Callable[[float], tuple[np.ndarray, np.ndarray, float]]:
    def vec(om: float) -> tuple[np.ndarray, np.ndarray, float]:
        pars = camb.CAMBparams()
        omnuh2 = mnu / 93.14 if mnu > 0 else 0.0
        omch2 = om * H * H - OMBH2 - omnuh2
        if mnu > 0:
            pars.set_cosmology(H0=100 * H, ombh2=OMBH2, omch2=omch2, mnu=mnu, num_massive_neutrinos=1, nnu=NNU, omk=0.0)
        else:
            pars.set_cosmology(H0=100 * H, ombh2=OMBH2, omch2=omch2, mnu=0.0, num_massive_neutrinos=0, nnu=NNU, omk=0.0)
        res = camb.get_background(pars)
        dm100 = np.array([res.comoving_radial_distance(float(z)) for z in ds.z]) * H
        e = np.array([res.hubble_parameter(float(z)) for z in ds.z]) / (100.0 * H)
        om_true = float(res.get_Omega("cdm") + res.get_Omega("baryon") + res.get_Omega("nu"))
        return dm100, e, om_true
    return vec


def fit_camb(ds: m.Dataset, mnu: float) -> dict[str, float]:
    vec = camb_vec_factory(ds, mnu)

    def inner(om: float) -> tuple[float, float, float]:
        dm100, e, om_true = vec(om)
        r = minimize_scalar(lambda hrd: float(m.chi2_vals(ds, m._assemble(ds.z, ds.kinds, dm100, e, hrd))),
                            bounds=(90.0, 115.0), method="bounded", options={"xatol": 1e-7})
        return float(r.fun), float(r.x), om_true

    r = minimize_scalar(lambda om: inner(om)[0], bounds=(0.25, 0.34), method="bounded", options={"xatol": 1e-7})
    chi2, hrd, om_true = inner(float(r.x))
    return {"Om_input": float(r.x), "Om_total_incl_nu": om_true, "hrd": hrd, "chi2": chi2}


def main() -> None:
    ds = m.load_dr1()
    orad = float(m.omega_rad_from_astropy())
    out = {
        "script": "results/cosmo_synthesis/dr1_chi2_offset_check.py",
        "date": datetime.date.today().isoformat(),
        "camb_version": camb.__version__,
        "data_mean_sha256": m.sha256(m.DR1_MEAN), "data_cov_sha256": m.sha256(m.DR1_COV),
        "desi_published": {"source": "arXiv:2404.03002 Sec. 3.2 and Fig. 1 caption (fetched via alphaXiv)",
                           "chi2": 12.66, "dof": 10, "Om_bestfit": 0.294, "H0rd_km_s": 1.0194e4},
        "fixed": {"h": H, "omega_b": OMBH2, "N_eff": NNU, "Omega_r_astropy": orad},
        "M0_no_radiation": fit_analytic(ds, 0.0),
        "M1_radiation": fit_analytic(ds, orad),
        "M2_camb_massless_nu": fit_camb(ds, 0.0),
        "M3_camb_mnu0.06": fit_camb(ds, 0.06),
    }
    for k in ("M0_no_radiation", "M1_radiation", "M2_camb_massless_nu", "M3_camb_mnu0.06"):
        out[k]["chi2_minus_desi"] = out[k]["chi2"] - 12.66
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
