#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# nightly_dispatch.sh — Automated Jules Mission Dispatch (PR Factory)
#
# Reads missions from missions.yaml and dispatches each to Jules.
# Designed to run from cron or GitHub Actions on a nightly schedule.
#
# Usage:
#   REPO=xaviercallens/AutoevolveAI ./nightly_dispatch.sh
#   ./nightly_dispatch.sh --dry-run
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="${REPO:-xaviercallens/AutoevolveAI}"
DRY_RUN=false
LOG_DIR="results/factory"
MISSIONS_FILE="${MISSIONS_FILE:-missions.yaml}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/dispatch_${TIMESTAMP}.log"

# God Prompt Antigravity Rules — injected into every mission
GOD_PROMPT="CONTRAINTES STRICTES:
1. ANTI-STUB: Interdiction absolue d'utiliser 'pass', 'TODO' ou des mocks non contractuels.
2. LEAN: Chaque modification logique doit s'accompagner d'une mise à jour de la spécification .lean dans formal/ANSE/.
3. PERFORMANCE: Refactorise pour atteindre une complexité spatiale/temporelle O(1) ou O(n log n).
4. EXÉCUTION: Tu as accès au terminal. Tu DOIS lancer 'make verify-all'. Corrige tes erreurs tant que le make échoue. N'ouvre la PR que lorsque tout est au vert."

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --help|-h) echo "Usage: $0 [--dry-run]"; exit 0 ;;
  esac
done

mkdir -p "$LOG_DIR"

log() {
  local msg="[$(date '+%H:%M:%S')] $1"
  echo "$msg" | tee -a "$LOG_FILE"
}

log "═══════════════════════════════════════════════════"
log "🏭 PR Factory — Nightly Dispatch"
log "   Repo:      $REPO"
log "   Missions:  $MISSIONS_FILE"
log "   Dry-run:   $DRY_RUN"
log "═══════════════════════════════════════════════════"

if ! command -v jules &>/dev/null; then
  log "⚠️  Jules CLI not found. Install: npm install -g @google/jules"
  if [ "$DRY_RUN" = false ]; then
    log "❌ Cannot dispatch without Jules CLI. Exiting."
    exit 1
  fi
fi

if [ ! -f "$MISSIONS_FILE" ]; then
  log "❌ Missions file not found: $MISSIONS_FILE"
  exit 1
fi

# Parse missions from YAML (simple grep-based parser for portability)
MISSION_COUNT=0
DISPATCH_COUNT=0
FAIL_COUNT=0

# Read missions line by line
parse_missions() {
  local in_mission=false
  local m_type="" m_target="" m_desc=""
  
  while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*type: ]]; then
      # If we had a previous mission, dispatch it
      if [ "$in_mission" = true ]; then
        dispatch_mission "$m_type" "$m_target" "$m_desc"
      fi
      in_mission=true
      m_type="$(echo "$line" | sed 's/.*type:[[:space:]]*//' | tr -d '"' | tr -d "'")"
      m_target=""
      m_desc=""
    elif [[ "$line" =~ ^[[:space:]]*target: ]]; then
      m_target="$(echo "$line" | sed 's/.*target:[[:space:]]*//' | tr -d '"' | tr -d "'")"
    elif [[ "$line" =~ ^[[:space:]]*description: ]]; then
      m_desc="$(echo "$line" | sed 's/.*description:[[:space:]]*//' | tr -d '"' | tr -d "'")"
    fi
  done < "$MISSIONS_FILE"
  
  # Dispatch the last mission
  if [ "$in_mission" = true ]; then
    dispatch_mission "$m_type" "$m_target" "$m_desc"
  fi
}

dispatch_mission() {
  local type="$1" target="$2" desc="$3"
  MISSION_COUNT=$((MISSION_COUNT + 1))
  
  # Build the session prompt
  local prompt=""
  case "$type" in
    performance)
      prompt="Mission Perf: Optimise le composant $target. Profiling: identifie les hot paths, élimine les allocations inutiles."
      ;;
    qa|qa_fuzzing)
      prompt="Mission QA: Développe la matrice de tests fuzzing pour $target. Utilise Hypothesis pour les property-based tests."
      ;;
    security)
      prompt="Mission Sécu: Patche les failles d'injection SQL potentielles sur $target."
      ;;
    lean_proof)
      prompt="Mission Lean: Ajoute la preuve formelle Lean 4 pour $target sans 'sorry'."
      ;;
    custom)
      prompt="$desc"
      ;;
    *)
      log "⚠️  Unknown mission type: $type — skipping"
      return
      ;;
  esac
  
  local full_prompt="$prompt

$GOD_PROMPT"
  
  log ""
  log "── Mission #$MISSION_COUNT ──"
  log "   Type:   $type"
  log "   Target: $target"
  log "   Desc:   ${desc:-(from template)}"
  
  if [ "$DRY_RUN" = true ]; then
    log "   [DRY-RUN] Would dispatch: jules remote new --repo $REPO"
    log "   [DRY-RUN] Prompt: ${prompt:0:100}..."
    DISPATCH_COUNT=$((DISPATCH_COUNT + 1))
    return
  fi
  
  # Dispatch to Jules
  if jules remote new \
    --repo "$REPO" \
    --session "$full_prompt" \
    >> "$LOG_FILE" 2>&1; then
    log "   ✅ Dispatched successfully"
    DISPATCH_COUNT=$((DISPATCH_COUNT + 1))
  else
    log "   ❌ Dispatch failed (see log for details)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  
  # Small delay between dispatches to avoid rate limiting
  sleep 2
}

parse_missions

log ""
log "═══════════════════════════════════════════════════"
log "🏭 Dispatch Summary"
log "   Total:      $MISSION_COUNT"
log "   Dispatched: $DISPATCH_COUNT"
log "   Failed:     $FAIL_COUNT"
log "   Log:        $LOG_FILE"
log "═══════════════════════════════════════════════════"

exit "$FAIL_COUNT"
