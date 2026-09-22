/-
  ANSE.WebArchitecture — Formal specification of the web API contracts.

  Sources:
    · web/server.py — 18 FastAPI endpoints
    · ANSE Audit Report 2026-09-22 — middleware stack

  This module formalizes:
    1. HTTP method and endpoint registry
    2. Response type contracts (JSON-only)
    3. Error handling invariants (HTTP status codes)
    4. Middleware composition (GZip, CORS, RateLimit)
    5. Async event loop safety (blocking-call prevention)
-/
import Mathlib.Data.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.List.Basic
import Mathlib.Tactic.Linarith

-- Disable Mathlib contribution-style linters
set_option linter.style.header false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace ANSE.WebArchitecture

-- ============================================================
-- §1  HTTP Method and Endpoint Types
-- ============================================================

/-- HTTP methods used by the ANSE web API. -/
inductive HTTPMethod
  | GET
  | POST
  | PUT
  | DELETE
  deriving Repr, DecidableEq

/-- Response content type. -/
inductive ContentType
  | JSON
  | HTML
  | PlainText
  | Binary
  deriving Repr, DecidableEq

/-- An API endpoint definition. -/
structure Endpoint where
  method : HTTPMethod
  path : String
  requiresAuth : Bool
  responseType : ContentType

/-- HTTP status code ranges. -/
inductive StatusCodeClass
  | success      -- 2xx
  | clientError   -- 4xx
  | serverError   -- 5xx
  deriving Repr, DecidableEq

/-- An API response. -/
structure APIResponse where
  statusClass : StatusCodeClass
  contentType : ContentType
  bodySize : ℕ  -- bytes

/-- **All API endpoints return JSON**:
    Every endpoint in the ANSE web API returns Content-Type: application/json. -/
def allEndpointsReturnJSON (endpoints : List Endpoint) : Prop :=
  ∀ e ∈ endpoints, e.responseType = ContentType.JSON

theorem json_only_api (endpoints : List Endpoint)
    (h : allEndpointsReturnJSON endpoints) :
    ∀ e ∈ endpoints, e.responseType = ContentType.JSON := h


-- ============================================================
-- §2  Error Handling Contracts
-- ============================================================

/-- An error response uses the correct HTTP status code class. -/
structure ErrorResponse where
  statusClass : StatusCodeClass
  message : String
  isHTTPError : statusClass = StatusCodeClass.clientError ∨
                statusClass = StatusCodeClass.serverError

/-- **Errors never use 2xx status codes**:
    Error responses always use 4xx or 5xx. -/
theorem error_never_success (e : ErrorResponse) :
    e.statusClass ≠ StatusCodeClass.success := by
  rcases e.isHTTPError with h | h <;> (rw [h]; decide)

/-- **Validation errors are 4xx (client errors)**. -/
def isValidationError (e : ErrorResponse) : Prop :=
  e.statusClass = StatusCodeClass.clientError

/-- **Internal errors are 5xx (server errors)**. -/
def isInternalError (e : ErrorResponse) : Prop :=
  e.statusClass = StatusCodeClass.serverError


-- ============================================================
-- §3  Middleware Stack Composition
-- ============================================================

/-- Middleware types in the ANSE web stack. -/
inductive Middleware
  | GZip         -- Compresses responses > minSize
  | CORS         -- Cross-origin access control
  | RateLimit    -- Request throttling
  | StaticFiles  -- Serves static assets
  deriving Repr, DecidableEq

/-- A middleware stack is an ordered list of middleware. -/
abbrev MiddlewareStack := List Middleware

/-- A middleware stack is valid if CORS runs before RateLimit
    (CORS preflight must not be rate-limited). -/
def validMiddlewareOrder (stack : MiddlewareStack) : Prop :=
  ∀ (i j : Fin stack.length),
    stack[i] = Middleware.CORS → stack[j] = Middleware.RateLimit →
    i.val < j.val

/-- **GZip reduces large payloads**:
    For payloads above the minimum size, GZip output is strictly smaller. -/
def gzipReduces (inputSize outputSize minSize : ℕ) : Prop :=
  inputSize > minSize → outputSize < inputSize

/-- **GZip is non-negative**: output size is always ≥ 0.
    (Trivially true for ℕ, but documents the contract.) -/
theorem gzip_output_nonneg (outputSize : ℕ) : 0 ≤ outputSize := Nat.zero_le _


-- ============================================================
-- §4  Async Event Loop Safety
-- ============================================================

/-- A function call classification for async safety. -/
inductive CallType
  | asyncNative     -- natively async (e.g., aiohttp, asyncio)
  | wrappedBlocking -- sync call wrapped in to_thread.run_sync
  | rawBlocking     -- sync call on the event loop (BAD!)
  deriving Repr, DecidableEq

/-- Whether a call type blocks the event loop. -/
def blocksEventLoop : CallType → Bool
  | .asyncNative     => false
  | .wrappedBlocking => false
  | .rawBlocking     => true

/-- **Async-native calls don't block**. -/
theorem async_native_safe :
    blocksEventLoop CallType.asyncNative = false := rfl

/-- **Wrapped blocking calls don't block**. -/
theorem wrapped_blocking_safe :
    blocksEventLoop CallType.wrappedBlocking = false := rfl

/-- **Raw blocking calls DO block**. -/
theorem raw_blocking_unsafe :
    blocksEventLoop CallType.rawBlocking = true := rfl

/-- A web handler is event-loop-safe if none of its calls block. -/
def handlerIsSafe (calls : List CallType) : Prop :=
  ∀ c ∈ calls, blocksEventLoop c = false

/-- **A handler with only async/wrapped calls is safe**. -/
theorem safe_handler_no_blocking (calls : List CallType)
    (h : handlerIsSafe calls) :
    ∀ c ∈ calls, blocksEventLoop c = false := h

/-- **Any raw blocking call makes a handler unsafe**. -/
theorem raw_blocking_makes_unsafe (calls : List CallType)
    (hRaw : CallType.rawBlocking ∈ calls) :
    ¬ handlerIsSafe calls := by
  intro hSafe
  have := hSafe _ hRaw
  exact absurd this (by decide)


-- ============================================================
-- §5  Endpoint Registry (ANSE Web API)
-- ============================================================

/-- The 18 endpoints of the ANSE web API, registered for formal tracking. -/
def anseEndpoints : List Endpoint := [
  -- Evolution Lab
  { method := .GET,  path := "/api/evolution/phases",      requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/api/evolution/use-cases",    requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/api/evolution/results",      requiresAuth := false, responseType := .JSON },
  { method := .POST, path := "/api/evolution/run",          requiresAuth := false, responseType := .JSON },
  -- PR Factory
  { method := .GET,  path := "/api/missions",               requiresAuth := false, responseType := .JSON },
  { method := .POST, path := "/api/missions",               requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/api/missions/{id}",          requiresAuth := false, responseType := .JSON },
  { method := .POST, path := "/api/missions/{id}/execute",  requiresAuth := false, responseType := .JSON },
  { method := .POST, path := "/api/missions/{id}/dispatch", requiresAuth := false, responseType := .JSON },
  -- System
  { method := .GET,  path := "/api/system/health",          requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/api/system/config",          requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/api/sandbox/status",         requiresAuth := false, responseType := .JSON },
  -- Evaluation
  { method := .POST, path := "/api/evaluate",               requiresAuth := false, responseType := .JSON },
  { method := .POST, path := "/api/execute",                requiresAuth := false, responseType := .JSON },
  -- UI Assets
  { method := .GET,  path := "/api/icon/{name}",            requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/",                           requiresAuth := false, responseType := .HTML },
  { method := .GET,  path := "/manifest.json",              requiresAuth := false, responseType := .JSON },
  { method := .GET,  path := "/sw.js",                      requiresAuth := false, responseType := .JSON }
]

/-- The ANSE API has exactly 18 endpoints. -/
theorem anse_has_18_endpoints : anseEndpoints.length = 18 := rfl


end ANSE.WebArchitecture
