from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from datetime import datetime

class User(AbstractUser):
    """
    Default custom user model for KillGPT.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    lifetime_assignment_usage = models.IntegerField(default=0)  # Lifetime usage of assignment feature
    monthly_assignment_usage = models.IntegerField(default=0)  # Monthly usage of assignment feature
    lifetime_detector_usage = models.IntegerField(default=0)  # Lifetime usage of detector
    monthly_detector_usage = models.IntegerField(default=0)  # Monthly usage of detector
    last_assignment_usage_update = models.DateTimeField(null=True)  # Last assignment usage update timestamp
    last_detector_usage_update = models.DateTimeField(null=True)  # Last detector usage update timestamp
    total_assignments_created = models.PositiveIntegerField(default=0)  # Total number of assignments created
    average_assignment_percentage = models.FloatField(default=0.0)  # Average percentage of all assignments
    subscription = models.ForeignKey(
        'djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
        help_text="The user's Stripe Subscription object, if it exists"
    )
    customer = models.ForeignKey(
        'djstripe.Customer', null=True, blank=True, on_delete=models.SET_NULL,
        help_text="The user's Stripe Customer object, if it exists"
    )    
    # subscription = models.ForeignKey(
    #     'djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
    #     help_text="The user's Stripe Subscription object, if it exists"
    # )
    # customer = models.ForeignKey(
    #     'djstripe.Customer', null=True, blank=True, on_delete=models.SET_NULL,
    #     help_text="The user's Stripe Customer object, if it exists"
    # )    
    def get_absolute_url(self):
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def update_monthly_assignment_usage(self):
        now = datetime.now()
        current_month = now.month
        if not self.last_assignment_usage_update or self.last_assignment_usage_update.month != current_month:
            # If there was no update this month, reset the usage count
            self.last_assignment_usage_update = now
            self.monthly_assignment_usage = 1
        else:
            # Increment the usage count for the current month
            self.monthly_assignment_usage += 1

    def update_monthly_detector_usage(self):
        now = datetime.now()
        current_month = now.month
        if not self.last_detector_usage_update or self.last_detector_usage_update.month != current_month:
            # If there was no update this month, reset the usage count
            self.last_detector_usage_update = now
            self.monthly_detector_usage = 1
        else:
            # Increment the usage count for the current month
            self.monthly_detector_usage += 1

    def update_lifetime_assignment_usage(self):
        self.lifetime_assignment_usage += 1

    def update_lifetime_detector_usage(self):
        self.lifetime_detector_usage += 1
