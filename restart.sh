#!/usr/bin/env bash
# ==============================================================================
# AutoevolveAI / ANSE — Easy Restart & Environment Verification Script
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE}  ANSE (Autopoietic Neuro-Symbolic Energy-based Model) — Environment Manager   ${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
}

usage() {
    echo -e "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status       (Default) Check environment, verify Lean 4, run fast benchmarks"
    echo "  test         Run complete test suite (195 tests across all modules)"
    echo "  test-fast    Run fast algorithmic & complexity tests only"
    echo "  lean         Build formal Lean 4 specification & verification proofs"
    echo "  run          Launch the ANSE main execution agent loop"
    echo "  web          Start the interactive Phase 1 & Phase 2 demonstration web server"
    echo "  clean        Clean temporary caches and sandbox artifacts"
    echo "  help         Display this help message"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}>>> Checking prerequisites...${NC}"
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}[ERROR] 'uv' package manager is not installed or not in PATH.${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] uv found: $(uv --version)${NC}"

    if ! command -v lake &> /dev/null; then
        echo -e "${YELLOW}[WARN] 'lake' (Lean 4) not found in global PATH. Checking ~/.elan/bin...${NC}"
        if [ -f "$HOME/.elan/bin/lake" ]; then
            export PATH="$HOME/.elan/bin:$PATH"
            echo -e "${GREEN}[OK] Added elan/bin to PATH. Lake found: $(lake --version)${NC}"
        else
            echo -e "${RED}[ERROR] Lean 4 'lake' toolchain not found.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}[OK] lake found: $(lake --version)${NC}"
    fi
}

cmd_lean() {
    check_prerequisites
    echo -e "${YELLOW}>>> Building Lean 4 formal verification proofs...${NC}"
    cd "$SCRIPT_DIR/formal"
    lake build
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}[OK] Formal verification completed successfully!${NC}"
}

cmd_test_fast() {
    check_prerequisites
    echo -e "${YELLOW}>>> Running fast performance & complexity benchmarks...${NC}"
    uv run pytest tests/performance/ -v
    echo -e "${GREEN}[OK] Fast benchmarks passed!${NC}"
}

cmd_test() {
    check_prerequisites
    echo -e "${YELLOW}>>> Running complete test suite (195 tests)...${NC}"
    uv run pytest tests/
    echo -e "${GREEN}[OK] All tests passed cleanly!${NC}"
}

cmd_run() {
    check_prerequisites
    echo -e "${YELLOW}>>> Launching ANSE Agent Loop...${NC}"
    uv run python main.py "$@"
}

cmd_web() {
    check_prerequisites
    echo -e "${YELLOW}>>> Launching ANSE Interactive Web Server...${NC}"
    uv run python web/server.py "$@"
}

cmd_clean() {
    echo -e "${YELLOW}>>> Cleaning cache files and sandbox artifacts...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    rm -f .coverage
    rm -rf /tmp/anse_t1_* 2>/dev/null || true
    echo -e "${GREEN}[OK] Cleanup complete.${NC}"
}

cmd_status() {
    print_header
    check_prerequisites
    echo ""
    cmd_lean
    echo ""
    cmd_test_fast
    echo ""
    echo -e "${GREEN}==============================================================================${NC}"
    echo -e "${GREEN}  ANSE SYSTEM READY — All formal proofs & physical benchmarks validated.     ${NC}"
    echo -e "${GREEN}==============================================================================${NC}"
}

ACTION="${1:-status}"

case "$ACTION" in
    status)
        cmd_status
        ;;
    test)
        print_header
        cmd_test
        ;;
    test-fast)
        print_header
        cmd_test_fast
        ;;
    lean)
        print_header
        cmd_lean
        ;;
    run)
        print_header
        shift || true
        cmd_run "$@"
        ;;
    web)
        print_header
        shift || true
        cmd_web "$@"
        ;;
    clean)
        cmd_clean
        ;;
    help|--help|-h)
        print_header
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $ACTION${NC}"
        usage
        exit 1
        ;;
esac
