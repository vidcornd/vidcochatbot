from fastapi import APIRouter
from app.config import settings
from app.schemas.widget import WidgetSessionRequest, WidgetSessionResponse, WidgetSessionData
from app.widget.identity import verify_identity_token, IdentityVerificationError
from app.widget.session_store import create_session, SESSION_TTL_SECONDS , get_session
from app.api.errors import api_error

router = APIRouter(prefix="/api/widget", tags=["widget"])

@router.post("/session", response_model=WidgetSessionResponse)
def create_widget_session(payload: WidgetSessionRequest):
    if not settings.is_origin_allowed(payload.origin):
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

@router.get("/session/{session_token}", response_model=WidgetSessionData)
def read_widget_session(session_token: str):
    session = get_session(session_token)
    if not session:
        raise api_error(status_code=404,error="session_not_found",message="Oturum bulunamadı veya süresi dolmuş.")

    return WidgetSessionData(
        botId=session.get("bot_id", ""),
        username=session.get("username"),
        userEmail=session.get("user_email"),
        userRoles=session.get("user_roles") or [],
        rolesVerified=session.get("roles_verified", False),
        currentPage=session.get("current_page"),
        pageTitle=session.get("page_title"),
        origin=session.get("origin", "")
    )