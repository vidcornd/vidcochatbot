from pydantic import BaseModel, Field, field_validator

class WidgetUser(BaseModel):
    username: str | None = None
    userEmail: str | None = None
    userRoles: list[str] = Field(default_factory=list)

    @field_validator("userRoles", mode="before")
    @classmethod
    def normalize_roles(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(role).strip() for role in value if str(role).strip()]

        if isinstance(value, str):
            return [role.strip() for role in value.split(";") if role.strip()]

        return []

class WidgetContext(BaseModel):
    currentPage: str | None = None
    pageTitle: str | None = None

class WidgetSessionRequest(BaseModel):
    botId: str = Field(..., min_length=1)
    user: WidgetUser = Field(default_factory=WidgetUser)
    context: WidgetContext = Field(default_factory=WidgetContext)
    identityToken: str | None = None
    origin: str = Field(..., min_length=1)
    requireConsent: bool = False

class WidgetSessionResponse(BaseModel):
    sessionToken: str
    expiresIn: int

class WidgetSessionData(BaseModel):
    botId: str
    username: str | None = None
    userEmail: str | None = None
    userRoles: list[str] = Field(default_factory=list)
    rolesVerified: bool = False
    currentPage: str | None = None
    pageTitle: str | None = None
    origin: str
    requireConsent: bool = False