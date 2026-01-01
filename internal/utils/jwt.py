from jose import jwt
from internal.constants.constants import SECRETKEY, ALGORITHM
from datetime import datetime, timedelta

def create_jwt_token(user_id, role, email, flat):
    encode = {"authorized":"true", "user_id":user_id, "role":role, "email":email, "flat":flat}
    expires = datetime.utcnow() + timedelta(hours=24)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRETKEY, algorithm=ALGORITHM)