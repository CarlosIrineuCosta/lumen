# Lumen Project - Error Handling Strategies

This document records the rationale and resolution steps for complex bugs encountered during development. It serves as a persistent memory to avoid repeating lengthy debugging sessions.

```json
[
  {
    "strategy_id": "EHS-001",
    "title": "Diagnosing 500 Internal Server Errors Masquerading as CORS Failures",
    "stack": ["FastAPI", "Pydantic", "SQLAlchemy", "Uvicorn"],
    "error_signature": {
      "browser_console": "Access to fetch at '...' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.",
      "network_tab": "GET http://... 500 (Internal Server Error)",
      "server_log": "Clean logs, no exceptions recorded despite the 500 error."
    },
    "symptoms": [
      "User cannot log in or view profile data.",
      "API requests fail with a CORS error in the browser, but the network status is 500.",
      "Restarting the server with correct CORS settings does not solve the issue."
    ],
    "investigation_steps": [
      {
        "step": 1,
        "action": "Verify basic CORS and server configuration.",
        "rationale": "Rule out the most common causes first.",
        "result": "CORS settings in `main.py` and `.env` were correct. Server was confirmed to be running on the correct host and port. The problem persisted."
      },
      {
        "step": 2,
        "action": "Hypothesize a hidden runtime error.",
        "rationale": "A 500 status code means the server is running but crashing during the request. The lack of logs suggests the exception is unhandled at a level before the standard logger can report it.",
        "result": "This became the leading theory."
      },
      {
        "step": 3,
        "action": "Install a temporary, high-level debugging middleware in `main.py`.",
        "rationale": "To guarantee that any unhandled exception, anywhere in the request-response cycle, would be caught and logged.",
        "code_snippet": "@app.middleware(\"http\")\nasync def log_exceptions_middleware(request: Request, call_next):\n    try:\n        return await call_next(request)\n    except Exception as e:\n        logger.error(f\"Unhandled exception: {e}\\n{traceback.format_exc()}\")\n        return JSONResponse(status_code=500, content={"detail": \"Internal Server Error\"})",
        "result": "This was the key step. It immediately revealed the true error in the browser console and logs."
      }
    ],
    "root_cause": {
      "description": "A Pydantic validation error was occurring during the serialization of the API response. A database record had a `photography_styles` field. The `UserProfileFull` response model expected this field to be a `list`. When Pydantic tried to serialize the `None` value as a list, it threw an exception.",
      "reason_for_confusion": "This exception happened after the main endpoint logic but before the CORS middleware could attach the `Access-Control-Allow-Origin` header to the outgoing response. The server crashed, sent a generic 500 error, and the browser, seeing no CORS header, reported a CORS failure."
    },
    "solution": {
      "description": "Made the data serialization logic in `user_service.py` more defensive to handle potentially corrupt or `null` data from the database.",
      "file_path": "backend/app/services/user_service.py",
      "method": "_user_to_profile_dict",
      "code_change": "Changed `\"photography_styles\": user.profile_data.get(\"photography_styles\", [])` to `\"photography_styles\": (user.profile_data or {}).get(\"photography_styles\") or []`. This ensures the value is always a list, even if `profile_data` or the `photography_styles` key itself is `None`."
    },
    "lesson_learned": "When a 500 error appears as a CORS issue and server logs are clean, the problem is likely an unhandled exception during response serialization. A temporary, global exception-catching middleware is the most effective tool for diagnosis."
  },
  {
    "strategy_id": "EHS-002",
    "title": "Upload System 422 Error - Field Name Mismatch Between Frontend and Backend",
    "stack": ["FilePond", "FastAPI", "Multipart Forms", "JavaScript"],
    "error_signature": {
      "browser_console": "POST http://100.106.201.33:8080/api/v1/photos/upload 422 (Unprocessable Entity)",
      "server_response": "{\"detail\":[{\"type\":\"missing\",\"loc\":[\"body\",\"file\"],\"msg\":\"Field required\",\"input\":null}]}",
      "frontend_logs": "FilePond upload error: Field required for 'file'",
      "auth_status": "Auth token: Present, User authenticated"
    },
    "symptoms": [
      "Upload button works, modal opens correctly",
      "File selection works, metadata form populated", 
      "Authentication successful, token present",
      "Upload fails with 422 error claiming missing 'file' field",
      "Multiple error toasts appearing (cascading error handlers)"
    ],
    "investigation_steps": [
      {
        "step": 1,
        "action": "MISTAKE: Assumed authentication issues and added token debugging",
        "rationale": "422 errors often indicate auth problems",
        "result": "Wasted time - authentication was working perfectly. Token was present and valid."
      },
      {
        "step": 2, 
        "action": "MISTAKE: Fixed API endpoint URL without checking if it was actually wrong",
        "rationale": "Previous debugging showed endpoint issues",
        "result": "API endpoint was already correct (/api/v1/photos/upload). No change needed."
      },
      {
        "step": 3,
        "action": "MISTAKE: Added error handling improvements before finding root cause",
        "rationale": "Trying to improve user experience", 
        "result": "Fixed cascading errors but didn't solve the core 422 issue."
      },
      {
        "step": 4,
        "action": "CRITICAL INSIGHT: User demanded systematic analysis using SequentialThinking",
        "rationale": "After 2+ hours of random fixes, systematic approach was required",
        "result": "Sequential analysis revealed the field name mismatch in under 10 minutes."
      },
      {
        "step": 5,
        "action": "Checked backend API requirements vs frontend field names",
        "rationale": "Compare what's sent vs what's expected",
        "result": "FOUND: Backend expects 'file' field, frontend sends 'filepond' field name."
      }
    ],
    "root_cause": {
      "description": "FilePond HTML input had name='filepond' but FastAPI backend expected name='file'. The multipart form data field names must match exactly.",
      "specific_files": {
        "frontend": "frontend/js/modules/upload.js line 49: <input name='filepond'>",
        "backend": "backend/app/api/endpoints/photos.py line 47: file: UploadFile = File(...)"
      },
      "why_missed_initially": "Didn't systematically check the complete request/response flow. Made assumptions about authentication and API endpoints instead of verifying field-level requirements."
    },
    "solution": {
      "description": "Changed HTML input field name from 'filepond' to 'file' to match backend expectation",
      "file_path": "frontend/js/modules/upload.js",
      "line_number": 49,
      "code_change": "<input type='file' id='photo-upload-input' name='file' multiple>",
      "time_to_fix": "30 seconds once root cause identified"
    },
    "critical_mistakes_made": [
      "❌ Didn't check API documentation/requirements first",
      "❌ Didn't trace complete data flow from UI to database", 
      "❌ Made random incremental fixes instead of systematic analysis",
      "❌ Assumed authentication issues without evidence",
      "❌ Didn't use SequentialThinking tool for complex debugging",
      "❌ Spent 2+ hours on what was a 1-line fix",
      "❌ Ignored user's demand for systematic approach initially"
    ],
    "lesson_learned": "For any API integration error: (1) Check exact field requirements in backend first, (2) Trace complete data flow systematically, (3) Use SequentialThinking for complex bugs, (4) Don't make assumptions - verify each step. A 422 'Field required' error means field names don't match exactly.",
    "time_wasted": "3+ hours on a single-line fix", 
    "correct_debugging_order": [
      "1. Read backend API endpoint requirements",
      "2. Check frontend request format matches requirements", 
      "3. Verify field names match exactly",
      "4. Test with corrected field names",
      "5. Only then investigate auth, endpoints, etc."
    ]
  }
]
```