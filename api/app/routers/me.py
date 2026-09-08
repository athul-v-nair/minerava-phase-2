from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import MeResponse, OrgOut, UserOut

router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    org = None
    if current_user.org_id:
        org = db.get(Organization, current_user.org_id)
    user_out = UserOut(
        id=current_user.id,
        email=current_user.email,
        orgId=current_user.org_id,
        role=current_user.role.value,
        created_at=current_user.created_at.isoformat(),
    )
    org_out = OrgOut(id=org.id, name=org.name, created_at=org.created_at.isoformat()) if org else None
    return MeResponse(user=user_out, org=org_out)
