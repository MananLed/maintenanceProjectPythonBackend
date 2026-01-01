from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from internal.constants.constants import SECRETKEY, ALGORITHM
from datetime import datetime, timedelta

def create_jwt_token(user_id, role, email, flat):
    encode = {"authorized":"true", "user_id":user_id, "role":role, "email":email, "flat":flat}
    expires = datetime.utcnow() + timedelta(hours=24)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRETKEY, algorithm=ALGORITHM)

def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    
    token = auth_header.split(" ")[1]

    try:
        claims = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    request.state.user = claims
