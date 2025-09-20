# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, GreenCreditTransaction

# Configuration for initial free wipes and credits
FREE_WIPES_ON_REGISTRATION = 3
GREEN_CREDITS_PER_FREE_WIPE = 10 # Adjust as per your business model, e.g., 10 credits per wipe

@receiver(post_save, sender=User)
def grant_free_wipes_and_credits_on_registration(sender, instance, created, **kwargs):
    if created and instance.is_superuser == False: # Only for new, non-superuser accounts
        # Grant free wipes
        instance.wipes_remaining += FREE_WIPES_ON_REGISTRATION

        # Grant initial green credits for free wipes
        initial_green_credits = FREE_WIPES_ON_REGISTRATION * GREEN_CREDITS_PER_FREE_WIPE
        instance.green_credits += initial_green_credits

        # Save the user instance to persist the changes
        instance.save(update_fields=['wipes_remaining', 'green_credits'])

        # Optionally, create a GreenCreditTransaction for transparency
        GreenCreditTransaction.objects.create(
            user=instance,
            transaction_type='awarded_wipe',
            amount=initial_green_credits,
            description=f"Initial {initial_green_credits} green credits awarded for {FREE_WIPES_ON_REGISTRATION} free wipes on registration."
        )

        print(f"User {instance.email} registered. Granted {FREE_WIPES_ON_REGISTRATION} free wipes and {initial_green_credits} green credits.")