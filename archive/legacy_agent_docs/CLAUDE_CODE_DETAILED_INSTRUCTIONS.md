# DETAILED INSTRUCTIONS FOR CLAUDE CODE - LM Studio Setup

## Project Location
- Linux path: `/home/cdc/Storage/NVMe/projects/lumen/`
- Server IP: 100.106.201.33

## About the LM Studio Frontend Issue

**The Problem**: LM Studio is a GUI application that normally requires a display. On a headless Linux server (no monitor), this won't work by default.

**The Solution**: The install script creates a "virtual display" using Xvfb (X Virtual Framebuffer). This tricks LM Studio into thinking there's a monitor attached, allowing it to run in "headless" mode while exposing its API on port 1234.

## Step-by-Step Setup Instructions

### 1. Navigate to Project Directory
```bash
cd /home/cdc/Storage/NVMe/projects/lumen
```

### 2. Make Scripts Executable
```bash
chmod +x scripts/agents/install-lmstudio.sh
chmod +x scripts/agents/ai-agent.sh
chmod +x scripts/agents/test-setup.sh
```

### 3. Install Dependencies First
```bash
# Install required packages
sudo apt-get update
sudo apt-get install -y xvfb jq curl wget

# Verify GPU drivers are installed
nvidia-smi
# You should see your GPU(s) listed. If not, install NVIDIA drivers first.
```

### 4. Run LM Studio Installation
```bash
./scripts/agents/install-lmstudio.sh
```

This script will:
- Check for NVIDIA GPU drivers
- Download LM Studio AppImage
- Extract it for headless operation
- Create start/stop scripts
- Install Xvfb if needed

### 5. Start LM Studio Server
```bash
cd ~/lmstudio
./start-lmstudio-server.sh
```

You should see:
```
LM Studio API running on http://localhost:1234
XVFB PID: [some number]
LM Studio PID: [some number]
```

### 6. Download a Model

Option A: Use the API (recommended)
```bash
# List available models
curl http://localhost:1234/v1/models

# Download a specific model (example with llama-3.2-3b)
curl -X POST http://localhost:1234/v1/models/download \
  -H "Content-Type: application/json" \
  -d '{"model": "TheBloke/Llama-2-7B-Chat-GGUF"}'
```

Option B: Use the GUI via X11 forwarding (if you have X11 set up)
```bash
# From your local machine with X11
ssh -X user@100.106.201.33
cd ~/lmstudio/squashfs-root
./AppRun
# Use the GUI to download models
```

### 7. Configure API Keys (Optional)
```bash
# Add to ~/.bashrc
echo 'export SAMBANOVA_API_KEY="your_key_here"' >> ~/.bashrc
echo 'export OPENROUTER_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 8. Test the Multi-Agent System
```bash
cd /home/cdc/Storage/NVMe/projects/lumen

# Run the test suite
./scripts/agents/test-setup.sh

# Test LM Studio connection
./scripts/agents/ai-agent.sh lmstudio "Test connection - respond with OK"

# Test auto-selection (will use LM Studio if running)
./scripts/agents/ai-agent.sh auto "Explain what Lumen is"

# Test code review
./scripts/agents/ai-agent.sh lmstudio "Review this code for security issues" "" backend/auth/firebase_auth.py
```

### 9. Test Python Coordinator
```bash
# Check current status
python3 scripts/agents/agent_coordinator.py list

# Update task status
python3 scripts/agents/agent_coordinator.py update "Install LM Studio" "Claude Code" "Completed" "Successfully installed and tested"

# Request a code review
python3 scripts/agents/agent_coordinator.py review "Check for CORS issues" backend/main.py backend/middleware/cors.py

# Complete a task
python3 scripts/agents/agent_coordinator.py complete "Install LM Studio" "Test with real code files"
```

### 10. Make it Persistent (Auto-start on boot)

Create a systemd service:
```bash
sudo nano /etc/systemd/system/lmstudio.service
```

Add this content:
```ini
[Unit]
Description=LM Studio API Server
After=network.target

[Service]
Type=simple
User=cdc
WorkingDirectory=/home/cdc/lmstudio
ExecStart=/home/cdc/lmstudio/start-lmstudio-server.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lmstudio
sudo systemctl start lmstudio
sudo systemctl status lmstudio
```

## Troubleshooting

### If LM Studio won't start:
```bash
# Check if port 1234 is in use
sudo lsof -i :1234

# Check Xvfb is running
ps aux | grep Xvfb

# Check logs
cd ~/lmstudio
cat nohup.out

# Kill stuck processes
./stop-lmstudio-server.sh
```

### If API calls fail:
```bash
# Test API directly
curl http://localhost:1234/v1/models

# Check if jq is installed
which jq || sudo apt-get install jq

# Test with verbose output
./scripts/agents/ai-agent.sh lmstudio "test" 2>&1
```

### If GPU isn't detected:
```bash
# Check NVIDIA drivers
nvidia-smi

# Install if missing
sudo apt-get install nvidia-driver-525  # or latest version

# Reboot after driver install
sudo reboot
```

## File Locations Summary

- **Coordination Status**: `/home/cdc/Storage/NVMe/projects/lumen/agents/COORDINATION.md`
- **Task History**: `/home/cdc/Storage/NVMe/projects/lumen/.agents/tasks.json`
- **Code Reviews**: `/home/cdc/Storage/NVMe/projects/lumen/.agents/reviews/`
- **LM Studio**: `~/lmstudio/`
- **Scripts**: `/home/cdc/Storage/NVMe/projects/lumen/scripts/agents/`

## Daily Workflow

1. **Start of day**: Check coordination status
   ```bash
   cat /home/cdc/Storage/NVMe/projects/lumen/agents/COORDINATION.md
   python3 scripts/agents/agent_coordinator.py list
   ```

2. **During work**: Update task status
   ```bash
   python3 scripts/agents/agent_coordinator.py update "Task name" "Claude Code" "In Progress"
   ```

3. **After completing code**: Request AI review
   ```bash
   python3 scripts/agents/agent_coordinator.py review "Review for bugs" file1.py file2.js
   ```

4. **Task completion**: Mark complete and set next
   ```bash
   python3 scripts/agents/agent_coordinator.py complete "Current task" "Next task"
   ```

## IMPORTANT NOTES

1. **LM Studio runs locally** - No data leaves the server
2. **Coordination is lightweight** - Only 15 lines in COORDINATION.md
3. **Reviews are saved** - Check `.agents/reviews/` for history
4. **Auto-fallback works** - If LM Studio is down, it tries cloud providers
5. **Everything is scriptable** - No manual file editing needed

## Questions?

If you encounter any issues not covered here:
1. Check the test script output: `./scripts/agents/test-setup.sh`
2. Look for error logs in `~/lmstudio/`
3. Verify all services are running: `systemctl status lmstudio`
