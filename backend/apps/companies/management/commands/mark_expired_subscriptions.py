"""Mark subscriptions past ends_at as expired (status only — never disables login)."""

from django.core.management.base import BaseCommand

from apps.companies.subscription_services import mark_expired_subscriptions


class Command(BaseCommand):
    help = (
        "Mark trialing/active/past_due subscriptions with ends_at in the past as expired. "
        "Does not disable user accounts."
    )

    def handle(self, *args, **options):
        count = mark_expired_subscriptions()
        self.stdout.write(self.style.SUCCESS(f"Marked {count} subscription(s) expired."))
