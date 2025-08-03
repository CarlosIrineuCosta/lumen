# Firebase Authentication Setup for Tailscale Development

## Issue: Domain Authorization Required

The Firebase popup authentication fails because the Tailscale domain `100.106.201.33:8001` is not authorized in the Firebase Console.

## Solution Options

### Option 1: Authorize Domain in Firebase Console (Recommended)

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select Project**: `lumen-photo-app-20250731`
3. **Navigate to Authentication**:
   - Click "Authentication" in the left sidebar
   - Click "Settings" tab
   - Click "Authorized domains"
4. **Add Authorized Domain**:
   - Click "Add domain"
   - Enter: `100.106.201.33`
   - Save changes

### Option 2: Use Localhost for Development

1. **Update your hosts file** (temporary):
   ```bash
   echo "100.106.201.33 lumen-local.dev" >> /etc/hosts
   ```
2. **Access via**: http://lumen-local.dev:8001/lumen-app.html
3. **Authorize domain**: `lumen-local.dev` in Firebase Console

### Option 3: Use Redirect Authentication (Already Implemented)

The app now automatically falls back to redirect authentication when popup fails:
- Popup attempts first (faster, better UX)
- Redirect used as fallback (works with unauthorized domains)
- Automatic error handling and user feedback

## Current Implementation

The authentication now includes:

1. **Smart Fallback**: Tries popup first, uses redirect if domain unauthorized
2. **Error Handling**: Clear messages for different error types
3. **Automatic Retry**: Attempts redirect after popup failures
4. **Debug Information**: Console logs for troubleshooting

## Testing

1. **Open**: http://100.106.201.33:8001/lumen-app.html
2. **Click**: "Sign In with Google"
3. **Expected Behavior**:
   - If domain authorized: Popup opens and authentication completes
   - If domain unauthorized: Automatic redirect to Google OAuth
   - User returns to app after authentication

## Debug Tools

Use the debug page for detailed testing:
- **URL**: http://100.106.201.33:8001/auth-debug.html
- **Features**: 
  - Test popup and redirect methods separately
  - Check Firebase configuration
  - View detailed error messages
  - Monitor authentication state

## Firebase Project Details

- **Project ID**: lumen-photo-app-20250731
- **Auth Domain**: lumen-photo-app-20250731.firebaseapp.com
- **Current Authorized Domains**: 
  - localhost
  - lumen-photo-app-20250731.firebaseapp.com
  - (Need to add: 100.106.201.33)

## Next Steps

1. **Authorize the Tailscale domain** in Firebase Console for best experience
2. **Test authentication** with both popup and redirect methods
3. **Complete user profile setup** flow
4. **Connect to backend API** for user data persistence