/-
  ANSE.Performance — Formal specification of Computational Physics & Performance Energy
  Use Case 1: The Algorithmic Performance Engineer

  Formal Foundations:
  - Energy Signal: E(y, x) = w_t * T(y, x) + w_m * M(y, x) if Correct(y, x) else E_fail
  - Monotonicity: Reductions in execution time or peak memory strictly reduce energy.
  - Correctness Supremacy: Any crashing or semantically broken code is strictly worse
    than any valid execution whose resource cost is bounded by E_fail.
  - Vectorization Theorem: Formalizes the complexity transition from scalar loops (O(N^2))
    to SIMD vectorized operations (O(N)), proving a strict positive energy delta.
-/
import ANSE.Basic

set_option linter.style.header false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace ANSE.Performance

/-- Computational execution physical observables:
    execution time (ms) and peak resident memory (MB). -/
structure ComputationalMetrics where
  time_ms     : ℝ
  peak_ram_mb : ℝ
  time_nonneg : 0 ≤ time_ms
  ram_nonneg  : 0 ≤ peak_ram_mb

/-- Performance energy configuration: positive weights for time and RAM,
    and a large failure penalty representing the ∞ energy barrier. -/
structure PerformanceWeights where
  w_time        : ℝ
  w_ram         : ℝ
  w_time_pos    : 0 < w_time
  w_ram_pos     : 0 < w_ram
  penalty_fail  : ℝ
  penalty_large : ∀ m : ComputationalMetrics,
    w_time * m.time_ms + w_ram * m.peak_ram_mb < penalty_fail

/-- Valid algorithmic execution vs. crash/incorrect output. -/
inductive ExecutionStatus (α : Type*) where
  | success : ComputationalMetrics → ExecutionStatus α
  | failure : ExecutionStatus α

/-- Raw computational energy: E = w_t * T + w_m * M -/
def physicalEnergy (w : PerformanceWeights) (m : ComputationalMetrics) : ℝ :=
  w.w_time * m.time_ms + w.w_ram * m.peak_ram_mb

/-- Total performance energy lifted to include failure penalty. -/
def performanceEnergy (w : PerformanceWeights) (s : ExecutionStatus Unit) : ℝ :=
  match s with
  | ExecutionStatus.success m => physicalEnergy w m
  | ExecutionStatus.failure   => w.penalty_fail

/-!
### Theorems of Computational Physics
-/

/-- Theorem P1: Physical energy is non-negative. -/
theorem physicalEnergy_nonneg (w : PerformanceWeights) (m : ComputationalMetrics) :
    0 ≤ physicalEnergy w m := by
  dsimp [physicalEnergy]
  have ht : 0 ≤ w.w_time * m.time_ms :=
    mul_nonneg (le_of_lt w.w_time_pos) m.time_nonneg
  have hr : 0 ≤ w.w_ram * m.peak_ram_mb :=
    mul_nonneg (le_of_lt w.w_ram_pos) m.ram_nonneg
  exact add_nonneg ht hr

/-- Theorem P2 (Correctness Supremacy):
    Any failing or semantically incorrect code receives higher energy
    than any valid execution whose resource usage is within physical limits. -/
theorem correctness_supremacy
    (w : PerformanceWeights) (m : ComputationalMetrics) :
    performanceEnergy w (ExecutionStatus.success m) <
    performanceEnergy w ExecutionStatus.failure := by
  dsimp [performanceEnergy]
  exact w.penalty_large m

/-- Theorem P3 (Strict Monotonicity of Speedup):
    If candidate y₂ is strictly faster than y₁ and uses no more memory,
    then its computational energy is strictly lower: E(y₂) < E(y₁). -/
theorem energy_monotonicity_speedup
    (w : PerformanceWeights)
    (m1 m2 : ComputationalMetrics)
    (h_time : m2.time_ms < m1.time_ms)
    (h_ram  : m2.peak_ram_mb ≤ m1.peak_ram_mb) :
    physicalEnergy w m2 < physicalEnergy w m1 := by
  dsimp [physicalEnergy]
  have ht : w.w_time * m2.time_ms < w.w_time * m1.time_ms :=
    mul_lt_mul_of_pos_left h_time w.w_time_pos
  have hr : w.w_ram * m2.peak_ram_mb ≤ w.w_ram * m1.peak_ram_mb :=
    mul_le_mul_of_nonneg_left h_ram (le_of_lt w.w_ram_pos)
  exact add_lt_add_of_lt_of_le ht hr

/-- Theorem P4 (Strict Monotonicity of Memory Reduction):
    If candidate y₂ uses strictly less memory and takes no more time,
    then its computational energy is strictly lower. -/
theorem energy_monotonicity_memory
    (w : PerformanceWeights)
    (m1 m2 : ComputationalMetrics)
    (h_time : m2.time_ms ≤ m1.time_ms)
    (h_ram  : m2.peak_ram_mb < m1.peak_ram_mb) :
    physicalEnergy w m2 < physicalEnergy w m1 := by
  dsimp [physicalEnergy]
  have ht : w.w_time * m2.time_ms ≤ w.w_time * m1.time_ms :=
    mul_le_mul_of_nonneg_left h_time (le_of_lt w.w_time_pos)
  have hr : w.w_ram * m2.peak_ram_mb < w.w_ram * m1.peak_ram_mb :=
    mul_lt_mul_of_pos_left h_ram w.w_ram_pos
  exact add_lt_add_of_le_of_lt ht hr

/-- Asymptotic Vectorization Model:
    Scalar loop execution scales quadratically: T_loop(N) = c_loop * N^2.
    Vectorized execution scales linearly: T_vec(N) = c_vec * N.
    Both constants are strictly positive. -/
structure ComplexityModel where
  c_loop      : ℝ
  c_vec       : ℝ
  ram_loop    : ℝ
  ram_vec     : ℝ
  c_loop_pos  : 0 < c_loop
  c_vec_pos   : 0 < c_vec
  ram_loop_nn : 0 ≤ ram_loop
  ram_vec_nn  : 0 ≤ ram_vec
  ram_le      : ram_vec ≤ ram_loop

/-- Theorem P5 (Vectorization Energy Reduction):
    For any scale N > c_vec / c_loop, the vectorized implementation achieves
    a strictly lower computational energy than the scalar loop. -/
theorem vectorization_energy_reduction
    (w : PerformanceWeights)
    (model : ComplexityModel)
    (N : ℝ)
    (hN_pos : 0 < N)
    (hN : model.c_vec / model.c_loop < N) :
    let m_loop : ComputationalMetrics := {
      time_ms := model.c_loop * (N ^ 2),
      peak_ram_mb := model.ram_loop,
      time_nonneg := mul_nonneg (le_of_lt model.c_loop_pos) (sq_nonneg N),
      ram_nonneg := model.ram_loop_nn
    }
    let m_vec : ComputationalMetrics := {
      time_ms := model.c_vec * N,
      peak_ram_mb := model.ram_vec,
      time_nonneg := mul_nonneg (le_of_lt model.c_vec_pos) (le_of_lt hN_pos),
      ram_nonneg := model.ram_vec_nn
    }
    physicalEnergy w m_vec < physicalEnergy w m_loop := by
  intro m_loop m_vec
  dsimp [physicalEnergy, m_loop, m_vec]
  have h_time : model.c_vec * N < model.c_loop * (N ^ 2) := by
    have h1 : model.c_vec < model.c_loop * N := by
      have := (div_lt_iff₀ model.c_loop_pos).mp hN
      linarith
    calc model.c_vec * N < (model.c_loop * N) * N := mul_lt_mul_of_pos_right h1 hN_pos
    _ = model.c_loop * (N ^ 2) := by ring
  have ht : w.w_time * (model.c_vec * N) < w.w_time * (model.c_loop * (N ^ 2)) :=
    mul_lt_mul_of_pos_left h_time w.w_time_pos
  have hr : w.w_ram * model.ram_vec ≤ w.w_ram * model.ram_loop :=
    mul_le_mul_of_nonneg_left model.ram_le (le_of_lt w.w_ram_pos)
  exact add_lt_add_of_lt_of_le ht hr

/-- Theorem P6 (Hash Lookup Energy Reduction):
    Formalizes the transition from quadratic search O(N^2) to linear hash lookup O(N).
    For any scale N > c_hash / c_linear, hash lookup achieves strictly lower energy. -/
theorem hash_lookup_energy_reduction
    (w : PerformanceWeights)
    (c_linear c_hash ram_linear ram_hash : ℝ)
    (h_linear_pos : 0 < c_linear)
    (h_hash_pos : 0 < c_hash)
    (h_ram_linear : 0 ≤ ram_linear)
    (h_ram_hash : 0 ≤ ram_hash)
    (h_ram_le : ram_hash ≤ ram_linear)
    (N : ℝ)
    (hN_pos : 0 < N)
    (hN : c_hash / c_linear < N) :
    let m_linear : ComputationalMetrics := {
      time_ms := c_linear * (N ^ 2),
      peak_ram_mb := ram_linear,
      time_nonneg := mul_nonneg (le_of_lt h_linear_pos) (sq_nonneg N),
      ram_nonneg := h_ram_linear
    }
    let m_hash : ComputationalMetrics := {
      time_ms := c_hash * N,
      peak_ram_mb := ram_hash,
      time_nonneg := mul_nonneg (le_of_lt h_hash_pos) (le_of_lt hN_pos),
      ram_nonneg := h_ram_hash
    }
    physicalEnergy w m_hash < physicalEnergy w m_linear := by
  intro m_linear m_hash
  dsimp [physicalEnergy, m_linear, m_hash]
  have h_time : c_hash * N < c_linear * (N ^ 2) := by
    have h1 : c_hash < c_linear * N := by
      have := (div_lt_iff₀ h_linear_pos).mp hN
      linarith
    calc c_hash * N < (c_linear * N) * N := mul_lt_mul_of_pos_right h1 hN_pos
    _ = c_linear * (N ^ 2) := by ring
  have ht : w.w_time * (c_hash * N) < w.w_time * (c_linear * (N ^ 2)) :=
    mul_lt_mul_of_pos_left h_time w.w_time_pos
  have hr : w.w_ram * ram_hash ≤ w.w_ram * ram_linear :=
    mul_le_mul_of_nonneg_left h_ram_le (le_of_lt w.w_ram_pos)
  exact add_lt_add_of_lt_of_le ht hr

/-- Theorem P7 (Catastrophic Backtracking Timeout Avoidance):
    A backtracking parser that times out triggers ExecutionStatus.failure with E = penalty_fail (10^6).
    Any deterministic linear parser that finishes within physical bounds achieves
    status ExecutionStatus.success with strictly lower energy. -/
theorem catastrophic_backtracking_timeout_avoidance
    (w : PerformanceWeights)
    (m_det : ComputationalMetrics) :
    performanceEnergy w (ExecutionStatus.success m_det) <
    performanceEnergy w (ExecutionStatus.failure (α := Unit)) := by
  dsimp [performanceEnergy]
  exact w.penalty_large m_det

end ANSE.Performance
