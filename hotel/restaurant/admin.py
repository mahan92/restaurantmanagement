from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Contact, Food, Drink, Soup, Res, UserRegistration

ALLOWED_ADMIN_USERNAME = 'Mahantesh_24'

# Check if the logged-in user is the admin
def check_if_admin(user):
    if user.username != ALLOWED_ADMIN_USERNAME:
        raise PermissionDenied("You do not have permission to access this area.")

# FoodAdmin Class
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'cuisine')
    search_fields = ('name', 'cuisine')

    def hot_selling_food(self, obj):
        # Get the top 5 hot-selling foods by the count of orders
        hot_selling = Res.objects.values('food').annotate(order_count=Count('food')).order_by('-order_count')[:5]

        # Get the actual Food objects for the ids
        food_sales = []
        for item in hot_selling:
            food = get_object_or_404(Food, id=item['food'])
            food_sales.append(f"{food.name} - Sold: {item['order_count']} orders")

        return ", ".join(food_sales)

    hot_selling_food.short_description = 'Top 5 Hot Selling Food'

# DrinkAdmin Class
class DrinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

    def hot_selling_drinks(self, obj):
        hot_selling = Res.objects.values('drinks').annotate(order_count=Count('drinks')).order_by('-order_count')[:5]

        drink_sales = []
        for item in hot_selling:
            drink = get_object_or_404(Drink, id=item['drinks'])
            drink_sales.append(f"{drink.name} - Sold: {item['order_count']} orders")

        return ", ".join(drink_sales)

    hot_selling_drinks.short_description = 'Top 5 Hot Selling Drinks'

# SoupAdmin Class
class SoupAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

    def hot_selling_soups(self, obj):
        hot_selling = Res.objects.values('soups').annotate(order_count=Count('soups')).order_by('-order_count')[:5]

        soup_sales = []
        for item in hot_selling:
            soup = get_object_or_404(Soup, id=item['soups'])
            soup_sales.append(f"{soup.name} - Sold: {item['order_count']} orders")

        return ", ".join(soup_sales)

    hot_selling_soups.short_description = 'Top 5 Hot Selling Soups'

# ResAdmin Class (with dynamic total amount calculation)
class ResAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'food', 'drinks', 'soups', 'quantity', 'order_type', 'date', 'dynamic_total_amount')
    search_fields = ('user__username', 'food__name', 'drinks__name', 'soups__name')
    list_filter = ('order_type', 'date')
    list_per_page = 20

    def get_user(self, obj):
        return obj.user.username if obj.user else obj.uname  # Display 'uname' if no user linked
    get_user.short_description = 'User'

    def dynamic_total_amount(self, obj):
        """ Calculate the total amount dynamically. """
        if obj.food and obj.drinks and obj.soups and obj.quantity:
            # Calculating the total amount based on quantity and prices of each item
            total_amount = (obj.food.price * obj.quantity) + (obj.drinks.price * obj.quantity) + (obj.soups.price * obj.quantity)
            return f"₹{total_amount:.2f}"  # Formatting the total as currency
        return "₹0.00"  # Return 0 if any of the items are missing

    dynamic_total_amount.short_description = 'Total Amount'

    def get_model_perms(self, request):
        check_if_admin(request.user)
        return super().get_model_perms(request)

# ContactAdmin Class
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

# UserRegistrationAdmin Class
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')

# Register all models
admin.site.register(Food, FoodAdmin)
admin.site.register(Drink, DrinkAdmin)
admin.site.register(Soup, SoupAdmin)
admin.site.register(Res, ResAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(UserRegistration, UserRegistrationAdmin)
