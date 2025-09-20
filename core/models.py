import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser # For custom user model
from django.utils.translation import gettext_lazy as _ # For internationalization if needed

# 1. Custom User Model
class User(AbstractUser):
    # Override the default auto-incrementing ID with a UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Use email as the unique identifier for login. AbstractUser already has 'email',
    # but we ensure it's unique and can be used for authentication.
    # Set USERNAME_FIELD = 'email' in settings.py and manage.py creatsuperuser will ask for email
    # username can remain, but be made optional if email is primary login
    # If you want username to be nullable, it must be removed from REQUIRED_FIELDS in your custom User manager.
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True) # Making username optional

    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Subscription details - link to current package
    current_subscription_package = models.ForeignKey(
        'SubscriptionPackage',
        on_delete=models.SET_NULL, # If a package is deleted, user's current_package becomes NULL
        null=True, blank=True,
        related_name='current_users'
    )
    wipes_remaining = models.IntegerField(default=0) # Wipes remaining based on current package

    green_credits = models.IntegerField(default=0) # Current balance of green credits

    free_wipes_used=models.IntegerField(default=0) #i added

    updated_at = models.DateTimeField(auto_now=True) # Automatically updates on save

    # Ensure AbstractUser's username is not required if email is USERNAME_FIELD
    # (Django will handle this if you set USERNAME_FIELD in settings.py)
    # If you choose to keep username as the USERNAME_FIELD, make sure 'email' is in REQUIRED_FIELDS

    # Custom manager if you decide to use email as USERNAME_FIELD and manage 'username' explicitly.
    # For now, let's keep it simple and ensure email is unique.
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.email or str(self.id)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# Set the custom user model in settings.py
# AUTH_USER_MODEL = 'core.User'
# To be added to settings.py after defining this model.

# 2. Category Model (Product Categories for Reseller Platform)
class Category(models.Model):
    id = models.AutoField(primary_key=True) # Simple auto-incrementing integer PK
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey(
        'self', # Self-referential FK for hierarchical categories (e.g., 'Laptops' -> 'Gaming Laptops')
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = 'Categories' # Correct pluralization in admin

    def __str__(self):
        return self.name

# 3. Certificate Model (Digital Certificate for Wipes)
class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # UUID for unique cert IDs
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    device_serial_number = models.CharField(max_length=255, unique=True) # Unique per device wiped

    WIPING_METHOD_CHOICES = [
        ('nist_clear', 'NIST 800-88 Clear'),
        ('nist_purge', 'NIST 800-88 Purge'),
        ('dod_5220_22m', 'DoD 5220.22-M'),
        ('other', 'Other Method'),
    ]
    wiping_method = models.CharField(max_length=100, choices=WIPING_METHOD_CHOICES)

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    wiped_at = models.DateTimeField() # When the wiping operation began (provided by client)
    completed_at = models.DateTimeField(blank=True, null=True) # When it finished

    DEVICE_TYPE_CHOICES = [
        ('hdd', 'HDD'), ('ssd', 'SSD'), ('emmc', 'eMMC'), ('nvme', 'NVMe'), ('other', 'Other')
    ]
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES, blank=True, null=True)

    OS_CHOICES = [
        ('windows', 'Windows'), ('linux', 'Linux'), ('android', 'Android'), ('macos', 'macOS'), ('ios', 'iOS'), ('other', 'Other')
    ]
    operating_system = models.CharField(max_length=50, choices=OS_CHOICES, blank=True, null=True)

    health_score_at_wipe = models.IntegerField(blank=True, null=True) # Estimated health score
    blockchain_tx_hash = models.CharField(max_length=255, unique=True, blank=True, null=True) # Transaction hash on Polygon
    qr_code_data = models.TextField(blank=True, null=True) # Data encoded in the QR code
    generated_at = models.DateTimeField(auto_now_add=True) # When the certificate record was created in the DB
    is_invalidated = models.BooleanField(default=False)

    def __str__(self):
        return f"Cert {self.id} for {self.device_serial_number}"

# 4. Listing Model (Reseller Platform Listings)
class Listing(models.Model):
    id = models.BigAutoField(primary_key=True) # Django default auto-incrementing ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings') # User who posted the listing
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Selling price
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)

    CONDITION_CHOICES = [
        ('new', 'New'), ('like_new', 'Used - Like New'),
        ('good', 'Used - Good'), ('fair', 'Used - Fair'), ('poor', 'Used - Poor'),
    ]
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='good')

    health_score = models.IntegerField(blank=True, null=True) # From Device Health Analysis at time of listing
    
    STATUS_CHOICES = [
        ('active', 'Active'), ('sold', 'Sold'), ('pending', 'Pending'),
        ('withdrawn', 'Withdrawn'), ('draft', 'Draft')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_redeemable_with_green_credits = models.BooleanField(default=False)
    green_credit_price = models.IntegerField(blank=True, null=True, help_text="Number of green credits required for purchase")

    # Link to a Certificate if this listing is for a device wiped by Clean Slate
    certificate = models.OneToOneField(
        Certificate,
        on_delete=models.SET_NULL, # If certificate is deleted, don't delete listing
        null=True, blank=True,
        related_name='listed_device',
        help_text="Link to the Clean Slate certificate if this device was wiped by the platform"
    )

    def __str__(self):
        return self.title

# 5. ListingMedia Model (Images/Videos for Listings)
class ListingMedia(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='media')
    file_url = models.URLField(max_length=500) # URL to the stored image/video (e.g., S3, CDN)
    
    MEDIA_TYPE_CHOICES = [('image', 'Image'), ('video', 'Video')]
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='image')
    
    is_primary = models.BooleanField(default=False) # Indicates the main cover photo
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures only one primary image per listing
        unique_together = ('listing', 'is_primary')
        indexes = [
            models.Index(fields=['listing']), # For faster lookups of media for a listing
        ]

    def __str__(self):
        return f"{self.listing.title} - {self.media_type} ({'Primary' if self.is_primary else 'Secondary'})"

# 6. AdminAction Model (Auditing Admin Activities)
class AdminAction(models.Model):
    id = models.BigAutoField(primary_key=True)
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=100) # e.g., 'delete_listing', 'suspend_user'
    target_table = models.CharField(max_length=100, blank=True, null=True) # e.g., 'listings', 'users'
    target_id = models.CharField(max_length=255, blank=True, null=True) # ID of the affected item (UUID, INT, etc., stored as text)
    performed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True) # IP address from which action was initiated

    def __str__(self):
        user_email = self.admin_user.email if self.admin_user else "N/A"
        return f"{user_email} - {self.action_type} on {self.target_table}:{self.target_id}"

# 7. SubscriptionPackage Model (Predefined Packages)
class SubscriptionPackage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    wipes_allowed = models.IntegerField(default=0, help_text="Number of wipes allowed (0 for unlimited)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Monetary cost
    is_active = models.BooleanField(default=True)

    #i added
    green_credits_awarded = models.IntegerFiel(
        default=0,
        help_text="Total green credits awarded upon purchasing this package."
    )

    def __str__(self):
        return self.name

# 8. UserSubscription Model (Tracking user's historical and current subscriptions)
class UserSubscription(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.PROTECT, related_name='user_subscriptions') # PROTECT to prevent deleting packages with active subs
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True) # Null for indefinite or until cancelled

    STATUS_CHOICES = [
        ('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled'), ('trial', 'Trial'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    initial_wipes_allocated = models.IntegerField(blank=True, null=True) # How many wipes were initially granted by THIS subscription
    wipes_used = models.IntegerField(default=0)
    # Using JSONField for flexible metadata from payment gateways (PostgreSQL's JSONB)
    payment_details = models.JSONField(blank=True, null=True) # e.g., Stripe subscription ID, transaction details

    def __str__(self):
        return f"{self.user.email}'s {self.package.name} subscription"

# 9. GreenCreditTransaction Model (Auditing Green Credits)
class GreenCreditTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='green_credit_transactions')
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='credit_transactions',
        help_text="If credits were awarded for a wipe."
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='credit_redemptions',
        help_text="If credits were used to purchase a listing."
    )
    
    TRANSACTION_TYPE_CHOICES = [
        ('awarded_wipe', 'Awarded for Wipe'),
        ('redeemed_purchase', 'Redeemed for Purchase'),
        ('admin_adjustment', 'Admin Adjustment'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    ]
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.IntegerField() # Positive for awarded, negative for redeemed
    transaction_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        user_email = self.user.email if self.user else "N/A"
        return f"User {user_email} {self.transaction_type} {self.amount} credits"