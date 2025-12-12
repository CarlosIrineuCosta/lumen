#!/bin/bash
# Correct MCP installation script with proper NVMe paths

echo "=== Fixing MCP Installation Paths ==="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# CORRECT PATHS
MCP_ROOT="/home/cdc/Storage/NVMe/mcp-servers"
OLD_MCP="/home/cdc/mcp-servers"

echo -e "${BLUE}Current location: $(pwd)${NC}"

# First, let's find where things were installed
echo -e "${YELLOW}=== Finding existing installations ===${NC}"

echo "Looking for mcp-servers directories..."
find /home/cdc -type d -name "mcp-servers" 2>/dev/null

echo "Looking for .codeium directory..."
find /home/cdc -type d -name ".codeium" 2>/dev/null

echo "Looking for claude configs..."
find /home/cdc -name "claude_desktop_config.json" 2>/dev/null

# Move incorrectly placed files
if [ -d "$OLD_MCP" ]; then
    echo -e "${YELLOW}Found MCP in wrong location: $OLD_MCP${NC}"
    echo -e "${BLUE}Moving to correct location: $MCP_ROOT${NC}"
    
    # Create correct directory structure
    mkdir -p "$(dirname $MCP_ROOT)"
    
    # Move the directory
    mv "$OLD_MCP" "$MCP_ROOT"
    echo -e "${GREEN}✓ Moved MCP to correct location${NC}"
else
    echo -e "${YELLOW}No MCP found at old location${NC}"
fi

# Ensure correct directory exists
mkdir -p "$MCP_ROOT"
cd "$MCP_ROOT"
echo -e "${GREEN}✓ Working directory: $MCP_ROOT${NC}"

# The .codeium directory should be in home
CODEIUM_DIR="$HOME/.codeium"
echo -e "${BLUE}=== Setting up Claude Code config ===${NC}"
echo "Creating $CODEIUM_DIR if needed..."
mkdir -p "$CODEIUM_DIR"

# Create Claude Code config with CORRECT paths
cat > "$CODEIUM_DIR/mcp.json" << EOF
{
  "mcpServers": {
    "zen": {
      "command": "sh",
      "args": [
        "-c",
        "exec \$(which uvx || echo uvx) --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server"
      ],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "YOUR_KEY",
        "OPENAI_API_KEY": "YOUR_KEY"
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
        "ide-assistant"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/cdc/Storage/NVMe/projects"
      ]
    }
  }
}
EOF
echo -e "${GREEN}✓ Claude Code config: $CODEIUM_DIR/mcp.json${NC}"

# Create Claude Desktop config with CORRECT paths
CONFIG_DIR="$HOME/.config/claude"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "zen": {
      "command": "sh",
      "args": [
        "-c",
        "exec \$(which uvx || echo uvx) --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server"
      ],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "YOUR_KEY",
        "OPENAI_API_KEY": "YOUR_KEY"
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
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/cdc/Storage/NVMe/projects"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
EOF
echo -e "${GREEN}✓ Claude Desktop config: $CONFIG_DIR/claude_desktop_config.json${NC}"

# Fix Playwright MCP if it exists in wrong location
if [ -d "$MCP_ROOT/playwright-mcp" ]; then
    echo -e "${GREEN}✓ Playwright MCP found in correct location${NC}"
else
    echo -e "${YELLOW}Playwright MCP not found, will be run via npx${NC}"
fi

echo -e "${BLUE}=== Directory Structure Summary ===${NC}"
echo "MCP Servers location: $MCP_ROOT"
echo "Projects location: /home/cdc/Storage/NVMe/projects"
echo "Claude Code config: $HOME/.codeium/mcp.json"
echo "Claude Desktop config: $HOME/.config/claude/claude_desktop_config.json"

echo -e "${BLUE}=== Testing Commands ===${NC}"
echo "You can test each MCP with:"
echo "  uvx --from git+https://github.com/BeehiveInnovations/zen-mcp-server.git zen-mcp-server --help"
echo "  uvx --from git+https://github.com/oraios/serena serena --help"
echo "  npx @executeautomation/playwright-mcp-server --help"

echo -e "${YELLOW}=== Windows Mapping Recommendation ===${NC}"
echo "You currently have L: mapped to /home/cdc/Storage/"
echo "Consider creating a direct mapping to NVMe:"
echo "  Windows: net use N: \\\\wsl$\\Ubuntu\\home\\cdc\\Storage\\NVMe"
echo "  Or in WSL: ln -s /home/cdc/Storage/NVMe ~/NVMe"

echo -e "${GREEN}=== Setup Complete ===${NC}"
echo "All MCP configurations now use the correct NVMe paths!"
