# How to Open Lumen in Edge from VS Code

## Quick Solutions

### 🎯 Option 1: PowerShell Script (Most Reliable)
Right-click and "Run with PowerShell":
```
L:\Storage\NVMe\projects\lumen\frontend-simple\launch.ps1
```

### 🎯 Option 2: Batch File
Double-click:
```
L:\Storage\NVMe\projects\lumen\frontend-simple\open-in-edge.bat
```

### 🎯 Option 3: Direct File URL
Copy and paste this into Edge:
```
file:///L:/Storage/NVMe/projects/lumen/frontend-simple/index.html
```

## VS Code Integration

### Install Required Extension
1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search and install: **"Open in Browser"** by TechER
4. Search and install: **"Live Server"** by Ritwick Dey

### Use Live Server (Recommended)
1. Open `index.html` in VS Code
2. Right-click in the editor
3. Select "Open with Live Server"
4. This will start a local server and open in your default browser

### Configure Default Browser
Add this to your VS Code settings (`Ctrl+,`):
```json
"liveServer.settings.CustomBrowser": "microsoft-edge",
"open-in-browser.default": "msedge"
```

### Debug with Edge
1. Press `F5` in VS Code
2. Select "Open Lumen in Edge" from the dropdown

## Manual Testing

### Test File
Open this simpler test file first to verify Edge works:
```
L:\Storage\NVMe\projects\lumen\frontend-simple\test.html
```

### Direct Edge Command
Open Command Prompt and run:
```cmd
start msedge "file:///L:/Storage/NVMe/projects/lumen/frontend-simple/index.html"
```

## Troubleshooting

### If Edge won't open:
1. **Check if Edge is installed**: Type "edge://version" in Edge
2. **Check file path**: Ensure the path exists
3. **Try the test file first**: It's simpler and will confirm basic functionality
4. **Check Windows default apps**: Settings > Apps > Default apps > Web browser

### If VS Code won't open files:
1. **Reload VS Code**: `Ctrl+Shift+P` then "Reload Window"
2. **Check workspace trust**: File > Workspace Trust
3. **Use absolute paths**: Full path instead of relative

## Current File Structure
```
frontend-simple/
├── index.html          ← Main application
├── test.html           ← Simple test file
├── launch.ps1          ← PowerShell launcher
├── open-in-edge.bat    ← Batch file launcher
├── manifest.json       ← PWA manifest
├── sw.js              ← Service worker
└── serve.py           ← Python server
```

## Success Verification
When it works, you should see:
1. A dark background with purple gradient
2. "Lumen" logo at the top
3. Navigation with Gallery, Upload, Profile
4. Glass morphism effects on components

The test.html will show:
- "✅ Lumen Frontend is Working!"
- Current file path
- Button to main application