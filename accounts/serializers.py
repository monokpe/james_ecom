from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Product,
    Category,
    Tag,
    ProductAttribute,
    StockMovement,
    Order,
    OrderItem,
    Payment,
    CartItem,
    WishlistItem,
    Address,
    Discount,
)


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "role")
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = CustomUserSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    attributes = ProductAttribute()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "tags",
            "attributes",
            "stock_level",
        ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            category_data = validated_data.pop("category")
            tags_data = validated_data.pop("tags")
            attributes = validated_data.pop("attributes")

            category = Category.objects.get_or_create(name=category_data["name"])[0]
            tags = [
                Tag.objects.get_or_create(name=tag_data["name"])[0]
                for tag_data in tags_data
            ]

            product = Product.objects.create(category=category, **validated_data)
            product.tags.set(tags)
            product.attributes = attributes
            product.save()

            return product
        except Exception as e:
            raise ValidationError(str(e))

    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            category_data = validated_data.pop("category", None)
            tags_data = validated_data.pop("tags", None)
            attributes = validated_data.pop("attributes", None)

            if category_data:
                instance.category = Category.objects.get_or_create(
                    name=category_data["name"]
                )[0]

            if tags_data:
                instance.tags.set(
                    [
                        Tag.objects.get_or_create(name=tag_data["name"])[0]
                        for tag_data in tags_data
                    ]
                )

            if attributes:
                instance.attributes = attributes

            instance.__dict__.update(
                {
                    k: v
                    for k, v in validated_data.items()
                    if k not in ["category", "tags", "attributes"]
                }
            )
            instance.save()

            return instance
        except Exception as e:
            raise ValidationError(str(e))


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "product", "movement_type", "quantity", "timestamp"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "user",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "zip_code",
            "country",
        ]


class OrderSerializer(serializers.ModelSerializer):
    billing_address = AddressSerializer()
    shipping_address = AddressSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total",
            "created_at",
            "updated_at",
            "billing_address",
            "shipping_address",
            "items",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["order", "amount", "timestamp", "success", "payment_gateway"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "user", "product", "quantity"]


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ["id", "user", "product"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id", "code", "discount_type", "discount_amount"]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'payment_date']