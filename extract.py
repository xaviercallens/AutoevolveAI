with open("anse/autopoiesis/hypervisor.py") as f:
    lines = f.readlines()

out = []
# Imports needed for trusted_driver
out.append("from __future__ import annotations\n")
out.append("import json\n")
out.append("from typing import Any\n")
out.append("from anse.symbolic.sandbox import ExecutionResult\n\n")

# Copy lines 67 to 328 (0-indexed 67:328)
out.extend(lines[67:328])

with open("anse/symbolic/trusted_driver.py", "w") as f:
    f.writelines(out)

# Now modify hypervisor to import them
hypervisor_lines = (
    lines[:67]
    + [
        "from anse.symbolic.trusted_driver import (\n",
        "    RESULT_VARIABLE,\n",
        "    _DRIVER_BUDGET_FRACTION,\n",
        "    build_driver,\n",
        "    trusted_payload,\n",
        ")\n\n",
    ]
    + lines[328:]
)

with open("anse/autopoiesis/hypervisor.py", "w") as f:
    f.writelines(hypervisor_lines)
