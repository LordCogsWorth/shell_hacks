"""
FastAPI Authentication Middleware for Auth0 JWT Token Validation

This module provides JWT token validation for Auth0 following the 
secure Authorization Code Flow with PKCE pattern.
"""

import jwt
import requests
from typing import Dict, Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'your-domain.auth0.com')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'https://travelmaster-api')
AUTH0_ALGORITHMS = ['RS256']

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthError(Exception):
    """Custom Auth Error Exception"""
    def __init__(self, error: Dict[str, str], status_code: int):
        self.error = error
        self.status_code = status_code


@lru_cache()
def get_auth0_public_key():
    """Get Auth0 public key for JWT verification (cached)"""
    try:
        if AUTH0_DOMAIN == 'your-domain.auth0.com':
            logger.warning("Auth0 not configured - authentication disabled")
            return None
            
        url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get Auth0 public key: {e}")
        return None


def get_token_payload(token: str) -> Dict:
    """
    Validate JWT token and return payload
    
    Args:
        token: JWT token string
        
    Returns:
        Dict containing token payload
        
    Raises:
        AuthError: If token is invalid
    """
    try:
        # Get signing key
        jwks = get_auth0_public_key()
        if not jwks:
            raise AuthError({
                "code": "auth_config_error",
                "description": "Authentication service not available"
            }, 503)
        
        # Decode token header to get kid
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise AuthError({
                "code": "invalid_header",
                "description": "Unable to find appropriate key"
            }, 401)
        
        # Create PyJWK from the RSA key
        from jwt import PyJWK
        jwk = PyJWK(rsa_key)
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            jwk.key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthError({
            "code": "token_expired",
            "description": "Token has expired"
        }, 401)
    except jwt.InvalidAudienceError:
        raise AuthError({
            "code": "invalid_audience",
            "description": "Token audience is invalid"
        }, 401)
    except jwt.InvalidIssuerError:
        raise AuthError({
            "code": "invalid_issuer",
            "description": "Token issuer is invalid"
        }, 401)
    except jwt.InvalidTokenError:
        raise AuthError({
            "code": "invalid_token",
            "description": "Token is invalid"
        }, 401)
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise AuthError({
            "code": "token_validation_failed",
            "description": "Unable to validate token"
        }, 401)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[Dict]:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Dict containing user information or None if no auth configured
        
    Raises:
        HTTPException: If token is invalid
    """
    # If Auth0 not configured, allow anonymous access
    if AUTH0_DOMAIN == 'your-domain.auth0.com':
        logger.info("Auth0 not configured - allowing anonymous access")
        return None
    
    # If no credentials provided, deny access
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = get_token_payload(credentials.credentials)
        return payload
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.error,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[Dict]:
    """
    Optional dependency to get current user (doesn't raise error if no auth)
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Dict containing user information or None
    """
    # If Auth0 not configured, return None
    if AUTH0_DOMAIN == 'your-domain.auth0.com':
        return None
    
    # If no credentials provided, return None
    if not credentials:
        return None
    
    try:
        payload = get_token_payload(credentials.credentials)
        return payload
    except AuthError:
        return None


def require_auth(user: Annotated[Dict, Depends(get_current_user)]) -> Dict:
    """
    Dependency that requires authentication
    
    Args:
        user: User from get_current_user dependency
        
    Returns:
        User information dict
    """
    return user


def optional_auth(user: Annotated[Optional[Dict], Depends(get_current_user_optional)]) -> Optional[Dict]:
    """
    Dependency that provides optional authentication
    
    Args:
        user: User from get_current_user_optional dependency
        
    Returns:
        User information dict or None
    """
    return user


# Utility functions for extracting user info
def get_user_id(user: Dict) -> str:
    """Extract user ID from token payload"""
    return user.get('sub', '')


def get_user_email(user: Dict) -> Optional[str]:
    """Extract user email from token payload"""
    return user.get('email')


def get_user_name(user: Dict) -> Optional[str]:
    """Extract user name from token payload"""
    return user.get('name') or user.get('given_name') or user.get('nickname')


def has_role(user: Dict, role: str) -> bool:
    """Check if user has a specific role"""
    roles = user.get('https://travelmaster.com/roles', [])
    return role in roles


def has_permission(user: Dict, permission: str) -> bool:
    """Check if user has a specific permission"""
    permissions = user.get('https://travelmaster.com/permissions', [])
    return permission in permissions
