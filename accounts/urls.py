from django.urls import path
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileView,
    ChangePasswordView,
    CategoryListCreateView,
    CategoryDetailView,
    TagListCreateView,
    TagDetailView,
    ProductAttributeListCreateView,
    ProductAttributeDetailView,
    ProductListCreateView,
    ProductDetailView,
    StockMovementView,
    StripePaymentView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("tags/", TagListCreateView.as_view(), name="tag-list-create"),
    path("tags/<int:pk>/", TagDetailView.as_view(), name="tag-detail"),
    path(
        "attributes/",
        ProductAttributeListCreateView.as_view(),
        name="attribute-list-create",
    ),
    path(
        "attributes/<int:pk>/",
        ProductAttributeDetailView.as_view(),
        name="attribute-detail",
    ),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("stock-movements/", StockMovementView.as_view()),
    path('stripe-payment/', StripePaymentView.as_view(), name='stripe-payment'),
]
