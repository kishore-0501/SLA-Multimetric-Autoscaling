from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # ---------------------------
    # Admin
    # ---------------------------
    path('admin/', admin.site.urls),

    # ---------------------------
    # General Pages
    # ---------------------------
    path("", views.home, name="home"),
    path("signup/", views.user_signup, name="user_signup"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path("saved-crops/", views.saved_crops, name="saved_crops"),

    # ---------------------------
    # Dashboard & Profile
    # ---------------------------
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("my-orders/", views.my_orders, name="my_orders"),

    # ---------------------------
    # Crop Management (Seller)
    # ---------------------------
    path("crops/add/", views.add_crop, name="add_crop"),
    path("crops/edit/<int:crop_id>/", views.edit_crop, name="edit_crop"),
    path("crops/delete/<int:crop_id>/", views.delete_crop, name="delete_crop"),

    # ---------------------------
    # Orders (Buyer)
    # ---------------------------
    path("place_order/<int:crop_id>/", views.place_order, name="place_order"),
    path("chat/<int:seller_id>/", views.chat_view, name="chat"),
    path("seller/chat/", views.seller_chat_list, name="seller_chat_list"),
    path("seller/chat/<int:buyer_id>/", views.seller_chat_view, name="seller_chat_view"),
    path('faq/', views.faq_page, name='faq'),
    path('about/', views.about_page, name='about'),
]
