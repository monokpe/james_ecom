import stripe
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes

from django.conf import settings
from .models import (
    Product,
    Category,
    Tag,
    ProductAttribute,
    Order,
    OrderItem,
    Payment,
    CartItem,
    WishlistItem,
    Address,
)
from .serializers import (
    CustomUserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ProductSerializer,
    CategorySerializer,
    TagSerializer,
    ProductAttributeSerializer,
    StockMovementSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
    CartItemSerializer,
    WishlistItemSerializer,
    AddressSerializer,
    OrderSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                return Response(
                    {"detail": "Password updated successfully."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateView(generics.ListCreateAPIView):
    """Category list create view"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Category detail view"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagListCreateView(generics.ListCreateAPIView):
    """Tag list create view"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Tag detail view"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ProductAttributeListCreateView(generics.ListCreateAPIView):
    """Product attribute list create view"""

    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer


class ProductAttributeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Product attribute detail view"""

    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """Product list create view"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "category__name", "tags__name"]
    ordering_fields = ["name", "price"]
    permission_classes = [permissions.IsAuthenticated]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Product detail view"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class StockMovementView(APIView):
    def post(self, request):
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            product = serializer.validated_data["product"]
            if serializer.validated_data["movement_type"] == "addition":
                product.stock_level += serializer.validated_data["quantity"]
            else:
                if product.stock_level < serializer.validated_data["quantity"]:
                    return Response(
                        {"error": "Insufficient stock for this operation."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                product.stock_level -= serializer.validated_data["quantity"]
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        if not order.items.exists():
            order.delete()
            return Response(
                {"error": "Order must have at least one item."},
                status=status.HTTP_400_BAD_REQUEST,
            )



class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def order_item_create_view(request):
    serializer = OrderItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def payment_create_view(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save()
        if payment.success:
            order = payment.order
            order.status = "PROCESSING"
            order.save()
            send_mail(
                "Order Confirmation",
                f"Your order {order.id} has been processed successfully.",
                "from@example.com",
                [request.user.email],
            )
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


class CartItemListCreateView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class WishlistItemListCreateView(generics.ListCreateAPIView):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class AddressListCreateView(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        # TO DO
        # Perform additional actions like payment processing, shipping calculations, tax calculations, etc.
        # For example, assuming `calculate_shipping` and `calculate_taxes` are utility functions:
        # shipping_cost = calculate_shipping(order)
        # taxes = calculate_taxes(order)
        # order.total += shipping_cost + taxes
        # order.save()


class StripePaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=serializer.validated_data["amount"]
                    * 100,  # Convert to cents
                    currency="usd",
                    payment_method_types=["card"],
                )
                # Create a Payment record in the database
                payment = Payment.objects.create(
                    amount=serializer.validated_data["amount"],
                    payment_method="card",
                )
                return Response(
                    {"clientSecret": intent.client_secret},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
