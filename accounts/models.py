from django.db import models
from model_utils import Choices
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator


# Define roles as a tuple of tuples
ROLES = Choices("User", "Admin", "Moderator")


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields and choices for role.
    Extends the default AbstractUser model provided by Django.

    Fields:
        email (EmailField): Unique email address for the user.
        bio (TextField): Optional biography for the user.
        role (CharField): Role of the user, chosen from predefined choices.
    """

    email = models.EmailField(unique=True, verbose_name="Email Address")
    bio = models.TextField(blank=True, null=True, verbose_name="Biography")
    role = models.CharField(
        max_length=50, choices=ROLES, default=ROLES.User, verbose_name="Role"
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    """
    Model to represent a product category.

    Fields:
        name (CharField): Name of the category, must be unique.
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Model to represent a tag for categorizing products.

    Fields:
        name (CharField): Name of the tag, must be unique.
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Tag Name")

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """
    Model to represent an attribute for products, such as size, color, or brand.

    Fields:
        name (CharField): Name of the attribute, must be unique.
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Attribute Name")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model to represent a product.

    Fields:
        name (CharField): Name of the product.
        description (TextField): Description of the product with a minimum length of 1.
        price (DecimalField): Price of the product, must be non-negative.
        category (ForeignKey): Category to which the product belongs.
        tags (ManyToManyField): Tags associated with the product.
        attributes (ForeignKey): Attributes of the product, such as size, color, or brand.
    """

    name = models.CharField(max_length=255, verbose_name="Product Name")
    description = models.TextField(
        validators=[MinLengthValidator(1)], verbose_name="Product Description"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Product Price",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name="Product Category",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Product Tags")
    attributes = models.ForeignKey(
        ProductAttribute, on_delete=models.CASCADE, verbose_name="Product Attributes"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    stock_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    """
    Model to represent stock movements (additions and subtractions).

    Fields:
        product (ForeignKey): Product for which the stock movement occurred.
        movement_type (CharField): Type of movement, either 'addition' or 'subtraction'.
        quantity (IntegerField): Quantity of the movement.
        timestamp (DateTimeField): The datetime when the movement occurred.
        user (ForeignKey): User who performed the movement.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(
        max_length=10,
        choices=[("addition", "Addition"), ("subtraction", "Subtraction")],
    )
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"


class Order(models.Model):
    """
    Model to represent an order.

    Fields:
        user (ForeignKey): User who placed the order.
        status (CharField): Status of the order, chosen from predefined choices.
        total (DecimalField): Total price of the order.
        created_at (DateTimeField): The datetime when the order was created.
        updated_at (DateTimeField): The datetime when the order was last updated.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    Model to represent an item in an order.

    Fields:
        order (ForeignKey): Order to which the item belongs.
        product (ForeignKey): Product that is part of the order.
        quantity (PositiveIntegerField): Quantity of the product in the order.
        price (DecimalField): Price of the product.
    """

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    """
    Model to represent a payment for an order.

    Fields:
        order (OneToOneField): Order for which the payment is made.
        amount (DecimalField): Amount of the payment.
        timestamp (DateTimeField): The datetime when the payment was made.
        success (BooleanField): Whether the payment was successful or not.
        payment_gateway (CharField): Name of the payment gateway used.
    """

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    payment_gateway = models.CharField(max_length=100)

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class CartItem(models.Model):
    """
    Model to represent an item in the shopping cart.

    Fields:
        user (ForeignKey): User who owns the cart item.
        product (ForeignKey): Product that is part of the cart.
        quantity (PositiveIntegerField): Quantity of the product in the cart.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class WishlistItem(models.Model):
    """
    Model to represent an item in the wishlist.

    Fields:
        user (ForeignKey): User who owns the wishlist item.
        product (ForeignKey): Product that is part of the wishlist.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class Address(models.Model):
    """
    Model to represent an address.

    Fields:
        user (ForeignKey): User who owns the address.
        name (CharField): Name associated with the address.
        address_line_1 (CharField): First line of the address.
        address_line_2 (CharField): Second line of the address, optional.
        city (CharField): City of the address.
        state (CharField): State of the address.
        zip_code (CharField): ZIP code of the address.
        country (CharField): Country of the address.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"


class Discount(models.Model):
    """
    Model to represent a discount.

    Fields:
        code (CharField): Code of the discount.
        discount_type (CharField): Type of the discount, either 'percentage' or 'fixed'.
        discount_amount (DecimalField): Amount of the discount.
    """

    code = models.CharField(max_length=20)
    discount_type = models.CharField(
        max_length=20, choices=[("percentage", "Percentage"), ("fixed", "Fixed")]
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code
