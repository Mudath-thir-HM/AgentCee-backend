from fastapi import (
    Header,
    HTTPException
)

from jose import (
    jwt,
    JWTError
)

from app.core.config import (
    settings
)


async def get_current_user(
    authorization: str | None = Header(
        default=None
    )
):
    print(
        "AUTH HEADER:",
        authorization
    )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith(
        "Bearer "
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[
                settings.JWT_ALGORITHM
            ]
        )

        user_id = payload.get(
            "sub"
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return user_id

    except JWTError as e:
        print(
            "JWT ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )