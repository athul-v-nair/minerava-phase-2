import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.auth import AuthResponse, LoginRequest, OrgOut, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        orgId=user.org_id,
        role=user.role.value,
        created_at=user.created_at.isoformat(),
    )


def _org_out(org: Organization | None) -> OrgOut | None:
    if not org:
        return None
    return OrgOut(id=org.id, name=org.name, created_at=org.created_at.isoformat())


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    org: Organization | None = None
    org_id: str | None = None
    role = UserRole.member

    if payload.orgName:
        org_name = payload.orgName.strip()
        if not org_name:
            raise HTTPException(status_code=400, detail="orgName cannot be empty")
        existing_org = db.query(Organization).filter(Organization.name == org_name).first()
        if existing_org:
            raise HTTPException(status_code=409, detail="Organization name already taken")
        org = Organization(id=str(uuid.uuid4()), name=org_name, created_at=datetime.now(UTC))
        db.add(org)
        db.flush()
        org_id = org.id
        role = UserRole.org_admin

    try:
        pw_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash=pw_hash,
        org_id=org_id,
        role=role,
        created_at=datetime.now(UTC),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if org:
        db.refresh(org)

    access = create_access_token(user_id=user.id, email=user.email, org_id=user.org_id, role=user.role.value)
    refresh, _jti, _exp = create_refresh_token(user_id=user.id)

    return AuthResponse(access_token=access, refresh_token=refresh, user=_user_out(user), org=_org_out(org))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    org = None
    if user.org_id:
        org = db.get(Organization, user.org_id)

    access = create_access_token(user_id=user.id, email=user.email, org_id=user.org_id, role=user.role.value)
    refresh, _jti, _exp = create_refresh_token(user_id=user.id)

    return AuthResponse(access_token=access, refresh_token=refresh, user=_user_out(user), org=_org_out(org))
