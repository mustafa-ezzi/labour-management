from __future__ import annotations

from typing import Any

from apps.accounts.audit import AdminAuditLog


def write_admin_audit(
    *,
    actor,
    action: str,
    summary: str = "",
    target_type: str = "",
    target_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> AdminAuditLog:
    return AdminAuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        summary=summary[:512],
        target_type=target_type[:64],
        target_id=str(target_id)[:64] if target_id else "",
        metadata=metadata or {},
    )
