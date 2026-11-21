import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_knowledge_item_auto_approve(client, mock_supabase):
    org_id = str(uuid.uuid4())
    item_id = str(uuid.uuid4())

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]
    created_item = {
        "id": item_id,
        "org_id": org_id,
        "source_document_id": None,
        "item_type": "rule",
        "category": "terminology",
        "title": "Use sign in",
        "content": "Use 'sign in' instead of 'login'",
        "source_page": None,
        "source_excerpt": None,
        "is_global": False,
        "metadata": {},
        "status": "approved",
        "created_at": "2026-11-19T00:00:00Z",
        "updated_at": "2026-11-19T00:00:00Z",
    }
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [created_item]

    with patch("app.api.knowledge_items.embed_and_store") as mock_embed:
        res = client.post(
            "/knowledge-items",
            json={
                "item_type": "rule",
                "category": "terminology",
                "title": "Use sign in",
                "content": "Use 'sign in' instead of 'login'",
                "auto_approve": True,
            },
            headers={"X-Org-Id": org_id},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["id"] == item_id
        assert data["status"] == "approved"
        mock_embed.assert_called_once_with(uuid.UUID(org_id), [item_id])


def test_create_knowledge_item_pending(client, mock_supabase):
    org_id = str(uuid.uuid4())
    item_id = str(uuid.uuid4())

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]
    created_item = {
        "id": item_id,
        "org_id": org_id,
        "source_document_id": None,
        "item_type": "rule",
        "category": "tone",
        "title": "Empathetic Tone",
        "content": "Always speak empathetically and avoid harsh dismissive language",
        "source_page": None,
        "source_excerpt": None,
        "is_global": False,
        "metadata": {},
        "status": "pending",
        "created_at": "2026-11-19T00:00:00Z",
        "updated_at": "2026-11-19T00:00:00Z",
    }
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [created_item]

    with patch("app.api.knowledge_items.embed_and_store") as mock_embed:
        res = client.post(
            "/knowledge-items",
            json={
                "item_type": "rule",
                "category": "tone",
                "title": "Empathetic Tone",
                "content": "Always speak empathetically and avoid harsh dismissive language",
                "auto_approve": False,
            },
            headers={"X-Org-Id": org_id},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "pending"
        mock_embed.assert_not_called()


def test_rule_tester_sandbox_matches(client, mock_supabase):
    org_id = str(uuid.uuid4())
    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]

    res = client.post(
        "/knowledge-items/test",
        json={
            "rule_content": "Use 'sign in' instead of 'login'",
            "rule_category": "terminology",
            "sample_text": "Please login to your account.",
        },
        headers={"X-Org-Id": org_id},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["matches"] is True
    assert data["method"] == "deterministic"
    assert data["detected_segment"].lower() == "login"
    assert data["suggested_correction"].lower() == "sign in"


def test_rule_tester_sandbox_clean_text(client, mock_supabase):
    org_id = str(uuid.uuid4())
    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]

    res = client.post(
        "/knowledge-items/test",
        json={
            "rule_content": "Use 'sign in' instead of 'login'",
            "rule_category": "terminology",
            "sample_text": "Please sign in to your account.",
        },
        headers={"X-Org-Id": org_id},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["matches"] is False
    assert data["detected_segment"] is None


def test_delete_knowledge_item(client, mock_supabase):
    org_id = str(uuid.uuid4())
    item_id = str(uuid.uuid4())

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]
    mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {"id": item_id}
    ]

    res = client.delete(f"/knowledge-items/{item_id}", headers={"X-Org-Id": org_id})
    assert res.status_code == 200
    assert res.json() == {"deleted": True, "id": item_id}


def test_delete_knowledge_item_not_found(client, mock_supabase):
    org_id = str(uuid.uuid4())
    item_id = str(uuid.uuid4())

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]
    mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

    res = client.delete(f"/knowledge-items/{item_id}", headers={"X-Org-Id": org_id})
    assert res.status_code == 404


def test_supabase_jwt_auth_resolution(client, mock_supabase):
    jwt_org_id = str(uuid.uuid4())
    jwt_user_id = str(uuid.uuid4())

    # Mock user returned by sb.auth.get_user
    mock_user = MagicMock()
    mock_user.id = jwt_user_id
    mock_user.email = "brandadmin@acme.com"
    mock_supabase.auth.get_user.return_value.user = mock_user

    # Mock profile lookup
    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"org_id": jwt_org_id, "role": "admin", "full_name": "Admin Alice"}
    ]

    # Call an endpoint using Bearer token without X-Org-Id header
    res = client.get("/organisations", headers={"Authorization": "Bearer test-valid-jwt-token"})
    assert res.status_code == 200


def test_cross_tenant_access_rejected_403(client, mock_supabase):
    user_org_id = str(uuid.uuid4())
    other_org_id = str(uuid.uuid4())
    jwt_user_id = str(uuid.uuid4())

    mock_user = MagicMock()
    mock_user.id = jwt_user_id
    mock_user.email = "user@tenant-a.com"
    mock_supabase.auth.get_user.return_value.user = mock_user

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"org_id": user_org_id, "role": "admin", "full_name": "Tenant A Admin"}
    ]

    # Attempt to access with a mismatched X-Org-Id (tenant B)
    res = client.get(
        "/organisations",
        headers={
            "Authorization": "Bearer valid-token-a",
            "X-Org-Id": other_org_id,
        },
    )
    assert res.status_code == 403
    assert "Forbidden: You do not have access to this workspace" in res.json()["detail"]


def test_get_other_organisation_forbidden_403(client, mock_supabase):
    user_org_id = str(uuid.uuid4())
    other_org_id = str(uuid.uuid4())
    jwt_user_id = str(uuid.uuid4())

    mock_user = MagicMock()
    mock_user.id = jwt_user_id
    mock_user.email = "user@tenant-a.com"
    mock_supabase.auth.get_user.return_value.user = mock_user

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"org_id": user_org_id, "role": "admin", "full_name": "Tenant A Admin"}
    ]

    # Attempt to fetch details of a different company's workspace directly by org_id
    res = client.get(
        f"/organisations/{other_org_id}",
        headers={"Authorization": "Bearer valid-token-a"},
    )
    assert res.status_code == 403
    assert "Forbidden: You do not have access to this workspace" in res.json()["detail"]


def test_analytics_metrics(client, mock_supabase):
    org_id = str(uuid.uuid4())
    rule_id = str(uuid.uuid4())

    mock_supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": org_id, "name": "Acme Corp"}
    ]

    # Setup mock returns for the 3 tables queried in get_analytics
    def table_router(table_name):
        mock_builder = MagicMock()
        if table_name == "content_submissions":
            mock_builder.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"id": str(uuid.uuid4()), "status": "approved", "content_type": "text"},
                {"id": str(uuid.uuid4()), "status": "approved", "content_type": "text"},
                {"id": str(uuid.uuid4()), "status": "needs_revision", "content_type": "pdf"},
            ]
        elif table_name == "findings":
            mock_builder.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
                {
                    "id": str(uuid.uuid4()),
                    "severity": "high",
                    "status": "fixed",
                    "source": "deterministic",
                    "knowledge_item_id": rule_id,
                },
                {
                    "id": str(uuid.uuid4()),
                    "severity": "medium",
                    "status": "open",
                    "source": "deterministic",
                    "knowledge_item_id": rule_id,
                },
            ]
        elif table_name == "knowledge_items":
            mock_builder.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
                {
                    "id": rule_id,
                    "title": "Use sign in",
                    "content": "Use 'sign in' instead of 'login'",
                    "category": "terminology",
                    "status": "approved",
                }
            ]
        elif table_name == "organisations":
            mock_builder.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
                {"id": org_id, "name": "Acme Corp"}
            ]
        return mock_builder

    mock_supabase.table.side_effect = table_router

    res = client.get("/analytics", headers={"X-Org-Id": org_id})
    assert res.status_code == 200
    data = res.json()
    assert data["total_submissions"] == 3
    assert data["approved_submissions"] == 2
    assert data["total_violations"] == 2
    assert data["fix_rate"] == 50.0
    assert len(data["top_violated_rules"]) == 1
    assert data["top_violated_rules"][0]["rule_id"] == rule_id
    assert data["category_breakdown"]["terminology"] == 2
    assert "compliance_score" in data
