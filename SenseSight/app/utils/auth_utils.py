from fastapi import HTTPException, status

from datetime import datetime, timedelta
import jwt

from app.config import security


def get_hashed_password(password: str) -> str:
    return security.pwd_crypt.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return security.pwd_crypt.verify(password, hashed_password)


def create_access_token(data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security.ACCESS_EXPIRY)
    to_encode.update({"exp": expire})
    payload = jwt.encode(to_encode, security.SECRET_KEY, algorithm=security.ALGORITHM)

    return payload, expire


async def get_current_user(request):
    try:
        get_token: str = request.cookies.get("access")
        if get_token is None:
            return None
        payload = jwt.decode(get_token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_id = int(payload.get("sub"))
        if not user_id:
            return None
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# def create_refresh_token(data: dict, expire_delta: timedelta = None):
#     to_encode = data.copy()
#     if expire_delta:
#         expire_delta = datetime.utcnow() + expire_delta
#     else:
#         expire_delta = datetime.utcnow() + timedelta(minutes=REFRESH_EXPIRY)
#     to_encode.update({"exp": expire_delta})
#
#     return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

