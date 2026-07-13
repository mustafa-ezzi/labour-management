"""User-facing support ticket APIs."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import IsAuthenticatedCompanyMember
from apps.companies.subscription_services import company_for_user
from apps.support.models import SupportTicket, TicketStatus
from apps.support.services import (
    add_user_message,
    annotate_message_count,
    create_ticket,
    serialize_ticket,
    user_unread_count,
)


class SupportTicketListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]

    def get(self, request):
        company = company_for_user(request.user)
        qs = annotate_message_count(
            SupportTicket.objects.filter(company=company)
            .select_related("company", "created_by", "company__owner")
            .order_by("-updated_at")
        )
        status_filter = (request.query_params.get("status") or "").strip().lower()
        if status_filter:
            qs = qs.filter(status=status_filter)
        results = [serialize_ticket(t) for t in qs[:100]]
        return Response(
            {
                "count": len(results),
                "unread": user_unread_count(request.user),
                "results": results,
            }
        )

    def post(self, request):
        company = company_for_user(request.user)
        data = request.data or {}
        try:
            ticket = create_ticket(
                company=company,
                user=request.user,
                subject=str(data.get("subject") or ""),
                body=str(data.get("body") or data.get("message") or ""),
                priority=str(data.get("priority") or "normal"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        ticket = (
            SupportTicket.objects.select_related("company", "created_by", "company__owner")
            .prefetch_related("messages__sender")
            .get(pk=ticket.pk)
        )
        return Response(
            serialize_ticket(ticket, include_messages=True),
            status=status.HTTP_201_CREATED,
        )


class SupportTicketDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]

    def get(self, request, ticket_id):
        company = company_for_user(request.user)
        try:
            ticket = (
                SupportTicket.objects.select_related(
                    "company", "created_by", "company__owner"
                )
                .prefetch_related("messages__sender")
                .get(pk=ticket_id, company=company)
            )
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"detail": "Ticket not found."}, status=404)

        if ticket.user_unread:
            ticket.user_unread = False
            ticket.save(update_fields=["user_unread"])

        return Response(serialize_ticket(ticket, include_messages=True))


class SupportTicketMessageCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedCompanyMember]

    def post(self, request, ticket_id):
        company = company_for_user(request.user)
        try:
            ticket = SupportTicket.objects.select_related("company").get(
                pk=ticket_id, company=company
            )
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"detail": "Ticket not found."}, status=404)

        try:
            add_user_message(
                ticket=ticket,
                user=request.user,
                body=str((request.data or {}).get("body") or ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        ticket = (
            SupportTicket.objects.select_related("company", "created_by", "company__owner")
            .prefetch_related("messages__sender")
            .get(pk=ticket.pk)
        )
        return Response(serialize_ticket(ticket, include_messages=True))
