from fastapi import Request
from jose import jwt, JWTError
from internal.constants.constants import *
from datetime import datetime, timedelta
from internal.errors.base_exception import AppException

def create_jwt_token(user_id, role, email, flat):
    encode = {"authorized":"true", "user_id":user_id, "role":role, "email":email, "flat":flat}
    expires = datetime.utcnow() + timedelta(hours=24)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRETKEY, algorithm=ALGORITHM)

def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AppException(AUTH_001)
    
    token = auth_header.split(" ")[1]

    try:
        claims = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
    except JWTError:
        raise AppException(AUTH_002)
    
    request.state.user = claims
