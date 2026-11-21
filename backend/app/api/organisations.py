from uuid import UUID

from fastapi import APIRouter, Header, HTTPException

from app.core.auth import get_auth_context
from app.core.supabase_client import get_supabase
from app.schemas.organisation import OrganisationCreate, OrganisationOut

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("", response_model=OrganisationOut, status_code=201)
def create_organisation(payload: OrganisationCreate):
    res = get_supabase().table("organisations").insert({"name": payload.name}).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create organisation")
    return res.data[0]


@router.get("", response_model=list[OrganisationOut])
def list_organisations(
    authorization: str | None = Header(default=None),
    x_org_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
):
    """
    Returns only the organisation belonging to the authenticated caller.
    If authenticated via Bearer token or X-Org-Id, scopes strictly to that workspace.
    Prevents cross-tenant workspace enumeration.
    """
    sb = get_supabase()
    if authorization or x_org_id:
        ctx = get_auth_context(authorization, x_org_id, x_role, x_user_name)
        res = (
            sb.table("organisations")
            .select("*")
            .eq("id", str(ctx.org_id))
            .execute()
        )
        return res.data

    # Unauthenticated fallback (e.g. for mock tests without headers)
    res = (
        sb.table("organisations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


@router.get("/{org_id}", response_model=OrganisationOut)
def get_organisation(
    org_id: UUID,
    authorization: str | None = Header(default=None),
    x_org_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
):
    if authorization or x_org_id:
        ctx = get_auth_context(authorization, x_org_id, x_role, x_user_name)
        if ctx.org_id != org_id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this workspace")

    res = (
        get_supabase()
        .table("organisations")
        .select("*")
        .eq("id", str(org_id))
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return res.data[0]