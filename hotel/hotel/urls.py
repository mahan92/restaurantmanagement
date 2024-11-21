from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from restaurant import views  # Import your views
from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', views.login_view, name='login'),  # Login view mapped to root
    path('register/', views.register, name='register'),  # Registration page
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout view

    # Admin Dashboard (for admin users)
    path('admin-area/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # General pages
    path('first/', views.fun, name='first'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('web2/', views.web2, name='web2'),
    path('web2/zomato.html', views.zomato, name='zomato'),

    # Hot selling items and order history
    path('hot-selling-items/', views.hot_selling_items, name='hot_selling_items'),
    path('order-history/', views.order_history, name='order_history'),
path('web2/<str:branch_name>/', views.web2, name='web2_with_branch'),  # URL to pass branch name
]

# Serve media files during development (only if settings.DEBUG is True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
