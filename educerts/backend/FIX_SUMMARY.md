# Fix Summary: 401 Unauthorized Error

## Problem Identified
You're getting 401 Unauthorized errors when trying to delete certificates from the frontend.

## Root Cause
The authentication cookie is not being sent from the browser, or the session has expired.

## What I Fixed

### 1. Enhanced Error Messages
Updated the backend authentication to provide more detailed error messages:
- Now shows exactly why authentication failed
- Logs debug information to help troubleshoot
- Provides clearer error messages to the frontend

### 2. Created Diagnostic Tools
- `test_auth.py` - Tests authentication flow from Python
- `TROUBLESHOOTING_401.md` - Complete troubleshooting guide

### 3. Verified Backend Works
Ran tests and confirmed:
- ✅ Login works correctly
- ✅ Authentication cookie is set properly
- ✅ Admin permissions are checked correctly
- ✅ Bulk-delete endpoint is accessible with proper auth

## Solution for You

The backend is working correctly. You need to fix the frontend session:

### Quick Fix (Choose One):

**Option 1: Log Out and Back In**
1. Go to your frontend (http://localhost:3000)
2. Click logout
3. Log in again with admin credentials
4. Try deleting certificates again

**Option 2: Clear Browser Cookies**
1. Open DevTools (F12)
2. Go to Application → Cookies
3. Delete all cookies for localhost:3000 and localhost:8000
4. Refresh the page
5. Log in again
6. Try deleting certificates again

**Option 3: Use Incognito/Private Window**
1. Open a new incognito/private browser window
2. Go to http://localhost:3000
3. Log in with admin credentials
4. Try deleting certificates

## Why This Happens

The authentication uses HttpOnly cookies that expire after 30 minutes. If:
- You logged in a while ago → Session expired
- You cleared cookies → Need to log in again
- You're using a different browser → Need to log in there too
- Backend was restarted → Old sessions are invalid

## Verification

After logging in again, you should be able to:
1. Select certificates
2. Click "Delete Documents"
3. See the confirmation modal
4. Successfully delete the certificates

## Prevention

To avoid this in the future:
- Log in fresh when starting a work session
- If you've been idle for 30+ minutes, log in again
- Keep the same browser tab open
- Don't clear cookies while working

## Technical Details

The authentication flow:
```
Browser → Login → Backend sets cookie (30 min expiry)
Browser → API request → Sends cookie automatically
Backend → Validates cookie → Checks admin status → Allows operation
```

The 401 error means the cookie is missing or expired at step 2.

## Still Having Issues?

If you're still getting 401 errors after logging in:

1. Check browser console (F12 → Console) for errors
2. Check Network tab (F12 → Network) to see if cookies are being sent
3. Make sure you're logging in as an admin user
4. Verify your user is admin: `python list_users.py`
5. Check backend logs for "DEBUG AUTH" messages

## Need More Help?

Read the full troubleshooting guide:
```bash
cat TROUBLESHOOTING_401.md
```

Or run the diagnostic test:
```bash
python test_auth.py
```
