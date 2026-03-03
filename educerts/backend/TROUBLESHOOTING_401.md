# Troubleshooting 401 Unauthorized Errors

## Problem
Getting "401 Unauthorized" errors when trying to delete certificates from the frontend.

## Root Cause
The 401 error means the authentication cookie is not being sent or is invalid. This happens when:

1. **Not logged in** - You need to be logged in as an admin
2. **Session expired** - Your login session has timed out
3. **Not an admin** - Your user account doesn't have admin privileges
4. **Cookie issues** - Browser not sending cookies properly

## Quick Fix

### Step 1: Verify Your Admin Status

Run this test script:

```bash
cd educerts/backend
python test_auth.py
```

**Update the credentials in `test_auth.py` first:**
```python
login_data = {
    "username": "admin",  # Your admin username
    "password": "admin123"  # Your admin password
}
```

### Step 2: Check Your User Account

```bash
cd educerts/backend
python list_users.py
```

Make sure your user has `Admin: True`.

### Step 3: Frontend Fixes

If you're logged in but still getting 401 errors:

1. **Log out and log back in**
   - Go to the login page
   - Log in with admin credentials
   - Try deleting again

2. **Clear browser cookies**
   - Open DevTools (F12)
   - Go to Application → Cookies
   - Delete all cookies for localhost:3000 and localhost:8000
   - Log in again

3. **Check browser console**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for CORS errors or cookie warnings

### Step 4: Verify Backend is Running

Make sure the backend server is running with the updated code:

```bash
cd educerts/backend
python main.py
```

You should see debug messages like:
```
DEBUG AUTH: User authenticated: admin (admin=True)
```

## Common Issues

### Issue 1: "Not an admin" error

**Solution:** Promote your user to admin:

```bash
cd educerts/backend
python promote_admin.py
```

Enter your username when prompted.

### Issue 2: Cookie not being sent

**Symptoms:**
- Backend logs show: `DEBUG AUTH: No access_token cookie found`
- Frontend works for other operations but not delete

**Solution:**
1. Check that `withCredentials: true` is set in the API call (already done)
2. Verify CORS is configured correctly (already done)
3. Make sure you're using the same domain for frontend and backend
4. Try using `localhost` instead of `127.0.0.1` (or vice versa)

### Issue 3: Session expired

**Symptoms:**
- Was working before, now getting 401
- Backend logs show: `DEBUG AUTH: Failed to decode access token`

**Solution:**
- Log out and log back in
- Sessions expire after 30 minutes by default

## Testing the Fix

After applying fixes, test in this order:

1. **Backend test:**
   ```bash
   python test_auth.py
   ```
   Should show: ✅ ALL TESTS PASSED!

2. **Frontend test:**
   - Open browser
   - Log in as admin
   - Go to Certificates page
   - Select a certificate
   - Click "Delete Documents"
   - Should work without 401 error

## Still Not Working?

Check the backend logs for detailed error messages:

```bash
cd educerts/backend
# Look at the terminal where main.py is running
# You should see DEBUG AUTH messages
```

If you see:
- `DEBUG AUTH: No access_token cookie found` → Cookie not being sent
- `DEBUG AUTH: Failed to decode access token` → Session expired, log in again
- `DEBUG AUTH: User not found in database` → User doesn't exist
- `Admin access required. Current user 'X' is not an admin` → User is not admin

## Prevention

To avoid this in the future:

1. **Always log in as admin** when managing certificates
2. **Refresh your session** if you've been idle for a while
3. **Use the same browser tab** - don't open multiple tabs
4. **Check admin status** before performing admin operations

## Technical Details

The authentication flow:

1. User logs in → Backend sets HttpOnly cookie with JWT token
2. Frontend makes API request → Browser automatically sends cookie
3. Backend validates cookie → Extracts user info
4. Backend checks admin status → Allows/denies operation

The 401 error occurs at step 3 when the cookie is missing or invalid.
