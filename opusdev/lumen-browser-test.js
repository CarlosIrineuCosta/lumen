// Test script for browser console monitoring with Lumen app
// This demonstrates how Claude can use Playwright MCP to debug your app

async function testLumenConsoleMonitoring() {
    // Step 1: Start the browser (visible for debugging)
    await start_browser({ headless: false, browser_type: "chromium" });
    
    // Step 2: Navigate to your Lumen dev app
    await browser_navigate({ url: "http://localhost:8080" });
    
    // Step 3: Wait a moment for the page to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Step 4: Get all console logs
    const allLogs = await get_console_logs({ type: "all" });
    console.log("All console logs:", allLogs);
    
    // Step 5: Check specifically for errors
    const errors = await get_console_logs({ type: "error" });
    if (errors.length > 0) {
        console.error("Found errors in console:");
        errors.forEach(error => {
            console.error(`- ${error.text}`);
            if (error.location) {
                console.error(`  at ${error.location}`);
            }
        });
    }
    
    // Step 6: Check for network errors (404s, failed requests)
    const allErrors = await get_all_errors();
    console.log("Total errors found:", allErrors.total_errors);
    
    if (allErrors.network_errors.length > 0) {
        console.log("Network errors:");
        allErrors.network_errors.forEach(err => {
            console.log(`- ${err.type}: ${err.url} (${err.status || err.failure})`);
        });
    }
    
    // Step 7: Check authentication status via console
    const authCheck = await execute_script({
        script: `
            // Check if user is authenticated
            const authToken = localStorage.getItem('auth_token');
            const userEmail = localStorage.getItem('user_email');
            console.log('Auth status:', authToken ? 'Logged in' : 'Not logged in');
            console.log('User:', userEmail || 'None');
            return {
                authenticated: !!authToken,
                user: userEmail
            };
        `
    });
    console.log("Authentication status:", authCheck.result);
    
    // Step 8: Get performance metrics
    const metrics = await get_page_metrics();
    console.log("Page load time:", metrics.totalLoadTime + "ms");
    console.log("DOM ready time:", metrics.domContentLoaded + "ms");
    
    // Step 9: Take a screenshot if errors were found
    if (allErrors.total_errors > 0) {
        const screenshot = await take_screenshot({ full_page: true });
        console.log("Screenshot saved:", screenshot.filename);
    }
    
    // Step 10: Try to trigger a specific action (e.g., click upload button)
    await playwright_click({ selector: 'button[data-test="upload"]' });
    
    // Step 11: Check for new errors after action
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newErrors = await get_console_logs({ type: "error", clear_after: true });
    if (newErrors.length > 0) {
        console.error("New errors after clicking upload:", newErrors);
    }
    
    // Step 12: Close browser when done
    // await close_browser();
    // Keep browser open for manual inspection if needed
}

// Common Lumen-specific checks
const lumenDebugChecks = {
    // Check Firebase authentication
    checkFirebaseAuth: `
        if (typeof firebase !== 'undefined') {
            const user = firebase.auth().currentUser;
            return {
                initialized: true,
                user: user ? user.email : null,
                uid: user ? user.uid : null
            };
        }
        return { initialized: false };
    `,
    
    // Check API connectivity
    checkAPIConnection: `
        fetch('http://localhost:8080/api/v1/auth/status')
            .then(r => {
                console.log('API Status:', r.status);
                return r.json();
            })
            .then(data => console.log('API Response:', data))
            .catch(err => console.error('API Error:', err));
    `,
    
    // Check for common JavaScript errors
    checkCommonErrors: `
        const errors = [];
        
        // Check if required globals exist
        if (typeof firebase === 'undefined') errors.push('Firebase not loaded');
        if (typeof fetch === 'undefined') errors.push('Fetch API not available');
        
        // Check localStorage availability
        try {
            localStorage.setItem('test', 'test');
            localStorage.removeItem('test');
        } catch(e) {
            errors.push('localStorage not available');
        }
        
        // Check for CORS issues (common with API calls)
        const img = new Image();
        img.onerror = () => console.error('CORS or network issue detected');
        img.src = 'http://localhost:8080/favicon.ico';
        
        return errors;
    `
};

// Instructions for use:
// 1. Make sure Playwright MCP is configured in Claude Desktop
// 2. Start your Lumen backend: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
// 3. Start your Lumen frontend: cd frontend && python3 -m http.server 8000
// 4. Ask Claude to run these browser tests
// 5. Claude will report all console errors, network failures, and authentication issues
