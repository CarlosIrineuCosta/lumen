#!/bin/bash
echo "Starting Lumen Test Server..."
echo ""
echo "Test URLs:"
echo "- Main App: http://localhost:8000"
echo "- Photo Viewer Test: http://localhost:8000/test-viewer.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python3 -m http.server 8000