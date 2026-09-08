import uuid

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def _uid() -> str:
    return uuid.uuid4().hex[:8]


def test_register_login_me_flow():
    suffix = _uid()
    email = f"e2e_{suffix}@example.com"
    org = f"Org_{suffix}"
    r = client.post("/auth/register", json={"email": email, "password": "supersecure123", "orgName": org})
    assert r.status_code == 201, r.text
    data = r.json()
    assert "access_token" in data and "refresh_token" in data
    assert data["user"]["email"] == email.lower()
    assert data["user"]["role"] == "org_admin"
    assert data["org"]["name"] == org

    token = data["access_token"]
    me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["user"]["email"] == email.lower()
    assert me.json()["org"]["name"] == org

    org_me = client.get("/orgs/me", headers={"Authorization": f"Bearer {token}"})
    assert org_me.status_code == 200
    assert org_me.json()["name"] == org

    # login again
    login = client.post("/auth/login", json={"email": email, "password": "supersecure123"})
    assert login.status_code == 200
    assert login.json()["user"]["id"] == data["user"]["id"]


def test_register_without_org_creates_member():
    suffix = _uid()
    email = f"member_{suffix}@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "anothersecure123"})
    assert r.status_code == 201, r.text
    assert r.json()["user"]["orgId"] is None
    assert r.json()["user"]["role"] == "member"
    assert r.json()["org"] is None


def test_wrong_password_401_no_stacktrace():
    suffix = _uid()
    email = f"wrong_{suffix}@example.com"
    client.post("/auth/register", json={"email": email, "password": "supersecure123"})
    r = client.post("/auth/login", json={"email": email, "password": "wrongpassword12"})
    assert r.status_code == 401
    body = r.json()
    assert "detail" in body
    # no stack trace in response
    assert "Traceback" not in r.text


def test_password_hash_not_plaintext():
    suffix = _uid()
    email = f"hash_{suffix}@example.com"
    pwd = "supersecure123"
    client.post("/auth/register", json={"email": email, "password": pwd})
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email.lower()).first()
        assert u is not None
        assert u.password_hash != pwd
        assert u.password_hash.startswith("$2b$") or u.password_hash.startswith("$2a$")
    finally:
        db.close()


def test_protected_routes_require_bearer():
    for path in ["/me", "/orgs/me"]:
        r = client.get(path)
        assert r.status_code == 401, f"{path} should be 401 without token, got {r.status_code}"
        r2 = client.get(path, headers={"Authorization": "Bearer invalidtoken"})
        assert r2.status_code == 401


def test_org_patch_admin_only_and_tenant_isolation():
    # admin
    suffix = _uid()
    admin_email = f"admin_{suffix}@example.com"
    r = client.post("/auth/register", json={"email": admin_email, "password": "supersecure123", "orgName": f"OrgA_{suffix}"})
    admin_token = r.json()["access_token"]
    org_id = r.json()["org"]["id"]

    # member without org tries to patch admin org -> 403 (admin only check first)
    mem_email = f"member2_{suffix}@example.com"
    r2 = client.post("/auth/register", json={"email": mem_email, "password": "anothersecure123"})
    mem_token = r2.json()["access_token"]
    r3 = client.patch(f"/orgs/{org_id}", headers={"Authorization": f"Bearer {mem_token}"}, json={"name": "Hacked"})
    assert r3.status_code in (403, 404)

    # admin patches own org -> ok
    r4 = client.patch(f"/orgs/{org_id}", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": f"Renamed_{suffix}"})
    assert r4.status_code == 200
    assert r4.json()["name"] == f"Renamed_{suffix}"

    # admin tries to patch non-existent org -> 404
    fake_id = uuid.uuid4().hex
    r5 = client.patch(f"/orgs/{fake_id}", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "X"})
    assert r5.status_code == 404

    # GET org detail with tenant isolation
    r6 = client.get(f"/orgs/{org_id}", headers={"Authorization": f"Bearer {mem_token}"})
    # member not in org -> 404 per S3 guardrail (not 403)
    assert r6.status_code == 404
    r7 = client.get(f"/orgs/{org_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert r7.status_code == 200
    assert "members" in r7.json()


def test_password_len_validation():
    suffix = _uid()
    r = client.post("/auth/register", json={"email": f"short_{suffix}@example.com", "password": "short"})
    assert r.status_code == 422

    r2 = client.post("/auth/register", json={"email": f"dup_{suffix}@example.com", "password": "supersecure123", "orgName": f"DupOrg_{suffix}"})
    assert r2.status_code == 201
    r3 = client.post("/auth/register", json={"email": f"dup_{suffix}@example.com", "password": "supersecure123"})
    assert r3.status_code == 409
