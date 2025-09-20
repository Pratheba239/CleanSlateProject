from django.contrib import admin
from .models import (
    User, Category, Certificate, Listing, ListingMedia,
    AdminAction, SubscriptionPackage, UserSubscription, GreenCreditTransaction
)

# 1. Custom User Model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'phone_number', 'is_staff', 'is_active', 'green_credits')
    list_filter = ('is_staff', 'is_active', 'current_subscription_package')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

# 2. Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'description')
    list_filter = ('parent_category',)
    search_fields = ('name', 'description')
    ordering = ('name',)

# 3. Certificate Model
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device_serial_number', 'wiping_method', 'status', 'completed_at', 'is_invalidated')
    list_filter = ('status', 'wiping_method', 'device_type', 'operating_system', 'is_invalidated')
    search_fields = ('device_serial_number', 'user__email', 'blockchain_tx_hash')
    raw_id_fields = ('user',) # Use raw_id_fields for FK to User for better performance with many users

# 4. Listing Model
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'price', 'category', 'condition', 'status', 'created_at', 'is_redeemable_with_green_credits')
    list_filter = ('status', 'condition', 'category', 'is_redeemable_with_green_credits')
    search_fields = ('title', 'description', 'user__email', 'brand', 'model_name')
    raw_id_fields = ('user', 'certificate')
    date_hierarchy = 'created_at'

# 5. ListingMedia Model
@admin.register(ListingMedia)
class ListingMediaAdmin(admin.ModelAdmin):
    list_display = ('listing', 'media_type', 'is_primary', 'file_url')
    list_filter = ('media_type', 'is_primary')
    search_fields = ('listing__title', 'file_url')
    raw_id_fields = ('listing',)

# 6. AdminAction Model
@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action_type', 'target_table', 'target_id', 'performed_at', 'ip_address')
    list_filter = ('action_type', 'target_table')
    search_fields = ('admin_user__email', 'action_type', 'target_table', 'target_id', 'reason')
    raw_id_fields = ('admin_user',)
    date_hierarchy = 'performed_at'

# 7. SubscriptionPackage Model
@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'wipes_allowed', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

# 8. UserSubscription Model
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'status', 'start_date', 'end_date', 'wipes_used')
    list_filter = ('status', 'package')
    search_fields = ('user__email', 'package__name')
    raw_id_fields = ('user', 'package')
    date_hierarchy = 'start_date'

# 9. GreenCreditTransaction Model
@admin.register(GreenCreditTransaction)
class GreenCreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'transaction_time', 'certificate', 'listing')
    list_filter = ('transaction_type',)
    search_fields = ('user__email', 'description')
    raw_id_fields = ('user', 'certificate', 'listing')
    date_hierarchy = 'transaction_time'