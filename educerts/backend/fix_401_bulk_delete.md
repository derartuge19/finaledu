# Fix for 401 Unauthorized Error on Bulk Delete

## Problem
You're getting `401 Unauthorized` when trying to delete certificates, even when logged in.

## Root Causes
1. **Session Expired**: Your login session has expired
2. **Wrong Credentials**: Using incorrect admin username/password
3. **Cookie Issues**: Browser not sending authentication cookies properly
4. **CORS Issues**: Cross-origin cookie problems

## Solutions

### Solution 1: Re-login (Most Common)
1. **Log out** from the application completely
2. **Clear browser cookies** for localhost
3. **Log back in** with correct admin credentials
4. **Try bulk delete again**

### Solution 2: Check Admin Credentials
Make sure you're using the correct admin credentials:
- Username: Check your database for the admin user
- Password: Make sure it's correct

### Solution 3: Browser Cookie Fix
1. Open **Browser DevTools** (F12)
2. Go to **Application** tab
3. Find **Cookies** for localhost:8000
4. **Delete all** localhost:8000 cookies
5. **Refresh and login again**

### Solution 4: Check User is Admin
Verify your user has `is_admin = True` in the database:

```sql
SELECT name, email, is_admin FROM users WHERE name = 'your_username';
```

### Solution 5: Frontend Session Fix
If the issue persists, the frontend might not be sending cookies properly:

1. **Check browser console** for CORS errors
2. **Ensure** `withCredentials: true` is in the API call
3. **Try using** `localhost:3000` instead of `127.0.0.1:3000`

## Debug Steps

1. **Open browser DevTools** (F12)
2. **Go to Network tab**
3. **Try bulk delete**
4. **Check the request**:
   - Is the `access_token` cookie being sent?
   - What's the exact error response?
   - Is the status 401 or 403?

## Quick Test

Use the browser console to test authentication:

```javascript
// Check if user is logged in
fetch('/api/user/me', {credentials: 'include'})
  .then(r => r.json())
  .then(user => console.log('Current user:', user))
  .catch(e => console.error('Auth error:', e));
```

## Backend Debug

If you need to debug the backend, add these prints to `main.py`:

```python
# In get_current_user_from_cookie function
print(f"DEBUG: Received access_token: {access_token}")
print(f"DEBUG: Decoded payload: {payload}")
print(f"DEBUG: User found: {user}")
print(f"DEBUG: User is_admin: {user.is_admin if user else 'No user'}")
```

## Most Likely Fix
**90% of the time, this is just a session expiration.**

1. Log out
2. Clear cookies  
3. Log back in
4. Try bulk delete again

If it still doesn't work, check your admin credentials in the database.
