"""init for cover_ls_fast: evens 2..2N (N=n+1) at shift 0 minus runner(s) in argv[3:]; usage: n out rm..."""
import sys


def make(n: int, out: str, rm: set[int]) -> None:
    N = n + 1
    tl = sorted(x for x in rm if x <= 2 * N)
    v = [2 * j for j in range(1, N + 1) if 2 * j not in rm] + tl[:-1]  # fixed first, freed (|T|-1) last
    extra = [x for x in range(1, 4 * N) if x % 2 == 1]
    assert len(v) == n, (len(v), n)
    with open(out, "w") as fh:
        fh.write("".join(f"{x} 0.0\n" for x in v))


if __name__ == "__main__":
    make(int(sys.argv[1]), sys.argv[2], {int(x) for x in sys.argv[3:]})
