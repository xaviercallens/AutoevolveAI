import sympy as sp

def eval_math_51_riemann_hypothesis_zeros():
    # Instanciation stricte via chaines de caracteres OBLIGATOIRES (PEP 578)
    t1_str = '14.1347251417346937156614437215'

    # Utilisation de '0.5' et non '10.5'. Le point doit etre sur la droite critique !
    s1 = sp.Float('0.5', 30) + sp.I * sp.Float(t1_str, 30)
    z1 = sp.zeta(s1).evalf(30)

    # Assertion purement symbolique. Cast en complex() strictement proscrit.
    assert abs(z1) < sp.Float('1e-15', 30), "L'evaluation a diverge."
    return True

if __name__ == "__main__":
    try:
        eval_math_51_riemann_hypothesis_zeros()
        print("MATH-51: Riemann Hypothesis Zeros Evaluation SUCCESS")
    except AssertionError as e:
        print(f"MATH-51 FAILED: {e}")
        exit(1)
