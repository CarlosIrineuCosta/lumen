# Portfolio Fix Instructions

## The Issue
The portfolio view is calling the wrong endpoint. The frontend is sending requests to:
`/photos/user/${this.user?.uid}?portfolio_only=true`

But it should be calling:
`/photos/my-photos?portfolio_only=true`

## Manual Fix Required

### File: `L:\Storage\NVMe\projects\wasenet\opusdev\js\app.js`
### Line: 326

**CHANGE THIS LINE:**
```javascript
return `/photos/user/${this.user?.uid}?portfolio_only=true`;
```

**TO THIS:**
```javascript
return '/photos/my-photos?portfolio_only=true';
```

## How to Apply the Fix

1. Open the file `L:\Storage\NVMe\projects\wasenet\opusdev\js\app.js` in your text editor
2. Go to line 326 (or search for "portfolio_only=true")
3. Replace the line as shown above
4. Save the file
5. Refresh your browser (Ctrl+F5 for hard refresh)
6. Click on Portfolio tab - it should now show your portfolio photos!

## Why This Works

- The backend endpoint `/photos/my-photos` automatically uses the current user's Firebase UID
- It accepts the `portfolio_only=true` parameter to filter for portfolio photos
- The old endpoint `/photos/user/{user_id}` was expecting a different ID format

## Testing

After making the change:
1. Refresh the page
2. Click on the Portfolio tab
3. You should see photos that are marked with `is_portfolio = true` in the database

If you still see no photos after this fix, then we need to check:
1. Are there actually photos marked as portfolio in the database?
2. Is the user ID matching correctly?

Let me know once you've made this change and whether the portfolio photos appear!
