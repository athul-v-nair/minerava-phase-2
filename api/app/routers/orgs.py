from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_org_admin
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import OrgOut, OrgPatchRequest, UserOut

router = APIRouter(prefix="/orgs", tags=["orgs"])


@router.get("/me", response_model=OrgOut)
def get_my_org(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    if not current_user.org_id:
        raise HTTPException(status_code=404, detail="No organization")
    org = db.get(Organization, current_user.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrgOut(id=org.id, name=org.name, created_at=org.created_at.isoformat())


@router.get("/{org_id}", response_model=dict)
def get_org_detail(org_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):  # type: ignore[no-untyped-def]
    # tenant isolation — only own org
    if current_user.org_id != org_id:
        raise HTTPException(status_code=404, detail="Organization not found")
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    members = db.query(User).filter(User.org_id == org_id).all()
    return {
        "org": OrgOut(id=org.id, name=org.name, created_at=org.created_at.isoformat()),
        "members": [
            UserOut(
                id=m.id,
                email=m.email,
                orgId=m.org_id,
                role=m.role.value,
                created_at=m.created_at.isoformat(),
            )
            for m in members
        ],
    }


@router.patch("/{org_id}", response_model=OrgOut)
def patch_org(
    org_id: str,
    payload: OrgPatchRequest,
    current_user: User = Depends(require_org_admin),
    db: Session = Depends(get_db),  # type: ignore[no-untyped-def]
):
    if current_user.org_id != org_id:
        raise HTTPException(status_code=404, detail="Organization not found")
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    # unique name check
    existing = db.query(Organization).filter(Organization.name == payload.name, Organization.id != org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Organization name already taken")
    org.name = payload.name
    db.commit()
    db.refresh(org)
    return OrgOut(id=org.id, name=org.name, created_at=org.created_at.isoformat())
