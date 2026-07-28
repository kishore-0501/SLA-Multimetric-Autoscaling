from django.contrib import admin
from .models import UserProfile, Crop, Order
from django.contrib.auth.models import User

# Optional: unregister default User admin if needed
# from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# admin.site.unregister(User)

# ---------------------------
# UserProfile Admin
# ---------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

# ---------------------------
# Custom Admin Dashboard Stats
# ---------------------------
from django.urls import path
from django.shortcuts import render

class CustomAdminSite(admin.AdminSite):
    site_header = "FarmEase Administration"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-stats/', self.admin_view(self.dashboard_stats))
        ]
        return custom_urls + urls

    def dashboard_stats(self, request):
        buyers_count = UserProfile.objects.filter(role='buyer').count()
        sellers_count = UserProfile.objects.filter(role='seller').count()
        return render(request, "admin/dashboard_stats.html", {
            "buyers_count": buyers_count,
            "sellers_count": sellers_count
        })

# Instantiate custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with the custom admin site
custom_admin_site.register(UserProfile)
custom_admin_site.register(Crop)
custom_admin_site.register(Order)
