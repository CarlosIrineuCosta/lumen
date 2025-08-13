"""
Playwright Console Debugger MCP Server
For real-time browser console monitoring and error detection
"""

import asyncio
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, ConsoleMessage
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio

class PlaywrightDebugger:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.console_logs: List[Dict[str, Any]] = []
        self.network_errors: List[Dict[str, Any]] = []
        self.page_errors: List[str] = []
        self.playwright = None
        
    async def start_browser(self, headless: bool = False, browser_type: str = "chromium"):
        """Start browser instance"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            
        if browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unknown browser type: {browser_type}")
            
        self.page = await self.browser.new_page()
        
        # Set up event listeners
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_page_error)
        self.page.on("requestfailed", self._handle_request_failed)
        self.page.on("response", self._handle_response)
        
        return {"status": "Browser started", "browser": browser_type, "headless": headless}
        
    def _handle_console(self, msg: ConsoleMessage):
        """Handle console messages"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg.type,
            "text": msg.text,
            "location": msg.location if hasattr(msg, 'location') else None,
            "args": []
        }
        
        # Try to get argument values
        try:
            for arg in msg.args:
                log_entry["args"].append(str(arg))
        except:
            pass
            
        self.console_logs.append(log_entry)
        
    def _handle_page_error(self, error: Exception):
        """Handle page errors"""
        self.page_errors.append({
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "type": "page_error"
        })
        
    def _handle_request_failed(self, request):
        """Handle failed network requests"""
        self.network_errors.append({
            "timestamp": datetime.now().isoformat(),
            "url": request.url,
            "method": request.method,
            "failure": request.failure() if hasattr(request, 'failure') else "Unknown",
            "type": "network_error"
        })
        
    def _handle_response(self, response):
        """Handle responses to check for errors"""
        if response.status >= 400:
            self.network_errors.append({
                "timestamp": datetime.now().isoformat(),
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "type": "http_error"
            })
            
    async def navigate(self, url: str, wait_until: str = "domcontentloaded"):
        """Navigate to URL"""
        if not self.page:
            await self.start_browser()
            
        await self.page.goto(url, wait_until=wait_until)
        return {"status": "Navigated", "url": url}
        
    async def get_console_logs(self, 
                              type_filter: Optional[str] = None,
                              clear_after: bool = False) -> List[Dict]:
        """Get console logs with optional filtering"""
        logs = self.console_logs
        
        if type_filter:
            logs = [log for log in logs if log["type"] == type_filter]
            
        if clear_after:
            self.console_logs = []
            
        return logs
        
    async def get_errors(self) -> Dict[str, Any]:
        """Get all errors (console, page, network)"""
        return {
            "console_errors": [log for log in self.console_logs if log["type"] == "error"],
            "page_errors": self.page_errors,
            "network_errors": self.network_errors,
            "total_errors": len([log for log in self.console_logs if log["type"] == "error"]) + 
                           len(self.page_errors) + len(self.network_errors)
        }
        
    async def execute_script(self, script: str):
        """Execute JavaScript in page context"""
        if not self.page:
            raise Exception("No page loaded")
            
        result = await self.page.evaluate(script)
        return {"result": result}
        
    async def take_screenshot(self, full_page: bool = True):
        """Take screenshot and save to file"""
        if not self.page:
            raise Exception("No page loaded")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        await self.page.screenshot(path=filename, full_page=full_page)
        return {"filename": filename}
        
    async def get_page_metrics(self):
        """Get performance metrics"""
        if not self.page:
            raise Exception("No page loaded")
            
        # Get performance timing
        metrics = await self.page.evaluate("""() => {
            const timing = performance.timing;
            const navigation = performance.navigation;
            
            return {
                // Page load times
                domContentLoaded: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                loadComplete: timing.loadEventEnd - timing.loadEventStart,
                domInteractive: timing.domInteractive - timing.domLoading,
                
                // Network times
                dns: timing.domainLookupEnd - timing.domainLookupStart,
                tcp: timing.connectEnd - timing.connectStart,
                request: timing.responseStart - timing.requestStart,
                response: timing.responseEnd - timing.responseStart,
                
                // Overall metrics
                totalLoadTime: timing.loadEventEnd - timing.navigationStart,
                redirectCount: navigation.redirectCount,
                
                // Memory (if available)
                memory: performance.memory ? {
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                } : null
            };
        }""")
        
        return metrics
        
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            
        # Clear logs
        self.console_logs = []
        self.network_errors = []
        self.page_errors = []
        
        return {"status": "Browser closed"}

# MCP Server setup
async def main():
    debugger = PlaywrightDebugger()
    server = Server("playwright-debugger")
    
    # Register tools
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="start_browser",
                description="Start browser for debugging",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "headless": {"type": "boolean", "default": False},
                        "browser_type": {"type": "string", "enum": ["chromium", "firefox", "webkit"], "default": "chromium"}
                    }
                }
            ),
            Tool(
                name="navigate",
                description="Navigate to URL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "wait_until": {"type": "string", "enum": ["domcontentloaded", "networkidle", "load"], "default": "domcontentloaded"}
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="get_console_logs",
                description="Get browser console logs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type_filter": {"type": "string", "enum": ["log", "error", "warning", "info", "debug"]},
                        "clear_after": {"type": "boolean", "default": False}
                    }
                }
            ),
            Tool(
                name="get_all_errors",
                description="Get all errors (console, page, network)",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="execute_script",
                description="Execute JavaScript in page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script": {"type": "string"}
                    },
                    "required": ["script"]
                }
            ),
            Tool(
                name="take_screenshot",
                description="Take screenshot of page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "full_page": {"type": "boolean", "default": True}
                    }
                }
            ),
            Tool(
                name="get_page_metrics",
                description="Get page performance metrics",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="close_browser",
                description="Close browser and cleanup",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            if name == "start_browser":
                result = await debugger.start_browser(**arguments)
            elif name == "navigate":
                result = await debugger.navigate(**arguments)
            elif name == "get_console_logs":
                result = await debugger.get_console_logs(**arguments)
            elif name == "get_all_errors":
                result = await debugger.get_errors()
            elif name == "execute_script":
                result = await debugger.execute_script(**arguments)
            elif name == "take_screenshot":
                result = await debugger.take_screenshot(**arguments)
            elif name == "get_page_metrics":
                result = await debugger.get_page_metrics()
            elif name == "close_browser":
                result = await debugger.close_browser()
            else:
                result = {"error": f"Unknown tool: {name}"}
                
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Run server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="playwright-debugger",
                server_version="1.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())