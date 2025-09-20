from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CategoryViewSet, CertificateViewSet, ListingViewSet,
    ListingMediaViewSet, AdminActionViewSet, SubscriptionPackageViewSet,
    UserSubscriptionViewSet, GreenCreditTransactionViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'certificates', CertificateViewSet)
router.register(r'listings', ListingViewSet)
router.register(r'listing-media', ListingMediaViewSet)
router.register(r'admin-actions', AdminActionViewSet)
router.register(r'subscription-packages', SubscriptionPackageViewSet)
router.register(r'user-subscriptions', UserSubscriptionViewSet)
router.register(r'green-credit-transactions', GreenCreditTransactionViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]