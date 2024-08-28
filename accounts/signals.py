from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def send_stock_level_notification(sender, instance, **kwargs):
    if instance.stock_level <= 10:
        # To do
        # Send notification (e.g., email, SMS, etc.)
        print(f"Low stock level notification for {instance.name}")
