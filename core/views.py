from rest_framework import viewsets, status #status added
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny # Import permissions
from rest_framework.response import Response 
from django.utils import timezone #i added
import uuid #i added
from .models import (
    User, Category, Certificate, Listing, ListingMedia,
    AdminAction, SubscriptionPackage, UserSubscription, GreenCreditTransaction
)
from rest_framework.decorators import action  #added
from .serializers import (
    UserSerializer, CategorySerializer, CertificateSerializer, ListingSerializer,
    ListingMediaSerializer, AdminActionSerializer, SubscriptionPackageSerializer,
    UserSubscriptionSerializer, GreenCreditTransactionSerializer
)

# Custom Permission to allow users to only view/edit their own profile
class IsOwnerOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Allow admin users to perform any action
        if request.user and request.user.is_staff:
            return True
        # Allow users to view/edit their own profile
        return obj == request.user
    
FREE_WIPES_ON_REGISTRATION = 3 #i added

GREEN_CREDITS_PER_FREE_WIPE = 10 #i added

GREEN_CREDITS_PER_PAID_WIPE = 20 #i added

# 1. User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('email')
    serializer_class = UserSerializer
    # Apply permissions: Only staff can list all, users can retrieve/update their own
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminUser] # Only admins can list all users
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin] # Users can view/edit their own profile
        else:
            permission_classes = [IsAdminUser] # For create or other actions, default to admin
        return [permission() for permission in permission_classes]


# 2. Category ViewSet - Can be viewed by anyone, but only staff can create/edit/delete
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny] # Anyone can view categories
        else:
            permission_classes = [IsAdminUser] # Only admin can create, update, delete
        return [permission() for permission in permission_classes]



# 3. Certificate ViewSet - Only authenticated users can list/retrieve their own, staff can manage all
class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.none()   #was not there
    serializer_class = CertificateSerializer #was not there
    def get_queryset(self):
        # Only show certificates belonging to the authenticated user, or all for admin
        if self.request.user.is_staff:
            return Certificate.objects.all().order_by('-generated_at')
        return Certificate.objects.filter(user=self.request.user).order_by('-generated_at')
    
    serializer_class = CertificateSerializer #i added
    permission_classes = [IsAuthenticated]  #i added
    
    # left here ????????????? 

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] # Authenticated users can list their own
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Custom permission: User can see/edit their own cert, admin can see/edit any
            permission_classes = [IsAuthenticated]
        else: # For create
            permission_classes = [IsAuthenticated] # Authenticated users can create certificates
        return [permission() for permission in permission_classes]

    # You might want to override perform_create to automatically set the user for a new certificate
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 4. Listing ViewSet - Anyone can view, only owner/admin can edit/delete
class IsListingOwnerOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().select_related('user', 'category', 'certificate').prefetch_related('media').order_by('-created_at')
    serializer_class = ListingSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny] # Anyone can view listings
        elif self.action == 'create':
            permission_classes = [IsAuthenticated] # Only authenticated users can create listings
        else: # update, partial_update, destroy
            permission_classes = [IsListingOwnerOrAdmin] # Only owner or admin can edit/delete
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 5. ListingMedia ViewSet - Publicly viewable, but only listing owner/admin can create/edit/delete
class IsListingMediaOwnerOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.listing.user == request.user

class ListingMediaViewSet(viewsets.ModelViewSet):
    queryset = ListingMedia.objects.all().order_by('listing', 'is_primary')
    serializer_class = ListingMediaSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny] # Anyone can view media
        else: # create, update, partial_update, destroy
            permission_classes = [IsListingMediaOwnerOrAdmin] # Only listing owner or admin can modify
        return [permission() for permission in permission_classes]


# 6. AdminAction ViewSet - Strictly Admin Only
class AdminActionViewSet(viewsets.ModelViewSet):
    queryset = AdminAction.objects.all().order_by('-performed_at')
    serializer_class = AdminActionSerializer
    permission_classes = [IsAdminUser] # Only admin users can view/manage admin actions

    def perform_create(self, serializer):
        serializer.save(admin_user=self.request.user)


# 7. SubscriptionPackage ViewSet - Publicly viewable, staff only for changes
class SubscriptionPackageViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPackage.objects.all().order_by('name')
    serializer_class = SubscriptionPackageSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny] # Anyone can view packages
        else:
            permission_classes = [IsAdminUser] # Only admin can create, update, delete
        return [permission() for permission in permission_classes]


# 8. UserSubscription ViewSet - Only users can see their own, admin can see all
class IsUserSubscriptionOwnerOrAdmin(IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.none()
    serializer_class = UserSubscriptionSerializer
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSubscription.objects.all().select_related('user', 'package').order_by('-start_date')
        return UserSubscription.objects.filter(user=self.request.user).select_related('user', 'package').order_by('-start_date')

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] # Authenticated user can list their own
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsUserSubscriptionOwnerOrAdmin] # Only owner or admin can edit/delete
        else: # For create
            permission_classes = [IsAuthenticated] # Authenticated users can create (e.g., via payment)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 9. GreenCreditTransaction ViewSet - Only users can see their own, admin can see all
class IsGreenCreditTransactionOwnerOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user

class GreenCreditTransactionViewSet(viewsets.ModelViewSet):
    queryset = GreenCreditTransaction.objects.none()
    serializer_class = GreenCreditTransactionSerializer
    def get_queryset(self):
        if self.request.user.is_staff:
            return GreenCreditTransaction.objects.all().select_related('user', 'certificate', 'listing').order_by('-transaction_time')
        return GreenCreditTransaction.objects.filter(user=self.request.user).select_related('user', 'certificate', 'listing').order_by('-transaction_time')

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] # Authenticated user can list their own
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsGreenCreditTransactionOwnerOrAdmin] # Only owner or admin can edit/delete
        else: # For create
            permission_classes = [IsAuthenticated] # Authenticated users can create (e.g., via wipe)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # For GreenCreditTransaction, the user is often implicitly tied to the action
        # For simplicity now, let's assume the request.user is the one making the transaction
        serializer.save(user=self.request.user)