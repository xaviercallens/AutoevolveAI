"""Build LeanFlow lean.certify claims (interval endpoints -> linear Int statements checked by the Lean kernel) from
the B2 ball-arithmetic runs.

usage: python -I b2_leanflow_claims.py RUN.json OUT_CLAIM.json NAME

The product pert.hi = trW.hi * esum.hi is formed exactly with Python Fractions (LeanFlow assertions are linear in the
endpoints); the same product is re-checked by the Lean kernel in ProgZeroPointCert.cert_B_neg, which multiplies the
two rationals itself.
"""

import json
import sys
from fractions import Fraction


def main() -> None:
    run = json.load(open(sys.argv[1]))
    out, name = sys.argv[2], sys.argv[3]
    cr = run["cert_rationals"]
    up_hi, up_lo = Fraction(cr["Upp0_hi"]), Fraction(cr["Upp0_lo"])
    trw_hi, esum_hi = Fraction(cr["trW_hi"]), Fraction(cr["esum_hi"])
    pert_hi = trw_hi * esum_hi
    claim = {
        "name": name,
        "tactic": "decide",
        "enclosures": {
            "Upp0": [str(up_lo), str(up_hi)],
            "pert": ["0", str(pert_hi)],
        },
        "assertions": [
            {"label": "certified window bound B = Upp0.hi + trW.hi*esum.hi < 0",
             "terms": [["1", "Upp0.hi"], ["1", "pert.hi"]], "op": "<", "rhs": "0"},
        ],
    }
    if cr.get("lmin_lo") is not None:
        claim["enclosures"]["lmin"] = [cr["lmin_lo"], cr["lmin_lo"]]
        claim["enclosures"]["dB"] = ["0", cr["dB_hi"]]
        claim["assertions"].append({"label": "stability margin lmin.lo - dB.hi > 0",
                                    "terms": [["1", "lmin.lo"], ["-1", "dB.hi"]], "op": ">", "rhs": "0"})
    json.dump(claim, open(out, "w"), indent=1)
    print(json.dumps(claim, indent=1))


if __name__ == "__main__":
    main()
