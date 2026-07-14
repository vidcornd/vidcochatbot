import jwt
from app.config import settings

class IdentityVerificationError(Exception):
    pass

def verify_identity_token(token: str) -> dict:
    if not settings.jwt_secret:
        raise IdentityVerificationError("JWT secret yapılandırılmamış.")

    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise IdentityVerificationError("identityToken süresi dolmuş.") from exc
    except jwt.InvalidTokenError as exc:
        raise IdentityVerificationError("identityToken geçersiz.") from exc