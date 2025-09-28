# Auth0 Setup Guide for TravelMaster AI

## Overview
This guide walks you through setting up Auth0 authentication for the TravelMaster AI application following the secure Authorization Code Flow with PKCE pattern.

## Phase 1: Auth0 Configuration

### 1. Create Auth0 Account
1. Go to [Auth0](https://auth0.com/) and sign up/login
2. Create a new tenant (domain) if needed

### 2. Create API (Backend Configuration)
1. Go to **Applications > APIs** in Auth0 Dashboard
2. Click **Create API**
3. Set:
   - **Name**: `TravelMaster API`
   - **Identifier**: `https://travelmaster-api` (this is your audience)
   - **Signing Algorithm**: `RS256`
4. Click **Create**

### 3. Create Application (Frontend Configuration)
1. Go to **Applications > Applications**
2. Click **Create Application**
3. Set:
   - **Name**: `TravelMaster Frontend`
   - **Application Type**: `Single Page Application`
4. Click **Create**

### 4. Configure Application Settings
1. In your new application, go to **Settings** tab
2. Configure:
   - **Allowed Callback URLs**: 
     ```
     http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500
     ```
   - **Allowed Logout URLs**: 
     ```
     http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500
     ```
   - **Allowed Web Origins**: 
     ```
     http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500
     ```
   - **Allowed Origins (CORS)**: 
     ```
     http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500
     ```
3. **Save Changes**

## Phase 2: Environment Configuration

### 1. Copy Environment File
```bash
cp .env.example .env
```

### 2. Update .env File
Edit `.env` with your Auth0 credentials:

```bash
# Your Auth0 domain (found in Application Settings)
AUTH0_DOMAIN=your-tenant-name.auth0.com

# Your API identifier (from API setup)
AUTH0_AUDIENCE=https://travelmaster-api
```

### 3. Update Frontend Configuration
Edit `frontend/index.html` around line 140:

```javascript
// Replace these with your actual Auth0 credentials
const AUTH0_DOMAIN = 'your-tenant-name.auth0.com';
const AUTH0_CLIENT_ID = 'your-client-id-from-app-settings';
const AUTH0_AUDIENCE = 'https://travelmaster-api';
```

## Phase 3: Testing Authentication

### 1. Install Dependencies
```bash
# Install PyJWT for backend token validation
pip install PyJWT[crypto] requests
```

### 2. Start the Application
```bash
# Start the backend
python src/travel_agent.py

# Open frontend in browser
open http://localhost:8000
```

### 3. Test Authentication Flow
1. You should see an authentication screen
2. Click **Sign In** or **Create Account**
3. Complete Auth0 Universal Login
4. Should redirect back to the application
5. You should see your user info in the header

## Phase 4: Features Enabled by Authentication

### Protected Endpoints
- `/api/my-trips` - Get user's saved trips
- `/api/save-trip` - Save trip itinerary

### Enhanced Features
- **Personalized Experience**: User-specific trip history
- **Secure Data**: Trip data associated with user accounts
- **User Management**: Profile information and preferences

## Troubleshooting

### Common Issues

1. **"Auth0 not configured" message**
   - Check that `AUTH0_DOMAIN` and `AUTH0_CLIENT_ID` are set correctly
   - Verify domain format: `tenant-name.auth0.com` (no https://)

2. **Callback URL errors**
   - Ensure all callback URLs are added to Auth0 app settings
   - Check for typos in URLs
   - Make sure URLs match exactly (including port numbers)

3. **CORS errors**
   - Add your domain to "Allowed Origins (CORS)" in Auth0
   - Check browser console for specific CORS error details

4. **Token validation errors**
   - Verify `AUTH0_AUDIENCE` matches your API identifier exactly
   - Check that API is created and identifier is correct

### Demo Mode
If Auth0 is not configured, the app automatically falls back to demo mode where:
- Authentication is bypassed
- All endpoints work without tokens
- User-specific features use mock data

## Production Deployment

### Additional Security
For production, consider adding:
- Role-based access control (RBAC)
- Rate limiting
- Database persistence for user data
- SSL/HTTPS enforcement
- Environment-specific configurations

### Environment Variables
Ensure these are set in production:
```bash
AUTH0_DOMAIN=your-production-domain.auth0.com
AUTH0_AUDIENCE=https://your-production-api
SECRET_KEY=strong-random-secret-key
DEBUG=False
```

## Next Steps

1. **Customize User Experience**: Add user profile management
2. **Add Roles**: Implement premium/standard user tiers
3. **Database Integration**: Persist user trips and preferences
4. **Analytics**: Track user behavior and trip patterns
5. **Social Login**: Enable Google, Facebook, etc. login options