from fastapi import APIRouter
from app.config import settings
from app.schemas.widget import WidgetSessionRequest, WidgetSessionResponse
from app.widget.identity import verify_identity_token, IdentityVerificationError
from app.widget.session_store import create_session, SESSION_TTL_SECONDS
from app.api.errors import api_error

router = APIRouter(prefix="/api/widget", tags=["widget"])

@router.post("/session", response_model=WidgetSessionResponse)
def create_widget_session(payload: WidgetSessionRequest):
    if payload.origin not in settings.allowed_origins_list:
        raise api_error(status_code=403,error="origin_not_allowed",message="Bu origin için widget oturumu açılamaz.")

    if payload.botId != settings.widget_bot_id:
        raise api_error(status_code=400,error="invalid_bot_id",message="Geçersiz botId.")

    user_roles = payload.user.userRoles
    roles_verified = False

    if payload.identityToken:
        try:
            claims = verify_identity_token(payload.identityToken)
            user_roles = claims.get("roles", [])
            roles_verified = True
        except IdentityVerificationError:
            roles_verified = False

    session_token = create_session({
        "bot_id": payload.botId,
        "username": payload.user.username,
        "user_email": payload.user.userEmail,
        "user_roles": user_roles,
        "roles_verified": roles_verified,
        "current_page": payload.context.currentPage,
        "page_title": payload.context.pageTitle,
        "origin": payload.origin})

    return WidgetSessionResponse(sessionToken=session_token, expiresIn=SESSION_TTL_SECONDS)