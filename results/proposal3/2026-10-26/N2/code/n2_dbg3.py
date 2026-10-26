"""N2 debugging aid: arb behaviour on wide balls (Tier X)."""
import sys
sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/.scratchpad/b2_pylib")
from flint import arb  # noqa: E402
x = arb(10, 3)
print(x, x.sin(), x.cos(), x * x.sin(), x * x * x, 1 - x.cos())
