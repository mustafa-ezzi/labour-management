"""Admin support inbox APIs."""

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import AdminAuditLog
from apps.accounts.audit_services import write_admin_audit
from apps.api.permissions import IsAppAdmin
from apps.support.models import SupportTicket, TicketPriority, TicketStatus
from apps.support.services import (
    add_admin_message,
    admin_unread_count,
    annotate_message_count,
    open_ticket_count,
    serialize_ticket,
)


class AdminSupportTicketListView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request):
        qs = annotate_message_count(
            SupportTicket.objects.select_related(
                "company", "created_by", "company__owner"
            ).order_by("-admin_unread", "-updated_at")
        )

        status_filter = (request.query_params.get("status") or "").strip().lower()
        if status_filter == "openish":
            qs = qs.filter(status__in=[TicketStatus.OPEN, TicketStatus.PENDING])
        elif status_filter:
            qs = qs.filter(status=status_filter)

        q = (request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(subject__icontains=q)
                | Q(company__name__icontains=q)
                | Q(created_by__email__icontains=q)
            )

        unread_only = request.query_params.get("unread")
        if unread_only in ("1", "true", "yes"):
            qs = qs.filter(admin_unread=True)

        results = [serialize_ticket(t) for t in qs[:200]]
        return Response(
            {
                "count": len(results),
                "open_count": open_ticket_count(),
                "unread_count": admin_unread_count(),
                "results": results,
            }
        )


class AdminSupportTicketDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def get(self, request, ticket_id):
        try:
            ticket = (
                SupportTicket.objects.select_related(
                    "company", "created_by", "company__owner"
                )
                .prefetch_related("messages__sender")
                .get(pk=ticket_id)
            )
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"detail": "Ticket not found."}, status=404)

        if ticket.admin_unread:
            ticket.admin_unread = False
            ticket.save(update_fields=["admin_unread"])

        return Response(serialize_ticket(ticket, include_messages=True))

    def patch(self, request, ticket_id):
        try:
            ticket = SupportTicket.objects.select_related(
                "company", "created_by", "company__owner"
            ).get(pk=ticket_id)
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"detail": "Ticket not found."}, status=404)

        data = request.data or {}
        changed = []
        if "status" in data:
            status_val = str(data["status"]).strip().lower()
            if status_val not in TicketStatus.values:
                return Response({"status": ["Invalid status."]}, status=400)
            ticket.status = status_val
            changed.append("status")
        if "priority" in data:
            pri = str(data["priority"]).strip().lower()
            if pri not in TicketPriority.values:
                return Response({"priority": ["Invalid priority."]}, status=400)
            ticket.priority = pri
            changed.append("priority")

        ticket.save()
        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.SUPPORT_STATUS,
            summary=f"Updated ticket {ticket.subject[:80]}",
            target_type="support_ticket",
            target_id=str(ticket.pk),
            metadata={"fields": changed, "status": ticket.status},
        )
        ticket = (
            SupportTicket.objects.select_related("company", "created_by", "company__owner")
            .prefetch_related("messages__sender")
            .get(pk=ticket.pk)
        )
        return Response(serialize_ticket(ticket, include_messages=True))


class AdminSupportTicketMessageCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAppAdmin]

    def post(self, request, ticket_id):
        try:
            ticket = SupportTicket.objects.select_related("company").get(pk=ticket_id)
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"detail": "Ticket not found."}, status=404)

        try:
            add_admin_message(
                ticket=ticket,
                admin=request.user,
                body=str((request.data or {}).get("body") or ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        write_admin_audit(
            actor=request.user,
            action=AdminAuditLog.Action.SUPPORT_REPLY,
            summary=f"Replied to ticket {ticket.subject[:80]}",
            target_type="support_ticket",
            target_id=str(ticket.pk),
        )
        ticket = (
            SupportTicket.objects.select_related("company", "created_by", "company__owner")
            .prefetch_related("messages__sender")
            .get(pk=ticket.pk)
        )
        return Response(serialize_ticket(ticket, include_messages=True))
