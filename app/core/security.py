import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, InvalidSignatureError

from core.config import settings


def generate_access_token(user_id: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "type": "access",
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    token = jwt.encode(
        payload,
        settings.AUTH_JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return token, jti


def generate_refresh_token(user_id: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())

    payload = {
        "type": "refresh",
        "sub": str(user_id),
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(
            days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    }

    token = jwt.encode(
        payload,
        settings.AUTH_JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return token, jti


def decode_access_token(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type not valid",
            )

        if not decoded.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, sub not in the payload",
            )

        if not decoded.get("jti"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, jti not in the payload",
            )

        return decoded

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {exc}",
        )

    
def decode_refresh_token(token: str) -> dict:
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"],
        )

        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type not valid",
            )

        if not decoded.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, sub not in the payload",
            )

        if not decoded.get("jti"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, jti not in the payload",
            )

        return decoded

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {exc}",
        )


def get_token_expiration_times() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)

    access_expires_at = now + timedelta(
        minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_expires_at = now + timedelta(
        days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS
    )

    return access_expires_at, refresh_expires_at

 
# def get_authenticated_user(
#     request: Request, 
#     db: Session = Depends(get_db)
# ):
#     access_token = request.cookies.get("access_token")
#     try:
#         decoded = jwt.decode(
#             access_token, settings.AUTH_JWT_SECRET_KEY, algorithms="HS256"
#         )
#         user_id = decoded.get("sub", None)
#         if not user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication failed, sub not in the payload",
#             )

#         if decoded.get("type") != "access":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication failed, token type not valid",
#             )

#         user_obj = db.query(UserModel).filter_by(id=user_id).one()
#         return user_obj

#     except InvalidSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication failed, invalid signature",
#         )
#     except DecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication failed, decode failed",
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Authentication failed, {e}",
#         )


# def admin_required(current_user: UserModel):
#     if current_user.type != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admin users can perform this action"
#         )
#     return True
    