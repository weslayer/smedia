from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from datetime import datetime
import os

security = HTTPBearer()

class AuthHandler:
    secret = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Get from env

    def decode_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            if payload["exp"] < datetime.utcnow().timestamp():
                raise HTTPException(status_code=401, detail="Token has expired")
            return payload["user_id"]
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

auth_handler = AuthHandler()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> int:
    return auth_handler.decode_token(credentials.credentials) 