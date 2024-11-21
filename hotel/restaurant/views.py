from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Res, Food, Drink, Soup, UserRegistration, Contact2, Contact, Branch, Sales, UserProfile
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np
import mplcursors


# Hello World or Test view
def fun(request):
    return HttpResponse("Hello from first Django project")

# Home Page View
def launch(request):
    context = {
        'variable': "this is sent"
    }
    return render(request, "home.html", context)
def register(request):
    # For GET requests, pass the list of branches to the template
    branches = Branch.objects.all()
    return render(request, "register.html", {'branches': branches})


# About Page View
def about(request):
    return render(request, "about.html")

# Services Page View
def services(request):
    return render(request, "services.html")

# Contact Form View - Saving contact data to the database
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Save the contact information into the Contact model
        contact = Contact(name=name, email=email, phone=phone)
        contact.save()

        # Flash success message
        messages.success(request, "Contact information submitted successfully!")
        return redirect('contact')  # Redirect back to the contact page after submission

    return render(request, "contact.html")

# Success Page View
def success(request):
    name = request.GET['user']
    return HttpResponse(f"LOGIN SUCCESSFUL...!!WELCOME {name}")

# Web2 Form View - Saving the information into the database
def web2(request,branch_name=None):
    if request.method == "POST":
        name2 = request.POST.get('name2')
        email2 = request.POST.get('email2')
        phone2 = request.POST.get('phone2')

        # Save the contact information into the Contact2 model
        web2 = Contact2(name2=name2, email2=email2, phone2=phone2)
        web2.save()
        branch_name = request.GET.get('branch_name', 'No branch selected')

        messages.success(request, "Information submitted successfully!")
        return redirect('web2')  # Redirect back to the web2 page after submission

    return render(request, 'web2.html', {'branch_name': branch_name})


def zomato(request):
    if request.method == "POST":
        uname = request.POST.get('uname')
        date = request.POST.get('date')
        email = request.POST.get('email')
        number = request.POST.get('number')
        food_name = request.POST.get('food')
        drinks_id = request.POST.get('drinks')
        soups_name = request.POST.get('soups')
        quantity = request.POST.get('quantity')
        order_type = request.POST.get('order')

        # Validate quantity
        if not quantity.isdigit() or int(quantity) <= 0:
            messages.error(request, "Quantity must be a positive number.")
            return redirect('zomato')

        quantity = int(quantity)

        try:
            food = Food.objects.get(name=food_name)
        except Food.DoesNotExist:
            messages.error(request, "Food item not found.")
            return redirect('zomato')

        drink = None
        drink_price = 0
        if drinks_id:
            try:
                drink = Drink.objects.get(id=drinks_id)
                drink_price = drink.price
            except Drink.DoesNotExist:
                messages.error(request, "Drink item not found.")
                return redirect('zomato')

        soup = None
        soup_price = 0
        if soups_name:
            try:
                soup = Soup.objects.get(name=soups_name)
                soup_price = soup.price
            except Soup.DoesNotExist:
                messages.error(request, "Soup item not found.")
                return redirect('zomato')

        # Convert prices to Decimal
        food_price = Decimal(food.price)
        drink_price = Decimal(drink_price) if drink else Decimal(0)
        soup_price = Decimal(soup_price) if soup else Decimal(0)

        # Convert quantity to Decimal
        quantity_decimal = Decimal(quantity)

        # Calculate totals
        total_food = food_price * quantity_decimal
        total_drinks = drink_price * quantity_decimal
        total_soups = soup_price * quantity_decimal

        # Subtotal and GST calculation
        subtotal = total_food + total_drinks + total_soups
        gst = subtotal * Decimal(0.02)  # 2% GST
        total_amount = subtotal + gst

        # Save the order
        order = Res(
            uname=uname,
            date=date,
            email=email,
            number=number,
            food=food,
            drinks=drink,
            soups=soup,
            quantity=quantity,
            order_type=order_type
        )
        order.save()

        # Return the rendered bill page
        return render(request, 'zomato_bill.html', {
            'food': food,
            'drink': drink,
            'soup': soup,
            'quantity': quantity,
            'food_price': food_price,
            'drink_price': drink_price,
            'soup_price': soup_price,
            'total_food': total_food,
            'total_drinks': total_drinks,
            'total_soups': total_soups,
            'subtotal': subtotal,
            'gst': gst,
            'total_amount': total_amount,
        })

    # If GET request, fetch type of khana (food, drinks, soups)
    vegetarian_foods = Food.objects.filter(cuisine='Vegetarian')
    non_vegetarian_foods = Food.objects.filter(cuisine='Non-Vegetarian')
    drinks = Drink.objects.all()
    soups = Soup.objects.all()

    context = {
        'vegetarian_foods': vegetarian_foods,
        'non_vegetarian_foods': non_vegetarian_foods,
        'drinks': drinks,
        'soups': soups,
        'cuisine': 'Non-Vegetarian',  # You can dynamically update this based on user input
    }

    return render(request, 'zomato.html', context)


ALLOWED_ADMIN_USERNAME = 'Mahantesh_24'

@login_required
def admin_dashboard(request):
    # Ensure the user is the admin
    if request.user.username != ALLOWED_ADMIN_USERNAME:
        raise PermissionDenied("You do not have permission to access this area.")

    # Query for total sales and order history
    total_orders = Res.objects.count()

    # Calculate total sales using the price of each item and quantity
    total_sales = Res.objects.annotate(
        total_food=F('food__price') * F('quantity'),
        total_drinks=F('drinks__price') * F('quantity'),
        total_soups=F('soups__price') * F('quantity')
    ).aggregate(
        total=Sum(F('total_food') + F('total_drinks') + F('total_soups'))
    )['total'] or Decimal(0)

    # Hot selling items (Top 5 by order count) with food, drink, and soup names included
    hot_selling_food = Res.objects.values('food', 'food__name').annotate(order_count=Count('food')).order_by(
        '-order_count')[:5]
    hot_selling_drinks = Res.objects.values('drinks', 'drinks__name').annotate(order_count=Count('drinks')).order_by(
        '-order_count')[:5]
    hot_selling_soups = Res.objects.values('soups', 'soups__name').annotate(order_count=Count('soups')).order_by(
        '-order_count')[:5]

    # Prepare the sales data in a simpler format for the template
    food_sales_list = [{'food_name': item['food__name'], 'order_count': item['order_count']} for item in
                       hot_selling_food]
    drink_sales_list = [{'drink_name': item['drinks__name'], 'order_count': item['order_count']} for item in
                        hot_selling_drinks]
    soup_sales_list = [{'soup_name': item['soups__name'], 'order_count': item['order_count']} for item in
                       hot_selling_soups]

    # Generate the detailed graph and get the path for the image
    food_chart_path = generate_sales_graph()

    # Fetch contacts for the contact table
    contacts = Contact.objects.all()

    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'food_chart_path': food_chart_path,
        'food_sales_list': food_sales_list,
        'drink_sales_list': drink_sales_list,
        'soup_sales_list': soup_sales_list,
        'contacts': contacts,
    }

    return render(request, 'dashboard.html', context)


@login_required
def branch_dashboard(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    # Get sales data for the branch
    sales_data = Sales.objects.filter(branch=branch).aggregate(
        total_food_sales=Sum('food_sales'),
        total_drink_sales=Sum('drink_sales'),
        total_soup_sales=Sum('soup_sales'),
        total_sales=Sum('total_sales')
    )

    context = {
        'branch': branch,
        'sales_data': sales_data,
    }

    return render(request, 'branch_dashboard.html', context)


def generate_sales_graph():
    # Ensure media directory exists
    media_dir = os.path.join(settings.BASE_DIR, 'media')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Query for the top selling items for food, drinks, and soups
    hot_selling_food = Res.objects.values('food', 'food__name').annotate(order_count=Count('food')).order_by(
        '-order_count')[:5]
    hot_selling_drinks = Res.objects.values('drinks', 'drinks__name').annotate(order_count=Count('drinks')).order_by(
        '-order_count')[:5]
    hot_selling_soups = Res.objects.values('soups', 'soups__name').annotate(order_count=Count('soups')).order_by(
        '-order_count')[:5]

    # Extract data for plotting
    food_names = [item['food__name'] for item in hot_selling_food]
    food_orders = [item['order_count'] for item in hot_selling_food]

    drink_names = [item['drinks__name'] for item in hot_selling_drinks]
    drink_orders = [item['order_count'] for item in hot_selling_drinks]

    soup_names = [item['soups__name'] for item in hot_selling_soups]
    soup_orders = [item['order_count'] for item in hot_selling_soups]

    # Make sure all datasets (drinks and soups) have the same length by padding with zeros
    max_len = max(len(drink_names), len(soup_names))

    # Pad the shorter list with zeros
    if len(drink_names) < max_len:
        drink_names += [''] * (max_len - len(drink_names))
        drink_orders += [0] * (max_len - len(drink_orders))

    if len(soup_names) < max_len:
        soup_names += [''] * (max_len - len(soup_names))
        soup_orders += [0] * (max_len - len(soup_orders))

    # Create a 2x2 grid for complex visualization (you can modify this as per the need)
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    # Bar Chart for Top Selling Food
    bars_food = axs[0, 0].barh(food_names, food_orders, color='skyblue', edgecolor='black')
    axs[0, 0].set_title('Top Selling Food')
    axs[0, 0].set_xlabel('Number of Orders')
    axs[0, 0].set_ylabel('Food Items')
    axs[0, 0].invert_yaxis()  # To display the highest bar at the top

    # Hover interaction with mplcursors
    mplcursors.cursor(bars_food, hover=True).connect("add", lambda sel: sel.annotation.set_text(f'Orders: {food_orders[sel.index]}'))

    # Pie Chart for Food Orders Breakdown
    axs[0, 1].pie(food_orders, labels=food_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axs[0, 1].set_title('Food Orders Breakdown')

    # Stacked Bar Chart for Drinks and Soups (Comparing Orders of Food, Drinks, Soups)
    bars_drinks = axs[1, 0].bar(drink_names, drink_orders, label='Drinks', color='lightgreen', width=0.5)
    bottom_vals = np.array(drink_orders)

    # Adding Soups on top of Drinks (Stacked)
    bars_soups = axs[1, 0].bar(soup_names, soup_orders, bottom=bottom_vals, label='Soups', color='lightcoral', width=0.5)
    axs[1, 0].set_title('Drinks and Soups Order Comparison')
    axs[1, 0].set_xlabel('Items')
    axs[1, 0].set_ylabel('Number of Orders')
    axs[1, 0].legend()

    # Line Chart for Trends (Example: trends in order count over time)
    trend_dates = Res.objects.values('date').annotate(order_count=Count('id')).order_by('date')
    trend_dates = [(item['date'], item['order_count']) for item in trend_dates]

    if trend_dates:
        dates, order_counts = zip(*trend_dates)
        axs[1, 1].plot(dates, order_counts, marker='o', color='purple', linestyle='-', linewidth=2)
        axs[1, 1].set_title('Order Count Over Time')
        axs[1, 1].set_xlabel('Date')
        axs[1, 1].set_ylabel('Order Count')
        axs[1, 1].tick_params(axis='x', rotation=45)

    # Save the generated graph
    chart_path = os.path.join(settings.MEDIA_ROOT, 'hot_selling_items_detailed.png')
    plt.savefig(chart_path)
    plt.close()
    return os.path.join(settings.MEDIA_URL, 'hot_selling_items_detailed.png')

    # Return the path



def hot_selling_items(request):
    # Get the top 5 hot selling foods, drinks, and soups by counting their occurrences in the Res model
    hot_selling_foods = Food.objects.annotate(order_count=Count('res')).order_by('-order_count')[:5]
    hot_selling_drinks = Drink.objects.annotate(order_count=Count('res')).order_by('-order_count')[:5]
    hot_selling_soups = Soup.objects.annotate(order_count=Count('res')).order_by('-order_count')[:5]

    context = {
        'hot_selling_foods': hot_selling_foods,
        'hot_selling_drinks': hot_selling_drinks,
        'hot_selling_soups': hot_selling_soups,
    }

    return render(request, 'hot_selling_items.html', context)
def order_history(request):

    orders = Res.objects.all()


    for order in orders:
        total_price = 0
        if order.food:
            total_price += order.food.price * order.quantity
        if order.drinks:
            total_price += order.drinks.price * order.quantity
        if order.soups:
            total_price += order.soups.price * order.quantity
        order.total_price = total_price

    # Context for passing data to the template
    context = {
        'orders': orders,
    }

    return render(request, 'order_history.html', context)
from django.shortcuts import render
from .models import Branch

# View for selecting a branch
def branch_selection(request):
    branches = Branch.objects.all()
    return render(request, 'branch_selection.html', {'branches': branches})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Branch, UserRegistration, UserProfile

def register(request):
    # Fetch all branches to populate the dropdown in the template
    branches = Branch.objects.all()

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # Optional: If you want to store phone number
        password = request.POST.get('password').strip()  # Trim any spaces
        confirm_password = request.POST.get('confirm_password').strip()  # Trim any spaces
        branch_id = request.POST.get('branch')  # Selected branch from the form

        # Validate if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        # Validate password strength (optional, you can add your own logic)
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register')

        try:
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use!")
                return redirect('register')

            # Create the User
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Get the selected branch (if any), default to None if no branch is selected
            branch = Branch.objects.get(id=branch_id) if branch_id else None

            # Create the UserRegistration entry
            user_registration = UserRegistration.objects.create(
                user=user,
                username=username,
                email=email,
                password=password,
                branch=branch
            )

            # Create the UserProfile entry
            UserProfile.create_user_profile(user=user, branch=branch, phone_number=phone)

            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')  # Redirect to the login page after successful registration

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('register')

    # For GET requests, just render the registration form along with branches
    return render(request, "register.html", {'branches': branches})







def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if user.username == ALLOWED_ADMIN_USERNAME:  # Check if admin
                return redirect('admin_dashboard')
            else:
                return redirect('web2')  # Redirect to user page/dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    # Log out the user
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    response = render(request, 'logout_page.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


@login_required
def some_protected_page(request):
    response = render(request, 'protected_page.html')

    # Prevent back navigation by setting cache control headers
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

