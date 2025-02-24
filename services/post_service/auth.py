from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from datetime import datetime

security = HTTPBearer()

class AuthHandler:
    secret = "your-secret-key"  # Should match user service secret

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