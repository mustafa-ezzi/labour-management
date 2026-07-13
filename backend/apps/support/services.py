"""Serialize + create helpers for support tickets."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from apps.companies.subscription_services import (
    company_for_user,
    serialize_subscription,
)
from apps.support.models import (
    SupportMessage,
    SupportTicket,
    TicketPriority,
    TicketStatus,
)


def serialize_message(msg: SupportMessage) -> dict:
    return {
        "id": str(msg.id),
        "body": msg.body,
        "is_admin_reply": msg.is_admin_reply,
        "created_at": msg.created_at.isoformat(),
        "sender_email": msg.sender.email if msg.sender_id else None,
        "sender_name": (
            f"{(msg.sender.first_name or '').strip()} {(msg.sender.last_name or '').strip()}".strip()
            or (msg.sender.email if msg.sender_id else None)
        ),
    }


def serialize_ticket(ticket: SupportTicket, *, include_messages: bool = False) -> dict:
    sub = None
    try:
        sub = serialize_subscription(ticket.company.subscription)
    except Exception:
        sub = None

    data = {
        "id": str(ticket.id),
        "subject": ticket.subject,
        "status": ticket.status,
        "priority": ticket.priority,
        "admin_unread": ticket.admin_unread,
        "user_unread": ticket.user_unread,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
        "company": {
            "id": str(ticket.company_id),
            "name": ticket.company.name,
        },
        "created_by": {
            "id": str(ticket.created_by_id) if ticket.created_by_id else None,
            "email": ticket.created_by.email if ticket.created_by_id else None,
        },
        "subscription": sub,
        "message_count": getattr(ticket, "message_count", None),
    }
    if include_messages:
        messages = ticket.messages.select_related("sender").order_by("created_at")
        data["messages"] = [serialize_message(m) for m in messages]
        data["message_count"] = len(data["messages"])
    return data


@transaction.atomic
def create_ticket(*, company, user, subject: str, body: str, priority: str = TicketPriority.NORMAL):
    subject = (subject or "").strip()[:255]
    body = (body or "").strip()
    if not subject:
        raise ValueError("Subject is required.")
    if not body:
        raise ValueError("Message is required.")
    if priority not in TicketPriority.values:
        priority = TicketPriority.NORMAL

    ticket = SupportTicket.objects.create(
        company=company,
        created_by=user,
        subject=subject,
        status=TicketStatus.OPEN,
        priority=priority,
        admin_unread=True,
        user_unread=False,
    )
    SupportMessage.objects.create(
        ticket=ticket,
        sender=user,
        body=body,
        is_admin_reply=False,
    )
    return ticket


@transaction.atomic
def add_user_message(*, ticket: SupportTicket, user, body: str) -> SupportMessage:
    body = (body or "").strip()
    if not body:
        raise ValueError("Message is required.")
    if ticket.status == TicketStatus.CLOSED:
        raise ValueError("This ticket is closed.")
    msg = SupportMessage.objects.create(
        ticket=ticket,
        sender=user,
        body=body,
        is_admin_reply=False,
    )
    ticket.admin_unread = True
    ticket.user_unread = False
    if ticket.status in (TicketStatus.RESOLVED, TicketStatus.PENDING):
        ticket.status = TicketStatus.OPEN
    ticket.updated_at = timezone.now()
    ticket.save(update_fields=["admin_unread", "user_unread", "status", "updated_at"])
    return msg


@transaction.atomic
def add_admin_message(*, ticket: SupportTicket, admin, body: str) -> SupportMessage:
    body = (body or "").strip()
    if not body:
        raise ValueError("Message is required.")
    msg = SupportMessage.objects.create(
        ticket=ticket,
        sender=admin,
        body=body,
        is_admin_reply=True,
    )
    ticket.user_unread = True
    ticket.admin_unread = False
    if ticket.status == TicketStatus.OPEN:
        ticket.status = TicketStatus.PENDING
    ticket.updated_at = timezone.now()
    ticket.save(update_fields=["user_unread", "admin_unread", "status", "updated_at"])
    return msg


def annotate_message_count(qs):
    return qs.annotate(message_count=Count("messages"))


def open_ticket_count() -> int:
    return SupportTicket.objects.filter(
        status__in=[TicketStatus.OPEN, TicketStatus.PENDING]
    ).count()


def admin_unread_count() -> int:
    return SupportTicket.objects.filter(admin_unread=True).exclude(
        status=TicketStatus.CLOSED
    ).count()


def user_unread_count(user) -> int:
    company = company_for_user(user)
    if not company:
        return 0
    return SupportTicket.objects.filter(
        company=company, user_unread=True
    ).exclude(status=TicketStatus.CLOSED).count()
