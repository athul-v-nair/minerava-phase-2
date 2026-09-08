from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    orgName: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    org_id: str | None = Field(default=None, alias="orgId")
    role: str
    created_at: str

    model_config = {"populate_by_name": True}


class OrgOut(BaseModel):
    id: str
    name: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut
    org: OrgOut | None = None


class MeResponse(BaseModel):
    user: UserOut
    org: OrgOut | None = None


class OrgPatchRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
