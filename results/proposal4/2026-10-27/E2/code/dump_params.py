"""Dump the Chen2020 parameters used (from the shipped PyBaMM set) to JSON."""
import json
import sys

import pybamm

p = pybamm.ParameterValues("Chen2020")
keys = [
    "Negative particle diffusivity [m2.s-1]",
    "Negative particle radius [m]",
    "Maximum concentration in negative electrode [mol.m-3]",
    "Negative electrode thickness [m]",
    "Negative electrode active material volume fraction",
    "Electrode height [m]",
    "Electrode width [m]",
    "Nominal cell capacity [A.h]",
    "Initial concentration in negative electrode [mol.m-3]",
]
out = {"pybamm_version": pybamm.__version__, "set": "Chen2020"}
for k in keys:
    try:
        out[k] = repr(float(p[k]))
    except KeyError:
        out[k] = None
        sys.stderr.write("missing " + k + "\n")
from scipy import constants

out["Faraday constant [C.mol-1] (scipy.constants, as used by pybamm.constants.F)"] = repr(
    float(constants.physical_constants["Faraday constant"][0])
)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
