
import Mathlib.Algebra.Group.Basic

structure RationalEllipticCurve where
  algebraic_rank : ℕ
  analytic_order_at_one : ℕ

def bsd_conjecture (E : RationalEllipticCurve) : Prop :=
  E.algebraic_rank = E.analytic_order_at_one
