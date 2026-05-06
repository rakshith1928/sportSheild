from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.database import get_supabase_client

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates the Supabase JWT token from the Authorization header.
    Returns the Supabase User object which contains the user ID.
    """
    token = credentials.credentials
    client = get_supabase_client()
    try:
        # Ask Supabase to verify the token and return the user
        user_resp = client.auth.get_user(token)
        if not user_resp or not getattr(user_resp, 'user', None):
            raise ValueError("Invalid session")
        return user_resp.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
