/-
  ANSE.Sandbox — Formal specification of the sandboxed code execution model.

  Sources:
    · anse/symbolic/sandbox.py — SandboxExecutor, SandboxConfig
    · docs/specs/HARDENING_AND_GPU_POD.md — WP2 (Fail-closed sandbox)
    · ANSE Agent Rules — E = 10^6 on crash (Maximum Pain)

  This module formalizes:
    1. Sandbox isolation tiers (process vs container)
    2. Fail-closed policy (deny vs allow_with_warning)
    3. Code trust classification (trusted vs untrusted)
    4. Energy assignment on execution outcomes
    5. Container security constraints
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith

-- Disable Mathlib contribution-style linters
set_option linter.style.header false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace ANSE.Sandbox

-- ============================================================
-- §1  Sandbox Isolation Tiers
-- ============================================================

/-- Execution isolation tier. -/
inductive IsolationTier
  | process    -- Tier 1: separate process, no container
  | container  -- Tier 2: Docker container with security constraints
  deriving Repr, DecidableEq

/-- Sandbox fallback policy when Docker is unavailable. -/
inductive FallbackPolicy
  | deny             -- fail-closed: reject untrusted code
  | allowWithWarning -- allow Tier 1 with a warning log
  deriving Repr, DecidableEq

/-- Code trust classification. -/
inductive TrustLevel
  | trusted    -- repository-authored code (references, registry payloads)
  | untrusted  -- model-generated code
  deriving Repr, DecidableEq


-- ============================================================
-- §2  Sandbox Configuration
-- ============================================================

/-- The sandbox configuration. -/
structure SandboxConfig where
  fallbackPolicy : FallbackPolicy
  dockerAvailable : Bool
  timeoutSeconds : ℕ
  memoryLimitMB : ℕ
  hTimeout : 0 < timeoutSeconds
  hMemory : 0 < memoryLimitMB


-- ============================================================
-- §3  Execution Outcomes
-- ============================================================

/-- Execution result from the sandbox. -/
inductive ExecutionOutcome
  | success (stdout : String) (isolation : IsolationTier)
  | failure (stderr : String) (returncode : Int) (isolation : IsolationTier)
  | sandboxUnavailable  -- Docker not available, policy=deny
  | timeout             -- execution exceeded time limit
  | memoryExceeded      -- execution exceeded memory limit
  deriving Repr

/-- Whether an execution outcome is a successful run. -/
def ExecutionOutcome.isSuccess : ExecutionOutcome → Bool
  | .success _ _ => true
  | _ => false

/-- The isolation tier of a successful execution. -/
def ExecutionOutcome.tier : ExecutionOutcome → Option IsolationTier
  | .success _ t => some t
  | .failure _ _ t => some t
  | _ => none


-- ============================================================
-- §4  Sandbox Routing Rules
-- ============================================================

/-- Determine the isolation tier for a given trust level and config. -/
def routeExecution (trust : TrustLevel) (config : SandboxConfig) : ExecutionOutcome :=
  match trust with
  | .trusted => ExecutionOutcome.success "" .process  -- trusted code always uses Tier 1
  | .untrusted =>
    if config.dockerAvailable then
      ExecutionOutcome.success "" .container  -- untrusted uses Tier 2
    else
      match config.fallbackPolicy with
      | .deny => ExecutionOutcome.sandboxUnavailable
      | .allowWithWarning => ExecutionOutcome.success "" .process

/-- **Trusted code always executes in Tier 1**. -/
theorem trusted_always_tier1 (config : SandboxConfig) :
    routeExecution .trusted config = ExecutionOutcome.success "" .process := rfl

/-- **Fail-closed: deny policy blocks untrusted code when Docker is absent**. -/
theorem fail_closed_deny (config : SandboxConfig)
    (hNoDocker : config.dockerAvailable = false)
    (hDeny : config.fallbackPolicy = FallbackPolicy.deny) :
    routeExecution .untrusted config = ExecutionOutcome.sandboxUnavailable := by
  simp [routeExecution, hNoDocker, hDeny]

/-- **Untrusted code uses container when Docker is available**. -/
theorem untrusted_uses_container (config : SandboxConfig)
    (hDocker : config.dockerAvailable = true) :
    routeExecution .untrusted config = ExecutionOutcome.success "" .container := by
  simp [routeExecution, hDocker]


-- ============================================================
-- §5  Energy Assignment on Execution Outcomes
-- ============================================================

/-- Energy assignment rules for the sandbox. -/
noncomputable def executionEnergy : ExecutionOutcome → ℝ
  | .success _ _ => 0            -- clean execution → zero energy
  | .failure _ _ _ => 50         -- test failure → moderate energy
  | .sandboxUnavailable => 1000000  -- sandbox unavailable → Maximum Pain
  | .timeout => 1000000          -- timeout → Maximum Pain
  | .memoryExceeded => 1000000   -- OOM → Maximum Pain

/-- **Success yields zero energy**. -/
theorem success_zero_energy (s : String) (t : IsolationTier) :
    executionEnergy (.success s t) = 0 := rfl

/-- **Crash yields maximum energy (10^6)**. -/
theorem timeout_max_energy :
    executionEnergy .timeout = 1000000 := rfl

theorem sandbox_unavailable_max_energy :
    executionEnergy .sandboxUnavailable = 1000000 := rfl

theorem memory_exceeded_max_energy :
    executionEnergy .memoryExceeded = 1000000 := rfl

/-- **Energy is always non-negative**. -/
theorem execution_energy_nonneg (outcome : ExecutionOutcome) :
    0 ≤ executionEnergy outcome := by
  cases outcome <;> simp [executionEnergy]

/-- **Failure energy is bounded below maximum pain**. -/
theorem failure_energy_bounded (stderr : String) (rc : Int) (t : IsolationTier) :
    executionEnergy (.failure stderr rc t) ≤ executionEnergy .timeout := by
  simp [executionEnergy]
  norm_num


-- ============================================================
-- §6  Container Security Constraints (WP2)
-- ============================================================

/-- Security constraints for a Tier 2 container. -/
structure ContainerConstraints where
  networkDisabled : Bool
  readOnlyRootFS : Bool
  noNewPrivileges : Bool
  capDropAll : Bool
  nonRootUser : Bool
  pidLimit : ℕ
  memoryLimitBytes : ℕ
  tmpfsNoExec : Bool

/-- A container is hardened if ALL security constraints are enabled. -/
def isHardened (c : ContainerConstraints) : Prop :=
  c.networkDisabled = true ∧
  c.readOnlyRootFS = true ∧
  c.noNewPrivileges = true ∧
  c.capDropAll = true ∧
  c.nonRootUser = true ∧
  c.tmpfsNoExec = true ∧
  0 < c.pidLimit ∧
  0 < c.memoryLimitBytes

/-- **A hardened container isolates the network**. -/
theorem hardened_no_network (c : ContainerConstraints)
    (h : isHardened c) :
    c.networkDisabled = true := h.1

/-- **A hardened container has read-only root filesystem**. -/
theorem hardened_readonly_fs (c : ContainerConstraints)
    (h : isHardened c) :
    c.readOnlyRootFS = true := h.2.1

/-- **A hardened container drops all capabilities**. -/
theorem hardened_no_capabilities (c : ContainerConstraints)
    (h : isHardened c) :
    c.capDropAll = true := h.2.2.2.1

/-- **A hardened container runs as non-root**. -/
theorem hardened_nonroot (c : ContainerConstraints)
    (h : isHardened c) :
    c.nonRootUser = true := h.2.2.2.2.1

/-- **Hardening subsumes all individual constraints**:
    If a container is hardened, ALL security properties hold. -/
theorem hardened_implies_all_security (c : ContainerConstraints)
    (h : isHardened c) :
    c.networkDisabled = true ∧
    c.readOnlyRootFS = true ∧
    c.noNewPrivileges = true ∧
    c.capDropAll = true ∧
    c.nonRootUser = true ∧
    c.tmpfsNoExec = true := by
  exact ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1, h.2.2.2.2.1, h.2.2.2.2.2.1⟩


end ANSE.Sandbox
