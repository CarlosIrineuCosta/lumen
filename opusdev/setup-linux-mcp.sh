#!/bin/bash
# Setup script for MCP servers on Linux machine
# This installs Zen and Serena MCPs and configures them for Claude Desktop and Claude Code

echo "Setting up MCP servers on Linux machine..."

# Create MCP directory structure
MCP_DIR="/home/cdc/mcp-servers"
mkdir -p "$MCP_DIR"
cd "$MCP_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Installing Zen MCP Server ===${NC}"
echo "Zen MCP orchestrates multiple AI models (Gemini, OpenAI, etc.) for enhanced development"

# Clone Zen MCP
if [ ! -d "$MCP_DIR/zen-mcp-server" ]; then
    git clone https://github.com/BeehiveInnovations/zen-mcp-server.git
    cd zen-mcp-server
    
    # Install dependencies
    echo -e "${YELLOW}Installing Zen dependencies...${NC}"
    npm install
    
    echo -e "${GREEN}✓ Zen MCP installed${NC}"
else
    echo -e "${YELLOW}Zen MCP already exists, updating...${NC}"
    cd zen-mcp-server
    git pull
    npm install
fi

echo -e "${BLUE}=== Installing Serena MCP Server ===${NC}"
echo "Serena provides semantic code analysis and editing capabilities"

# Serena installation (Python-based, uses uv)
cd "$MCP_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create a wrapper script for Serena
cat > "$MCP_DIR/serena-start.sh" << 'EOF'
#!/bin/bash
# Serena MCP starter script
uvx --from git+https://github.com/oraios/serena serena start-mcp-server "$@"
EOF
chmod +x "$MCP_DIR/serena-start.sh"

echo -e "${GREEN}✓ Serena MCP prepared${NC}"

echo -e "${BLUE}=== Installing Playwright MCP Server ===${NC}"
echo "Playwright enables browser automation and console monitoring"

# Clone the official Playwright MCP
if [ ! -d "$MCP_DIR/playwright-mcp" ]; then
    git clone https://github.com/microsoft/playwright-mcp.git
    cd playwright-mcp
    npm install
    echo -e "${GREEN}✓ Playwright MCP installed${NC}"
else
    echo -e "${YELLOW}Playwright MCP already exists, updating...${NC}"
    cd playwright-mcp
    git pull
    npm install
fi

echo -e "${BLUE}=== Creating MCP Configuration Files ===${NC}"

# Create Claude Desktop config for Linux
CONFIG_DIR="$HOME/.config/claude"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "zen": {
      "command": "node",
      "args": ["$MCP_DIR/zen-mcp-server/dist/index.js"],
      "env": {
        "GEMINI_API_KEY": "YOUR_GEMINI_KEY",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY",
        "OPENROUTER_API_KEY": "YOUR_OPENROUTER_KEY"
      }
    },
    "serena": {
      "command": "$MCP_DIR/serena-start.sh",
      "args": ["--context", "ide-assistant"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless=false"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/cdc/projects"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
EOF

echo -e "${GREEN}✓ Claude Desktop config created at $CONFIG_DIR/claude_desktop_config.json${NC}"

# Create Claude Code config
cat > "$HOME/.codeium/mcp.json" << EOF
{
  "mcpServers": {
    "zen": {
      "command": "node",
      "args": ["$MCP_DIR/zen-mcp-server/dist/index.js"]
    },
    "serena": {
      "command": "$MCP_DIR/serena-start.sh",
      "args": ["--context", "ide-assistant", "--project", "\${workspaceRoot}"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    }
  }
}
EOF

echo -e "${GREEN}✓ Claude Code config created${NC}"

# Create environment file for API keys
cat > "$MCP_DIR/.env" << EOF
# Add your API keys here
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# For Zen MCP custom models
CUSTOM_MODELS_PATH=$MCP_DIR/zen-mcp-server/conf/custom_models.json
EOF

echo -e "${YELLOW}=== Setup Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Edit $MCP_DIR/.env and add your API keys"
echo "2. For Lumen development, port is configurable (not hardcoded to 8000)"
echo "3. Restart Claude Desktop and Claude Code to load MCPs"
echo ""
echo "MCP Commands Quick Reference:"
echo "  Zen: 'use zen to analyze this code with gemini pro'"
echo "  Serena: 'activate project /home/cdc/projects/wasenet/lumen-gcp'"
echo "  Playwright: 'navigate to http://localhost:PORT and check console errors'"
echo ""
echo -e "${GREEN}All MCP servers installed in: $MCP_DIR${NC}"
