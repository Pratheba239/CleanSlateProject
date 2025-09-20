from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from .models import (
    User, Category, Certificate, Listing, ListingMedia,
    AdminAction, SubscriptionPackage, UserSubscription, GreenCreditTransaction
)

# 1. User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone_number',
            'current_subscription_package', 'wipes_remaining', 'green_credits',
            'is_staff', 'is_active', 'date_joined', 'updated_at'
        )
        read_only_fields = ('id', 'is_staff', 'is_active', 'date_joined', 'updated_at', 'wipes_remaining', 'green_credits','free_wipes_used')


# 2. Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent_category')


# 3. Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email') # Display user's email, not just ID

    class Meta:
        model = Certificate
        fields = (
            'id', 'user', 'user_email', 'device_serial_number', 'wiping_method', 'status',
            'wiped_at', 'completed_at', 'device_type', 'operating_system',
            'health_score_at_wipe', 'blockchain_tx_hash', 'qr_code_data',
            'generated_at', 'is_invalidated'
        )
        read_only_fields = ('id', 'generated_at', 'user_email','health_score_at_wipe','device_serial_number') #i added with concern , chetan bagat


# 4. ListingMedia Serializer (nested for Listing)
class ListingMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingMedia
        fields = ('id', 'file_url', 'media_type', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')


# 5. Listing Serializer
class ListingSerializer(serializers.ModelSerializer):
    media = ListingMediaSerializer(many=True, read_only=True) # Nested serializer for media
    category_name = serializers.ReadOnlyField(source='category.name')
    user_email = serializers.ReadOnlyField(source='user.email')
    certificate_id = serializers.ReadOnlyField(source='certificate.id')

    class Meta:
        model = Listing
        fields = (
            'id', 'user', 'user_email', 'title', 'description', 'price',
            'category', 'category_name', 'brand', 'model_name', 'condition',
            'health_score', 'status', 'created_at', 'updated_at',
            'is_redeemable_with_green_credits', 'green_credit_price',
            'certificate', 'certificate_id', 'media'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'user_email', 'category_name', 'certificate_id', 'media')


# 6. AdminAction Serializer
class AdminActionSerializer(serializers.ModelSerializer):
    admin_user_email = serializers.ReadOnlyField(source='admin_user.email')

    class Meta:
        model = AdminAction
        fields = (
            'id', 'admin_user', 'admin_user_email', 'action_type',
            'target_table', 'target_id', 'performed_at', 'reason', 'ip_address'
        )
        read_only_fields = ('id', 'performed_at', 'admin_user_email')


# 7. SubscriptionPackage Serializer
class SubscriptionPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPackage
        fields = ('id', 'name', 'description', 'wipes_allowed', 'price', 'is_active')
        read_only_fields = ('id',)


# 8. UserSubscription Serializer
class UserSubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    package_name = serializers.ReadOnlyField(source='package.name')

    class Meta:
        model = UserSubscription
        fields = (
            'id', 'user', 'user_email', 'package', 'package_name',
            'start_date', 'end_date', 'status', 'initial_wipes_allocated',
            'wipes_used', 'payment_details'
        )
        read_only_fields = ('id', 'start_date', 'user_email', 'package_name', 'wipes_used')


# 9. GreenCreditTransaction Serializer
class GreenCreditTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    certificate_id = serializers.ReadOnlyField(source='certificate.id')
    listing_id = serializers.ReadOnlyField(source='listing.id')

    class Meta:
        model = GreenCreditTransaction
        fields = (
            'id', 'user', 'user_email', 'certificate', 'certificate_id',
            'listing', 'listing_id', 'transaction_type', 'amount',
            'transaction_time', 'description'
        )
        read_only_fields = ('id', 'transaction_time', 'user_email', 'certificate_id', 'listing_id')




# 1. Custom UserCreate Serializer for Djoser
class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name', 'phone_number'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}, # Ensure email is required
        }