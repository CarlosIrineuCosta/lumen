#!/bin/bash
# LM Studio Headless Installation for Lumen Project
# Run on Linux dev server (100.106.201.33)

set -e

echo "=== LM Studio Headless Installation ==="
echo "This will install LM Studio for local AI code reviews"
echo ""

# Check system requirements
echo "Checking system requirements..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. Install NVIDIA drivers first."
    exit 1
fi

echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader

# Create directories
INSTALL_DIR="$HOME/lmstudio"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download LM Studio
echo ""
echo "Downloading LM Studio..."
if [ ! -f "LM-Studio-linux.AppImage" ]; then
    wget -O LM-Studio-linux.AppImage "https://installers.lmstudio.ai/linux/x64/0.3.26-6/LM-Studio-0.3.26-6-x64.AppImage"
    chmod +x LM-Studio-linux.AppImage
else
    echo "LM Studio already downloaded"
fi

# Extract AppImage for headless operation
echo "Extracting for headless operation..."
if [ ! -d "squashfs-root" ]; then
    ./LM-Studio-linux.AppImage --appimage-extract
fi

# Create headless startup script
cat > start-lmstudio-server.sh << 'EOF'
#!/bin/bash
# Start LM Studio in headless mode
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!

cd $(dirname $0)/squashfs-root
./AppRun --api-server --port 1234 &
LMSTUDIO_PID=$!

echo "LM Studio API running on http://localhost:1234"
echo "XVFB PID: $XVFB_PID"
echo "LM Studio PID: $LMSTUDIO_PID"

# Save PIDs for shutdown
echo "$XVFB_PID" > ../xvfb.pid
echo "$LMSTUDIO_PID" > ../lmstudio.pid

wait $LMSTUDIO_PID
EOF

chmod +x start-lmstudio-server.sh

# Create shutdown script
cat > stop-lmstudio-server.sh << 'EOF'
#!/bin/bash
if [ -f lmstudio.pid ]; then
    kill $(cat lmstudio.pid) 2>/dev/null
    rm lmstudio.pid
fi
if [ -f xvfb.pid ]; then
    kill $(cat xvfb.pid) 2>/dev/null
    rm xvfb.pid
fi
echo "LM Studio server stopped"
EOF

chmod +x stop-lmstudio-server.sh

# Install Xvfb if not present
if ! command -v Xvfb &> /dev/null; then
    echo "Installing Xvfb for headless operation..."
    sudo apt-get update
    sudo apt-get install -y xvfb
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Start the server: cd $INSTALL_DIR && ./start-lmstudio-server.sh"
echo "2. Download a model through the API or GUI"
echo "3. Test API: curl http://localhost:1234/v1/models"
echo ""
echo "Recommended models for code review:"
echo "- codellama-13b-instruct"
echo "- deepseek-coder-6.7b-instruct"
echo "- llama-3.2-3b-instruct (lightweight)"
