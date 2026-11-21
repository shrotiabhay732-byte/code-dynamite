from uuid import UUID

from fastapi import Depends, Header, HTTPException

from app.core.supabase_client import get_supabase

ROLES = ("admin", "creator", "reviewer")


class AuthContext:
    def __init__(
        self,
        org_id: UUID,
        role: str,
        user_name: str,
        user_id: str | None = None,
    ):
        self.org_id = org_id
        self.role = role
        self.user_name = user_name
        self.user_id = user_id


def get_auth_context(
    authorization: str | None = Header(default=None),
    x_org_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
) -> AuthContext:
    """
    Authenticates requests via Supabase Auth JWT Bearer token or demo headers.
    1. Checks Authorization: Bearer <jwt>, verifies user and retrieves org profile.
    2. Falls back to X-Org-Id, X-Role, X-User-Name for backward compatibility and testing.
    """
    sb = get_supabase()

    # 1. Supabase Auth JWT
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            try:
                user_res = sb.auth.get_user(token)
                user = getattr(user_res, "user", None)
                if user and getattr(user, "id", None):
                    p_res = (
                        sb.table("profiles")
                        .select("org_id, role, full_name")
                        .eq("id", str(user.id))
                        .limit(1)
                        .execute()
                    )
                    user_org_id = None
                    role = "admin"
                    full_name = getattr(user, "email", "Caraxes User")
                    if p_res.data:
                        prof = p_res.data[0]
                        user_org_id = UUID(prof["org_id"])
                        role = (prof.get("role") or "admin").lower()
                        full_name = (prof.get("full_name") or getattr(user, "email", "Caraxes User"))[:60]
                    else:
                        meta = getattr(user, "user_metadata", {}) or {}
                        if meta.get("org_id"):
                            user_org_id = UUID(meta["org_id"])
                            role = (meta.get("role") or "admin").lower()
                            full_name = (meta.get("full_name") or getattr(user, "email", "Caraxes User"))[:60]

                    if user_org_id:
                        # Prevent cross-workspace tenant hopping:
                        # If a client attempts to pass a different organization's X-Org-Id, reject it!
                        if x_org_id:
                            try:
                                requested_org = UUID(x_org_id)
                                if requested_org != user_org_id:
                                    raise HTTPException(
                                        status_code=403,
                                        detail="Forbidden: You do not have access to this workspace",
                                    )
                            except ValueError:
                                raise HTTPException(status_code=400, detail="Invalid X-Org-Id format")

                        return AuthContext(
                            org_id=user_org_id,
                            role=role if role in ROLES else "admin",
                            user_name=full_name,
                            user_id=str(user.id),
                        )
            except HTTPException:
                raise
            except Exception:
                pass

    # 2. Fallback to demo headers
    if not x_org_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: Provide Bearer token or X-Org-Id header",
        )
    try:
        org_id = UUID(x_org_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-Org-Id is not a valid UUID")

    res = (
        sb.table("organisations")
        .select("id")
        .eq("id", str(org_id))
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=401, detail="Unknown organisation")

    role = (x_role or "admin").lower()
    return AuthContext(
        org_id=org_id,
        role=role if role in ROLES else "admin",
        user_name=(x_user_name or "Caraxes User")[:60],
    )


def get_org_id(ctx: AuthContext = Depends(get_auth_context)) -> UUID:
    return ctx.org_id


def get_role(ctx: AuthContext = Depends(get_auth_context)) -> str:
    return ctx.role


def get_user_name(ctx: AuthContext = Depends(get_auth_context)) -> str:
    return ctx.user_name


def require_role(*allowed: str):
    """Common interface: all roles (admin, creator, reviewer) have access to all actions."""

    def checker(role: str = Depends(get_role)) -> str:
        return role

    return checker