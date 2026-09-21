#!/bin/bash
set -e

echo "================================================="
echo " Antigravity MCP Cluster Setup & Launcher Script "
echo "================================================="

# 1. Check for Node.js (Required for community MCP servers)
if ! command -v npm &> /dev/null; then
    echo "[!] npm could not be found. Installing Node.js (v20)..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "[OK] Node.js and npm are already installed."
fi

# 2. Install Official MCP Servers globally
echo "[*] Downloading and installing Official MCP Servers..."
sudo npm install -g @modelcontextprotocol/server-sequential-thinking
sudo npm install -g @modelcontextprotocol/server-filesystem
sudo npm install -g @modelcontextprotocol/server-github
sudo npm install -g @modelcontextprotocol/server-memory

# 3. Check for uv (Python package manager)
if ! command -v uv &> /dev/null; then
    echo "[!] uv could not be found. Installing astral-uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
else
    echo "[OK] uv is already installed."
fi

# 4. Sync Python dependencies for the Local Guard Server
echo "[*] Syncing Python dependencies for Antigravity Guard MCP Server..."
uv sync --all-extras

echo "================================================="
echo " Installation Complete! "
echo "================================================="
echo "The MCP servers are now installed and ready to be routed via the Gateway."
echo "Your Antigravity MCP configuration is located at: .antigravity/mcp_config.json"
echo ""
echo "▶ OPTION 1: Launch the Local Antigravity Guard MCP Server standalone:"
echo "    uv run python mcp_guard_server.py"
echo ""
echo "▶ OPTION 2: Launch the MCP Inspector UI to visually debug the Guard Server:"
echo "    npx @modelcontextprotocol/inspector uv run python mcp_guard_server.py"
echo ""
echo "▶ OPTION 3: Launch the Antigravity Gateway (Cognitive Router):"
echo "    uv run python gateway.py --mcp-config .antigravity/mcp_config.json"
echo "================================================="
