from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth import decode_token

#read Header Bearer
bearer = HTTPBearer()

#Auth Dependency for secured Endpoints
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    username = decode_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return username
