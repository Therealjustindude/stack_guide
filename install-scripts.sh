#!/usr/bin/env bash

# StackGuide Scripts Installation Script
# Installs the stackguide scripts to your PATH for easy access

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 StackGuide Scripts Installation${NC}"
echo "======================================"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if scripts exist
if [ ! -f "$SCRIPT_DIR/stackguide" ]; then
    echo -e "${RED}❌ stackguide script not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Determine the target directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TARGET_DIR="$HOME/.local/bin"
    SHELL_RC="$HOME/.zshrc"
    if [ ! -f "$SHELL_RC" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    TARGET_DIR="$HOME/.local/bin"
    SHELL_RC="$HOME/.bashrc"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash, Cygwin)
    TARGET_DIR="$HOME/.local/bin"
    SHELL_RC="$HOME/.bashrc"
else
    echo -e "${YELLOW}⚠️  Unknown OS type: $OSTYPE${NC}"
    echo "Please manually add the scripts to your PATH"
    exit 1
fi

echo -e "${BLUE}📁 Target directory: $TARGET_DIR${NC}"
echo -e "${BLUE}📝 Shell configuration: $SHELL_RC${NC}"
echo ""

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}📁 Creating directory: $TARGET_DIR${NC}"
    mkdir -p "$TARGET_DIR"
fi

# Copy scripts to target directory
echo -e "${BLUE}📋 Installing scripts...${NC}"

# Copy main script
cp "$SCRIPT_DIR/stackguide" "$TARGET_DIR/"
chmod +x "$TARGET_DIR/stackguide"

# Copy Windows scripts if on Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    if [ -f "$SCRIPT_DIR/stackguide.bat" ]; then
        cp "$SCRIPT_DIR/stackguide.bat" "$TARGET_DIR/"
    fi
    if [ -f "$SCRIPT_DIR/stackguide.ps1" ]; then
        cp "$SCRIPT_DIR/stackguide.ps1" "$TARGET_DIR/"
    fi
fi

echo -e "${GREEN}✅ Scripts copied to $TARGET_DIR${NC}"

# Check if PATH already includes target directory
if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️  Adding $TARGET_DIR to PATH...${NC}"
    
    # Add to shell configuration
    if [ -f "$SHELL_RC" ]; then
        echo "" >> "$SHELL_RC"
        echo "# StackGuide scripts" >> "$SHELL_RC"
        echo "export PATH=\"\$PATH:$TARGET_DIR\"" >> "$SHELL_RC"
        echo -e "${GREEN}✅ Added to $SHELL_RC${NC}"
        
        echo -e "${YELLOW}⚠️  Please restart your terminal or run: source $SHELL_RC${NC}"
    else
        echo -e "${RED}❌ Could not find shell configuration file${NC}"
        echo "Please manually add the following line to your shell configuration:"
        echo "export PATH=\"\$PATH:$TARGET_DIR\""
    fi
else
    echo -e "${GREEN}✅ $TARGET_DIR is already in your PATH${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""
echo -e "${BLUE}📖 Usage Examples:${NC}"
echo "  stackguide start          # Start services and open CLI"
echo "  stackguide ingest-url     # Ingest URLs from Confluence, Notion, GitHub"
echo "  stackguide query 'How do I set up the database?'"
echo "  stackguide status         # Check system status"
echo "  stackguide help           # Show all available commands"
echo ""
echo -e "${YELLOW}💡 Pro tip: You can now run 'stackguide' from any directory!${NC}"

# Test if the script is accessible
if command -v stackguide >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Script is accessible from PATH${NC}"
else
    echo -e "${YELLOW}⚠️  Script not yet accessible. Please restart your terminal.${NC}"
fi
