from jose import jwt, JWTError
from fastapi import (
    Header,
    HTTPException
)

from app.core.security import (
    SECRET_KEY,
    ALGORITHM
)


async def get_current_user(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="No token"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload["sub"]

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )