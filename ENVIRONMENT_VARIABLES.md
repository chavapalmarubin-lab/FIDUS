# FIDUS Investment Platform - Environment Variables Documentation

## Overview
This document describes all the environment variables required for the FIDUS investment management platform. These variables configure database connections, Google integrations, JWT authentication, and frontend/backend communication.

## Required Environment Variables

### Database Configuration

#### `DB_NAME`
- **Value**: `fidus-invest-test_databa`
- **Description**: MongoDB database name for the FIDUS application
- **Required**: Yes
- **Example**: `fidus-invest-production`

#### `MONGO_URL`
- **Value**: `mongodb+srv://fidus-in...`
- **Description**: Complete MongoDB connection string including authentication
- **Required**: Yes
- **Format**: `mongodb+srv://username:password@cluster.mongodb.net/database`
- **Security**: Keep this credential secure and never expose publicly

### Frontend/Backend Communication

#### `FRONTEND_URL`
- **Value**: `https://fidus-invest.emergent.host`
- **Description**: Base URL for the React frontend application
- **Required**: Yes
- **Used By**: Backend for CORS configuration and OAuth redirects

#### `REACT_APP_BACKEND_URL`
- **Value**: `https://fidus-invest.emergent.host`
- **Description**: Backend API URL used by the React frontend
- **Required**: Yes
- **Note**: Must be prefixed with `REACT_APP_` to be available in React

### Google OAuth & API Integration

#### `GOOGLE_CLIENT_ID`
- **Value**: `909926639154-r3v0ka9...`
- **Description**: Google OAuth 2.0 client ID for authentication
- **Required**: Yes
- **Obtained From**: Google Cloud Console > APIs & Services > Credentials

#### `GOOGLE_CLIENT_SECRET`
- **Value**: `GOCSPX-HQ3ceZZGfnB...`
- **Description**: Google OAuth 2.0 client secret for authentication
- **Required**: Yes
- **Security**: Keep this secret secure and never expose in frontend code

#### `GOOGLE_OAUTH_REDIRECT_URI`
- **Value**: `https://fidus-invest.emergent.host`
- **Description**: Authorized redirect URI for Google OAuth flow
- **Required**: Yes
- **Note**: Must match exactly with Google Cloud Console configuration

#### `GOOGLE_SERVICE_ACCOUNT_KEY`
- **Value**: `{"type":"service_accou...`
- **Description**: Google Service Account JSON key for API access
- **Required**: Yes for Google Workspace integration
- **Format**: Complete JSON service account key
- **Used For**: Gmail, Calendar, Drive API access

### Authentication & Security

#### `JWT_SECRET_KEY`
- **Value**: `your-jwt-secret-key-her...`
- **Description**: Secret key for signing JWT tokens
- **Required**: Yes
- **Security**: Use a strong, randomly generated secret
- **Length**: Minimum 32 characters recommended

### Development Configuration

#### `WDS_SOCKET_PORT`
- **Value**: `443`
- **Description**: WebSocket port for webpack dev server
- **Required**: For development with HTTPS
- **Default**: `443` for HTTPS environments

## Environment File Structure

### Backend Environment (.env)
Create `/app/backend/.env` with the following structure:

```bash
# Database Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/fidus-invest
DB_NAME=fidus-invest-production

# Google OAuth Configuration
GOOGLE_CLIENT_ID=909926639154-r3v0ka9...
GOOGLE_CLIENT_SECRET=GOCSPX-HQ3ceZZGfnB...
GOOGLE_OAUTH_REDIRECT_URI=https://fidus-invest.emergent.host
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}

# JWT Authentication
JWT_SECRET_KEY=your-strong-jwt-secret-key-here-minimum-32-characters

# Frontend Configuration
FRONTEND_URL=https://fidus-invest.emergent.host
```

### Frontend Environment (.env)
Create `/app/frontend/.env` with:

```bash
# Backend API Configuration
REACT_APP_BACKEND_URL=https://fidus-invest.emergent.host

# Development Configuration (if needed)
WDS_SOCKET_PORT=443
```

## Security Best Practices

### 1. Environment Variable Security
- **Never commit** `.env` files to version control
- Add `.env` to `.gitignore` files
- Use different values for development, staging, and production
- Rotate secrets regularly (JWT keys, database passwords)

### 2. Google Credentials Security
- Keep `GOOGLE_CLIENT_SECRET` and `GOOGLE_SERVICE_ACCOUNT_KEY` secure
- Only store service account keys in backend environment
- Never expose Google credentials in frontend code
- Regularly review Google Cloud Console access logs

### 3. Database Security
- Use strong database passwords
- Restrict MongoDB network access
- Enable MongoDB authentication
- Use connection encryption (SSL/TLS)

## Deployment Configuration

### Production Deployment
For production deployment, ensure:

1. **HTTPS URLs**: All URLs should use `https://` protocol
2. **Strong Secrets**: Generate new, strong secrets for JWT and database
3. **Google OAuth**: Configure production redirect URIs in Google Console
4. **Database**: Use production MongoDB cluster with proper security

### Environment-Specific Values
- **Development**: Use `localhost` URLs and test credentials
- **Staging**: Use staging URLs and separate database
- **Production**: Use production URLs and production-grade security

## Troubleshooting

### Common Issues

#### 1. Google OAuth Errors
- **redirect_uri_mismatch**: Ensure `GOOGLE_OAUTH_REDIRECT_URI` matches Google Console
- **invalid_client**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

#### 2. Database Connection Issues
- **Connection timeout**: Check `MONGO_URL` format and network access
- **Authentication failed**: Verify username/password in connection string

#### 3. Frontend/Backend Communication
- **CORS errors**: Ensure `FRONTEND_URL` matches actual frontend domain
- **API not found**: Verify `REACT_APP_BACKEND_URL` is correct and accessible

### Validation Commands
Test environment variables with these commands:

```bash
# Test MongoDB connection
node -e "const mongoose = require('mongoose'); mongoose.connect(process.env.MONGO_URL).then(() => console.log('MongoDB Connected')).catch(err => console.error('MongoDB Error:', err));"

# Test JWT secret
node -e "const jwt = require('jsonwebtoken'); const token = jwt.sign({test: 'data'}, process.env.JWT_SECRET_KEY); console.log('JWT Test:', jwt.verify(token, process.env.JWT_SECRET_KEY));"

# Test Google OAuth config
curl "https://oauth2.googleapis.com/tokeninfo?client_id=${GOOGLE_CLIENT_ID}"
```

## Production Checklist

Before deploying to production, verify:

- [ ] All environment variables are set
- [ ] Google OAuth redirect URIs are configured
- [ ] MongoDB connection is secure and accessible
- [ ] JWT secret is strong and unique
- [ ] HTTPS is enabled for all URLs
- [ ] Service account permissions are minimal
- [ ] Database backups are configured
- [ ] Environment variables are not logged
- [ ] Access logs are monitored

## Contact & Support

For environment configuration issues:
1. Check this documentation first
2. Review deployment platform logs
3. Verify Google Cloud Console configuration
4. Test individual components as outlined above

---

**Last Updated**: September 27, 2025
**Version**: 1.0
**Platform**: FIDUS Investment Management Platform