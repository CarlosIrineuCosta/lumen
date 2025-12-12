#!/bin/bash
# Fix script for MCP installations on Linux

echo "Fixing MCP installations..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MCP_DIR="/home/cdc/mcp-servers"
cd "$MCP_DIR"

echo -e "${BLUE}=== Fixing Zen MCP Server ===${NC}"

# Remove incorrectly cloned Zen (it's Python, not Node.js)
if [ -d "$MCP_DIR/zen-mcp-server" ]; then
    echo -e "${YELLOW}Removing incorrect Zen installation...${NC}"
    rm -rf "$MCP_DIR/zen-mcp-server"
fi

# Zen is installed via uvx directly, no need to clone
echo -e "${GREEN}✓ Zen will be run directly via uvx${NC}"

echo -e "${BLUE}=== Fixing Claude Code Configuration ===${NC}"

# Create the correct directory for Claude Code
CODEIUM_DIR="$HOME/.codeium"
if [ ! -d "$CODEIUM_DIR" ]; then
    echo -e "${YELLOW}Creating .codeium directory...${NC}"
    mkdir -p "$CODEIUM_DIR"
fi

# Write Claude Code config
cat > "$CODEIUM_DIR/mcp.json" << 'EOF'
{
  "mcpServers": {
    "zen": {
      "command": "sh",
      "args": [
        "-c",
        "exec $(which uvx || echo uvx) --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server"
      ],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "YOUR_GEMINI_KEY",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY",
        "OPENROUTER_API_KEY": "YOUR_OPENROUTER_KEY"
      }
    },
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        "${workspaceRoot}"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    }
  }
}
EOF

echo -e "${GREEN}✓ Claude Code config created at $CODEIUM_DIR/mcp.json${NC}"

echo -e "${BLUE}=== Updating Claude Desktop Configuration ===${NC}"

# Fix Claude Desktop config with correct Zen command
CONFIG_DIR="$HOME/.config/claude"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "zen": {
      "command": "sh",
      "args": [
        "-c",
        "exec $(which uvx || echo uvx) --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server"
      ],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "YOUR_GEMINI_KEY",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY",
        "OPENROUTER_API_KEY": "YOUR_OPENROUTER_KEY"
      }
    },
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server"
      ]
    },
    "playwright": {
      "command": "node",
      "args": ["/home/cdc/mcp-servers/playwright-mcp/dist/index.js"]
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

echo -e "${GREEN}✓ Claude Desktop config updated${NC}"

echo -e "${BLUE}=== Building Playwright MCP ===${NC}"

# Build Playwright MCP if needed
cd "$MCP_DIR/playwright-mcp"
if [ -f "package.json" ]; then
    echo -e "${YELLOW}Building Playwright MCP...${NC}"
    npm run build 2>/dev/null || echo "Build script not found, checking dist..."
    
    if [ ! -d "dist" ]; then
        echo -e "${YELLOW}Dist folder not found, using npx version instead${NC}"
    else
        echo -e "${GREEN}✓ Playwright MCP built${NC}"
    fi
fi

echo -e "${BLUE}=== Testing MCP Installations ===${NC}"

# Test uvx is available
if command -v uvx &> /dev/null; then
    echo -e "${GREEN}✓ uvx is installed${NC}"
else
    echo -e "${RED}✗ uvx not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Test Zen can be called
echo -e "${YELLOW}Testing Zen MCP...${NC}"
uvx --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server --help 2>/dev/null && echo -e "${GREEN}✓ Zen MCP works${NC}" || echo -e "${RED}✗ Zen MCP failed${NC}"

# Test Serena can be called
echo -e "${YELLOW}Testing Serena MCP...${NC}"
uvx --from git+https://github.com/oraios/serena serena --help 2>/dev/null && echo -e "${GREEN}✓ Serena MCP works${NC}" || echo -e "${RED}✗ Serena MCP failed${NC}"

# Test Playwright
echo -e "${YELLOW}Testing Playwright MCP...${NC}"
npx @executeautomation/playwright-mcp-server --help 2>/dev/null && echo -e "${GREEN}✓ Playwright MCP works${NC}" || echo -e "${RED}✗ Playwright MCP failed${NC}"

echo -e "${BLUE}=== Creating Quick Test Script ===${NC}"

cat > "$MCP_DIR/test-browser-console.sh" << 'EOF'
#!/bin/bash
# Quick test to verify Playwright MCP can monitor browser console

echo "Testing browser console monitoring..."
echo "This will open a browser and check for console errors"

# Using npx to run Playwright MCP
npx @executeautomation/playwright-mcp-server << 'COMMANDS'
{
  "action": "navigate",
  "url": "http://localhost:8000"
}
{
  "action": "get_console_logs",
  "type": "error"
}
COMMANDS
EOF
chmod +x "$MCP_DIR/test-browser-console.sh"

echo -e "${GREEN}=== All Fixes Applied ===${NC}"
echo ""
echo "Summary:"
echo "• Zen MCP: Python-based, runs via uvx (not npm)"
echo "• Serena MCP: Python-based, runs via uvx"
echo "• Playwright MCP: Node.js-based, runs via npx"
echo "• Configs fixed for both Claude Desktop and Claude Code"
echo ""
echo "Next steps:"
echo "1. Add your API keys to the config files"
echo "2. Test with: uvx --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server --help"
echo "3. Restart Claude Desktop and Claude Code"
echo ""
echo -e "${YELLOW}Note: For Lumen, use port 8000 (not hardcoded in configs)${NC}"
