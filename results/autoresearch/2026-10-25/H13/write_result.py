"""Assemble H13 result.json from the real compile logs (no hand-typed axiom output)."""
import json

D = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/autoresearch/2026-10-25/H13/"


def main() -> None:
    ax = open(D + "compile_clean.log").read()
    ctl = open(D + "compile_controls.log").read()
    ns = "StringTheory.Foundation.StringTheory.TadpoleCancellation.Autoresearch."
    names = ["d7_count_unique", "tadpole_pair_unique", "tadpole_unique_given_geometry", "tadpole_pair_exists",
             "local_distribution_unique", "local_implies_global", "ctl_neg_no_d3", "ctl_neg_no_sevenbrane",
             "ctl_neg_global_only"]
    r = {
        "id": "H13",
        "verdict": "KEEP",
        "attempts": [
            {"n": 1, "minutes": 44, "status": "DISCARD",
             "error_class": "infra_io_starvation_timeout: lake env hung at 0% CPU; direct lean timed out after 900 s "
                            "using 0.4 s CPU (D-state page faults on disk 2; gcloud rsync of /mnt/disks/.../leanmaster "
                            "plus 2 sibling lean jobs, load ~110). Never elaborated."},
            {"n": 2, "minutes": 5, "status": "KEEP", "error_class": None, "compiles": 3,
             "note": "compile 1: decide on user def Props (failed to synthesize Decidable) and decide on a goal with a "
                     "free variable; fixed with unfold/show. compile 2: rc 0. compile 3: docstring-only, rc 0. "
                     "Page cache warmed first (580 MB)."},
        ],
        "statement_chosen": (
            "U1 d7_count_unique: n*1 + 4*(-4) = 0 <-> n = 16. U2 tadpole_pair_unique (main): for a,b:Nat (#O7-, #D7), "
            "seven-brane tadpole -4a+b=0 AND induced-D3-charge matching 2a+b = chi(K3xK3)/24 = 24 <-> (a,b)=(4,16) "
            "(not the D3 tadpole N_D3+N_flux/2=24; a=4 is geometric, agreement is a consistency check). "
            "U3 local_distribution_unique: f:Fin 4->Nat locally cancelled at every O7 <-> f = const 4. "
            "All over the library constants of TadpoleCancellation.lean (imported, unchanged)."),
        "theorems": [ns + n for n in names],
        "axioms_output": ax,
        "controls_output": ctl,
        "controls_caught": {
            "ctl_sorry": "'ctl_sorry' depends on axioms: [sorryAx]" in ctl,
            "ctl_axiom": "'ctl_axiom' depends on axioms: [ctl_planted_axiom]" in ctl,
            "neg_drop_D3_condition": "(1,4),(4,16) both solve the seven-brane tadpole (kernel-checked)",
            "neg_drop_sevenbrane_condition": "(0,24),(4,16) both meet the induced-D3 equation (kernel-checked)",
            "neg_global_only": "(16,0,0,0),(4,4,4,4) both globally cancelled (kernel-checked)",
        },
        "grep_clean_file": "no sorry/admit/native_decide/axiom in Autoresearch_Tadpole.lean "
                           "(controls only in Autoresearch_Tadpole_controls.lean)",
        "toolchain": "lean v4.34.0-rc2 run directly with LEAN_PATH=<LeanMaster>/.lake/build/lib/lean (lake env hung); "
                     "TadpoleCancellation.olean newer than its source",
        "files": [D + "Autoresearch_Tadpole.lean", D + "Autoresearch_Tadpole_controls.lean"],
        "tier": "KEEP (producer); Tier A pending independent recompile + statement audit",
        "impact": "low",
    }
    json.dump(r, open(D + "result.json", "w"), indent=1)
    print(r["controls_caught"]["ctl_sorry"], r["controls_caught"]["ctl_axiom"])


if __name__ == "__main__":
    main()
