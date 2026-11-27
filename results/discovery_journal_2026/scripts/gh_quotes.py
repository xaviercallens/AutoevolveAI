import json, re
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
E = json.load(open(B + "enriched.json"))
for n in ["SocrateAI-Scientific-Agora-LeanMaster", "SocrateAI-Scientific-Agora-K3-DarkMatter", "SocrateAI-Scientific-AlienMathematics-Foundation",
          "Mirror-Map-Sieve", "SocrateAI-Scientific-QuantumFluids", "AutoevolveAI", "HiveMind", "SocrateAI-Scientific-Communication",
          "SocrateAI-Scientific-SectorCausalityTheory", "SocrateAI-Scientific-Elenchus", "SocrateAI-Scientific-Agora-LeanFlow",
          "SocrateAI-Scientific-Agora-RamanujanNeuroSymbolic", "rusty-SUNDIALS", "OptimalEnergyAI", "TIC4206066-Exoplanet-Verification"]:
    rd = E[n]["readme_head"] or ""
    print("##", n)
    # quote blocks
    q = [l.strip()[:300] for l in rd.splitlines() if l.strip().startswith(">")]
    print("\n".join(q[:9]))
    ms = [l.strip()[:260] for l in rd.splitlines() if re.search(r"(retract|not claim|honest|lesson|caveat|null result|refut|no signal|failed)", l, re.I)]
    print("  KEY:", " || ".join(ms[:5]))
