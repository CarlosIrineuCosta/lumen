# /server - Start Backend Server

Starts the Lumen backend server using the mandatory startup script.

## Usage
```
/server
```

## What it does
- Uses the mandatory `./scripts/start-server.sh` script
- Loads environment variables properly from backend/.env
- Tests database connection before starting
- Prevents recurring database connection issues

## Important
This command MUST be used instead of running uvicorn directly to avoid the "fe_sendauth: no password supplied" error that occurs when .env variables aren't loaded properly.