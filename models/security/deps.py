from fastapi import Request, HTTPException
from models.security.jwt import verify_token


def get_current_user(request: Request):

    auth = request.headers.get("Authorization")

    if not auth:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = auth.split(" ")[1]
    except:
        raise HTTPException(status_code=401, detail="Invalid token format")

    try:
        payload = verify_token(token)

        if "nth_uid" not in payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        return {
            "nth_uid": payload["nth_uid"],
            "username": payload["username"]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )