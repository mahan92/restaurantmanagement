from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


# Model to store contact information (general inquiries, etc.)
class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.name


# Model to store contact information (another form, if needed)
class Contact2(models.Model):
    name2 = models.CharField(max_length=122)
    email2 = models.EmailField(max_length=122)
    phone2 = models.CharField(max_length=12)

    def __str__(self):
        return self.name2


# Model to store branch details
class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name


# Model to store user registration details (Custom User Model)
class UserRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null temporarily
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# Model to store user profile with branch preference
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    # Method to ensure that each user has a corresponding UserProfile
    @staticmethod
    def create_user_profile(user, branch=None):
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(user=user, branch=branch)


# Ensure that user profile is created automatically when a new user is registered
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.create_user_profile(user=instance)


# Model to store food items and their prices
class Food(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cuisine = models.CharField(choices=[('Vegetarian', 'Vegetarian'), ('Non-Vegetarian', 'Non-Vegetarian')], max_length=20, null=True)
    image_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Model to store Drink items
class Drink(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Model to store Soup items
class Soup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Model to store orders (Food, Drink, Soup items)
class Res(models.Model):
    uname = models.CharField(max_length=122, null=True)  # Name of the person placing the order
    date = models.DateField(default=timezone.now)  # Date of the order
    email = models.EmailField(null=True)  # Email of the person placing the order
    number = models.CharField(max_length=15, null=True)  # Contact number
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True)  # Food item (FK to Food model)
    drinks = models.ForeignKey(Drink, on_delete=models.CASCADE, blank=True, null=True)  # Optional: Drinks item (FK to Drink model)
    soups = models.ForeignKey(Soup, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(null=True)  # Quantity of the food
    order_type = models.CharField(max_length=50, choices=[('dine_in', 'Dine In'), ('takeaway', 'Takeaway')], default='dine_in')  # Order type (Dine-in or Takeaway)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='orders', null=True)  # Link order to a branch

    def __str__(self):
        return f"Order by {self.uname} on {self.date}"

    @property
    def total_food_price(self):
        return self.food.price * self.quantity if self.food else 0

    @property
    def total_drinks_price(self):
        return self.drinks.price * self.quantity if self.drinks else 0

    @property
    def total_soups_price(self):
        return self.soups.price * self.quantity if self.soups else 0

    @property
    def subtotal(self):
        return self.total_food_price + self.total_drinks_price + self.total_soups_price

    @property
    def gst(self):
        return self.subtotal * Decimal('0.02')

    @property
    def total_amount(self):
        return self.subtotal + self.gst


# Model to store Sales data per branch
class Sales(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="sales")
    food_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    drink_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    soup_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date = models.DateField(auto_now_add=True)

    def update_sales(self):
        # Update the total sales for the branch
        self.total_sales = self.food_sales + self.drink_sales + self.soup_sales
        self.save()

    def __str__(self):
        return f"Sales for {self.branch.name} on {self.date}"
