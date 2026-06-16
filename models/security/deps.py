from fastapi import Request, HTTPException, Depends
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
        return payload  # contains user_id, username
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")